"""
One-Sixth, model 2: a physics-based limit model for thin fuels (v2).

Structure follows the published "simplified model" for opposed-flow flame
spread over thin fuels (Takahashi et al., Proc. Combust. Inst. 35 (2015)
2535-2543; Takahashi & Maruta, Trans. JSASS Aerospace Tech. Japan 16 (2018)
28-34): a flame survives while

        R_rad + 1/Da < 1

  R_rad = radiative loss from the fuel surface / conduction from the flame
        = a / ( p * V * (Tf - Tv) )
  1/Da  = flow time needed / chemical time available
        = b * V^2 * exp(theta / Tf) / ( X * p^n )
  Tf    = T_inf + dT * X / 0.21      (flame temperature rises with oxygen X)

  V  opposed flow speed at the flame (cm/s), p pressure (atm), X O2 mole fraction.
  In still air the flow is buoyant:  V = Vb1 * (g / p)^(1/3),
  with Vb1 = buoyant speed at 1 g, 1 atm (Takahashi: about 35 cm/s).

We could not access the paywalled papers' equations verbatim, so this is our
own implementation of that structure. The scale constants a and b are
calibrated from data rather than taken from the papers; theta = E/R uses the
published activation energy for PMMA (1.5e5 J/mol, Takahashi poster) with
+/-15 %, and a broad range for cellulose. The pressure exponent n is not
known. For an overall reaction order m, 1/Da scales as p^(2-m), so n = m - 2:
n = 0 is second order (Takahashi's rate form) and n = 1 is third order. We
sample n over [0, 1] because that range brackets the pressure trend measured
at NASA White Sands; it is a choice, not a derivation. model/sensitivity.py
reruns the forecast with n in [-1, 0] (orders 1 to 2). n only matters for the
pressure step.

Inference: rejection sampling over broad priors, as in model 1.

EARTH CHECKS (rules fixed in this file before the first run of this model):
  PMMA (thin film): fit ONLY to forced-flow tests in orbit / parabolic flight
    (no 1-g data). Predict the 1-g still-air limit. PASS if the measured value
    (17.0 % O2, Takahashi) is inside the 90 % predictive interval AND
    |median - 17.0| <= 1.5.
  Cellulose: fit ONLY to reduced-gravity evidence (same rows as model 1).
    PASS if both measured 1-g values (15.6, 16.5) are inside the 90 % interval
    AND |median - 16.05| <= 1.5.
A model/material pair that fails does not forecast.

NOTE ON PRESSURE: with n in [0, 1] the model's rise in the 1-g limit from 14.7
to 8.2 psia sits inside the range measured at NASA White Sands for upward
tests (Hirsch et al., NTRS 20110008636). That agreement follows from the
choice of n, so it is not an independent check.
"""
import numpy as np

T_INF = 300.0
TOL = 0.25
G_MOON, G_MARS = 0.165, 0.38
P_HAB = 8.2 / 14.7
VGRID = np.geomspace(0.3, 200.0, 56)
LOGV = np.log(VGRID)
XLO, XHI = 0.06, 0.60

MATERIALS = {
    "pmma": dict(label="Thin PMMA film (0.1-0.2 mm)", Tv=670.0, theta=(15300.0, 20750.0)),
    "cellulose": dict(label="Thin cellulose (tissue/paper class)", Tv=618.0, theta=(12030.0, 19240.0)),
}


def f(X, V, p, a, b, theta, dT, Tv, n):
    tf = T_INF + dT * X / 0.21
    rrad = a / (p * V * np.maximum(tf - Tv, 1.0) / 1000.0)
    inv_da = b * V ** 2 * np.exp(theta / tf) / (X * p ** n)
    return rrad + inv_da - 1.0


def limit_curve(par, Tv, p=1.0):
    """Limiting O2 (%) on VGRID for each draw; 60 where nothing burns below 60 % O2."""
    a, b, theta, dT, n = (par[k][:, None] for k in ("a", "b", "theta", "dT", "n"))
    V = VGRID[None, :]
    lo = np.full((a.shape[0], V.shape[1]), XLO)
    hi = np.full_like(lo, XHI)
    for _ in range(26):
        mid = 0.5 * (lo + hi)
        burn = f(mid, V, p, a, b, theta, dT, Tv, n) < 0
        hi = np.where(burn, mid, hi)
        lo = np.where(burn, lo, mid)
    return 100.0 * hi


def at_v(curve, v):
    """Interpolate each draw's limit curve at its own velocity v (array or scalar)."""
    v = np.broadcast_to(np.asarray(v, dtype=float), (curve.shape[0],))
    lv = np.clip(np.log(v), LOGV[0], LOGV[-1])
    i = np.clip(np.searchsorted(LOGV, lv) - 1, 0, len(LOGV) - 2)
    t = (lv - LOGV[i]) / (LOGV[i + 1] - LOGV[i])
    r = np.arange(curve.shape[0])
    return curve[r, i] * (1 - t) + curve[r, i + 1] * t


def v_buoy(par, g, p=1.0):
    return par["Vb1"] * (g / p) ** (1.0 / 3.0)


def draw_prior(rng, n, mat):
    lo, hi = MATERIALS[mat]["theta"]
    return dict(
        a=np.exp(rng.uniform(np.log(0.05), np.log(50.0), n)),
        b=np.exp(rng.uniform(np.log(1e-11), np.log(1e-6), n)),
        theta=rng.uniform(lo, hi, n),
        dT=rng.uniform(1700.0, 2100.0, n),
        Vb1=rng.uniform(25.0, 45.0, n),
        n=rng.uniform(0.0, 1.0, n),
    )


def training_mask(mat, par, curve, skip=()):
    m = np.ones(curve.shape[0], dtype=bool)
    if mat == "pmma" and "B14" in skip:
        # Post-hoc diagnostic only: drop the BASS-II low-flow rows
        mloc = curve.min(axis=1)
        m &= (mloc >= 14.7 - 0.4) & (mloc <= 14.7 + 0.4)
        m &= at_v(curve, 15.0) <= 17.35 + TOL
        m &= at_v(curve, 55.0) >= 17.35 - TOL
    elif mat == "pmma":
        # Minimum limit in microgravity 14.7 % (Takahashi, 0.125 mm film)
        mloc = curve.min(axis=1)
        m &= (mloc >= 14.7 - 0.4) & (mloc <= 14.7 + 0.4)
        # BASS-II B14 (0.2 mm): burned at 15 % at 3-5 cm/s, went out near 2 cm/s
        m &= at_v(curve, 3.0) <= 15.0 + TOL
        m &= at_v(curve, 5.0) <= 15.0 + TOL
        m &= at_v(curve, 2.0) >= 15.0 - TOL
        # BASS-II B18/B19: blowoff at 17.3-17.4 % when the fan was raised toward
        # maximum; anemometer display saturated, tunnel maximum ~40-55 cm/s.
        m &= at_v(curve, 15.0) <= 17.35 + TOL
        m &= at_v(curve, 55.0) >= 17.35 - TOL
    else:
        # Sacksteder & T'ien 1994: limit 13-14 % at 0.05-0.1 g
        for g in (0.05, 0.075, 0.1):
            v = at_v(curve, v_buoy(par, g))
            m &= (v >= 13.0 - TOL) & (v <= 14.0 + TOL)
        # T'ien et al. 1992: 1/6 g burns at 15 %, not at 14 %
        v6 = at_v(curve, v_buoy(par, 1 / 6))
        m &= (v6 <= 15.0 + TOL) & (v6 > 14.0 - TOL)
        # Olson 2004: in orbit with 5-20 cm/s ventilation, sustained even at 14 %
        band = (VGRID >= 5.0) & (VGRID <= 20.0)
        m &= curve[:, band].min(axis=1) <= 14.0 + TOL
    return m


EARTH = {"pmma": [17.0], "cellulose": [15.6, 16.5]}


def earth_mask(mat, par, curve):
    v1 = at_v(curve, v_buoy(par, 1.0))
    return (v1 >= min(EARTH[mat]) - TOL - (0.15 if mat == "pmma" else 0)) & \
           (v1 <= max(EARTH[mat]) + TOL + (0.15 if mat == "pmma" else 0))


def sub(par, m):
    return {k: v[m] for k, v in par.items()}


def pct(a, ps=(5, 50, 95)):
    return [round(float(np.percentile(a, q)), 3) for q in ps]


def band_vs_g(par, c1, gs, p=1.0):
    out = {"p5": [], "p50": [], "p95": []}
    for g in gs:
        a, b, c = pct(at_v(c1, v_buoy(par, g, p)))
        out["p5"].append(a); out["p50"].append(b); out["p95"].append(c)
    return out


def band_vs_v(curve):
    q = np.percentile(curve, [5, 50, 95], axis=0)
    return {"p5": q[0].round(3).tolist(), "p50": q[1].round(3).tolist(), "p95": q[2].round(3).tolist()}


def run_material(mat, rng, n_draws, gs, chunk=250_000):
    Tv = MATERIALS[mat]["Tv"]
    keep, kept_curves, diag = [], [], []
    for start in range(0, n_draws, chunk):
        par = draw_prior(rng, min(chunk, n_draws - start), mat)
        curve = limit_curve(par, Tv, 1.0)
        m = training_mask(mat, par, curve)
        keep.append(sub(par, m)); kept_curves.append(curve[m])
        if mat == "pmma":
            md = training_mask(mat, par, curve, skip=("B14",))
            diag.append(at_v(curve[md], v_buoy(sub(par, md), 1.0)))
    par = {k: np.concatenate([d[k] for d in keep]) for k in keep[0]}
    curve = np.concatenate(kept_curves)
    res = {"label": MATERIALS[mat]["label"], "prior_draws": n_draws}

    # ---- Earth check (training-only fit) ----
    pred = at_v(curve, v_buoy(par, 1.0))
    p5, p50, p95 = pct(pred)
    targets = EARTH[mat]
    inside = [bool(p5 <= t <= p95) for t in targets]
    err = abs(p50 - float(np.mean(targets)))
    res["earth_check"] = dict(accepted=int(len(pred)), predicted_1g=[p5, p50, p95], measured=targets,
                              inside_90=inside, median_error=round(err, 3),
                              PASSED=bool(all(inside) and err <= 1.5))
    res["training_only_moon_1atm"] = pct(at_v(curve, v_buoy(par, G_MOON)))
    page = {"check_1atm": band_vs_g(par, curve, gs), "u_check_1atm": band_vs_v(curve)}
    if diag:
        d = np.concatenate(diag)
        res["posthoc_diagnostic_without_BASS-II_low_flow_rows"] = dict(
            note="Run after the Earth check failed, to locate the tension. Not a pass.",
            accepted=int(len(d)), predicted_1g=pct(d))
    if not res["earth_check"]["PASSED"]:
        res["forecast"] = None
        return res, page

    # ---- Final fit: add the 1-g data ----
    m = earth_mask(mat, par, curve)
    par, curve = sub(par, m), curve[m]
    curve_h = limit_curve(par, Tv, P_HAB)
    moon1 = at_v(curve, v_buoy(par, G_MOON)); earth1 = at_v(curve, v_buoy(par, 1.0))
    moonh = at_v(curve_h, v_buoy(par, G_MOON, P_HAB)); earthh = at_v(curve_h, v_buoy(par, 1.0, P_HAB))
    vstar = VGRID[curve.argmin(axis=1)]
    res["forecast"] = dict(
        valid=res["earth_check"]["PASSED"], accepted=int(m.sum()),
        LOC_moon_1atm=pct(moon1), LOC_earth_1atm=pct(earth1),
        gravity_penalty=pct(earth1 - moon1), P_moon_below_earth=round(float(np.mean(earth1 > moon1)), 4),
        LOC_moon_hab=pct(moonh), LOC_earth_hab=pct(earthh),
        gravity_penalty_hab=pct(earthh - moonh),
        margin_vs_34=pct(34.0 - moonh),
        pressure_rise_moon_pts=pct(moonh - moon1),
        pressure_rise_1g_relative=pct((earthh - earth1) / earth1),
        min_limit_microgravity=pct(curve.min(axis=1)),
        most_flammable_speed_cm_s=pct(vstar),
        most_flammable_gravity=pct(np.minimum((vstar / par["Vb1"]) ** 3, 5.0)),
        draft_speed_moon_cm_s=pct(v_buoy(par, G_MOON)),
        draft_speed_moon_hab_cm_s=pct(v_buoy(par, G_MOON, P_HAB)),
        draft_speed_earth_cm_s=pct(v_buoy(par, 1.0)),
        limit_at_2_cm_s_1atm=pct(at_v(curve, 2.0)),
        limit_at_0p5_cm_s_1atm=pct(at_v(curve, 0.5)),
    )
    page.update(final_1atm=band_vs_g(par, curve, gs), final_hab=band_vs_g(par, curve_h, gs, P_HAB),
                u_1atm=band_vs_v(curve), u_hab=band_vs_v(curve_h))
    return res, page


def run(n_draws=1_500_000, seed=20261116):
    rng = np.random.default_rng(seed)
    gs = [round(float(v), 5) for v in np.geomspace(0.002, 1.0, 120)]
    results, page = {}, {"g": gs, "v": VGRID.round(4).tolist()}
    for mat, nd in (("pmma", n_draws), ("cellulose", n_draws // 2)):
        results[mat], page[mat] = run_material(mat, rng, nd, gs)
    return results, page
