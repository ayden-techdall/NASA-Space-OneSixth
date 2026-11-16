"""
One-Sixth: gravity-scaled flammability-limit model for thin fuels, with a
held-out Earth check and a forecast for the lunar habitat atmosphere.

Physics (published framework, not invented here):
  * In a quiescent room, buoyancy supplies the opposed flow that feeds a
    downward-spreading flame. The characteristic buoyant velocity scales as
    U_b ~ (g * alpha * dT/T)^(1/3), so ln(U_b) = ln(g)/3 + const.
    (Olson/T'ien/Sacksteder framework; Takahashi et al. "equivalent velocity".)
  * Microgravity flammability maps are U-shaped in (flow velocity, O2):
    a radiative QUENCH branch at low flow and a kinetic BLOWOFF branch at high
    flow (Olson 1991; T'ien et al. 1992; Olson & Ferkul).
  * On the blowoff branch, extinction occurs at a critical Damkohler number,
    Da ~ (alpha/U^2) * B * exp(-E/RT_f). Because flame temperature rises roughly
    linearly with O2 over a few points of O2, the limiting O2 is close to linear
    in ln(U). We therefore model:

        LOC(g) = L* + s * max(0, x - x*) + q * max(0, x* - x),   x = ln(g)/3

    L*  minimum limiting O2 (bottom of the U)
    x*  where the minimum sits (g* = exp(3 x*))
    s   blowoff-branch slope, q  quench-branch slope   [% O2 per unit ln U]

Inference: approximate Bayesian computation by rejection. Draw parameters from
broad priors; keep draws consistent with every training observation (interval
constraints with a +/-0.25 % O2 reading tolerance).

EARTH CHECK (pre-registered in this file before the first run):
  Fit using ONLY reduced-gravity evidence (0 g, 0.05-0.1 g, 1/6 g).
  Predict LOC at 1 g. PASS if BOTH measured 1-g values (15.6 %, 16.5 %) fall
  inside the 90 % predictive interval AND |median - 16.05| <= 1.5 % O2.
  Only if it passes do we use the model to forecast.
"""
import json
import numpy as np

RNG = np.random.default_rng(20261115)
N_DRAWS = 4_000_000
TOL = 0.25  # % O2 reading tolerance

G_MOON = 0.165
P_HAB_PSIA = 8.2
P_ATM_PSIA = 14.7
HAB_O2 = (34.0, 37.0)

EARTH_PASS_HALF_WIDTH = 1.5
EARTH_TARGETS = {"Sacksteder & T'ien 1994": 15.6, "Olson 2004 (NASA TM)": 16.5}


def loc(g, Ls, xs, s, q):
    """Limiting O2 (%) at gravity g (fraction of Earth), vectorized over draws."""
    x = np.log(g) / 3.0
    return Ls + s * np.maximum(0.0, x - xs) + q * np.maximum(0.0, xs - x)


def draw_prior(n):
    Ls = RNG.uniform(13.0, 14.5, n)              # Olson 2004: 0-g minimum "about 14%"
    log10_gstar = RNG.uniform(-3.0, 0.0, n)      # where the minimum sits, 0.001 g .. 1 g
    xs = np.log(10.0 ** log10_gstar) / 3.0
    s = RNG.uniform(0.0, 20.0, n)                # blowoff slope
    q = RNG.uniform(0.0, 20.0, n)                # quench slope
    return Ls, xs, s, q


def training_mask(Ls, xs, s, q, use_T93b=True):
    """Reduced-gravity constraints only (no 1-g data)."""
    m = np.ones_like(Ls, dtype=bool)
    # Sacksteder & T'ien 1994: LOC 13-14 % at 0.05-0.1 g
    for g in (0.05, 0.075, 0.1):
        v = loc(g, Ls, xs, s, q)
        m &= (v >= 13.0 - TOL) & (v <= 14.0 + TOL)
    # T'ien et al. 1992: propagation at 14 % at 0.1 g  -> LOC(0.1) <= 14
    m &= loc(0.1, Ls, xs, s, q) <= 14.0 + TOL
    # T'ien et al. 1992: steady at 15 % at 1/6 g -> LOC(1/6) <= 15
    v6 = loc(1 / 6, Ls, xs, s, q)
    m &= v6 <= 15.0 + TOL
    # T'ien et al. 1992: no survival at 14 % at g above 0.1 -> LOC(1/6) > 14
    if use_T93b:
        m &= v6 > 14.0 - TOL
    return m


def final_mask(Ls, xs, s, q, use_T93b=True):
    """Training constraints plus the 1-g observations (used only after the Earth check)."""
    m = training_mask(Ls, xs, s, q, use_T93b)
    v1 = loc(1.0, Ls, xs, s, q)
    m &= (v1 >= 15.6 - TOL) & (v1 <= 16.5 + TOL)
    return m


def pct(a, ps=(5, 50, 95)):
    return [float(np.percentile(a, p)) for p in ps]


def pressure_factor(n):
    """Relative LOC increase per psia drop, from NASA WSTF Test-1 data
    (Hirsch et al., NTRS 20110008636): slopes 0.251-0.975 %O2/psia for
    materials with MOC 25-35 %. Converted to a relative rate so it can be
    applied to a material with LOC ~15 %. Flagged as an extrapolation."""
    lo, hi = 0.251 / 35.0, 0.975 / 25.0
    r = RNG.uniform(lo, hi, n)
    return 1.0 + r * (P_ATM_PSIA - P_HAB_PSIA)


def curves(params, gs):
    Ls, xs, s, q = params
    out = {"p5": [], "p50": [], "p95": []}
    for g in gs:
        v = loc(g, Ls, xs, s, q)
        a, b, c = pct(v)
        out["p5"].append(round(a, 3)); out["p50"].append(round(b, 3)); out["p95"].append(round(c, 3))
    return out


def run():
    Ls, xs, s, q = draw_prior(N_DRAWS)
    results = {"n_prior_draws": N_DRAWS}

    # ---------------- Earth check ----------------
    m_tr = training_mask(Ls, xs, s, q, use_T93b=True)
    P_tr = (Ls[m_tr], xs[m_tr], s[m_tr], q[m_tr])
    pred1 = loc(1.0, *P_tr)
    p5, p50, p95 = pct(pred1)
    inside = {k: bool(p5 <= v <= p95) for k, v in EARTH_TARGETS.items()}
    err = abs(p50 - np.mean(list(EARTH_TARGETS.values())))
    passed = all(inside.values()) and err <= EARTH_PASS_HALF_WIDTH
    results["earth_check"] = {
        "accepted_draws": int(m_tr.sum()),
        "predicted_LOC_1g_p5_p50_p95": [p5, p50, p95],
        "measured": EARTH_TARGETS,
        "inside_90pct_interval": inside,
        "median_error_vs_mean_measured": err,
        "pass_rule": "both measured values inside 90% PI and |median-16.05| <= 1.5",
        "PASSED": bool(passed),
    }

    # Sensitivity: drop the ambiguous T93-b constraint
    m_tr_b = training_mask(Ls, xs, s, q, use_T93b=False)
    pb = pct(loc(1.0, Ls[m_tr_b], xs[m_tr_b], s[m_tr_b], q[m_tr_b]))
    results["earth_check_without_T93b"] = {
        "accepted_draws": int(m_tr_b.sum()),
        "predicted_LOC_1g_p5_p50_p95": pb,
        "inside_90pct_interval": {k: bool(pb[0] <= v <= pb[2]) for k, v in EARTH_TARGETS.items()},
    }

    # Training-only prediction at lunar g (for comparison with the final model)
    results["training_only_LOC_moon_1atm"] = pct(loc(G_MOON, *P_tr))

    # ---------------- Forecast (only if Earth check passed) ----------------
    m_f = final_mask(Ls, xs, s, q, use_T93b=True)
    P_f = (Ls[m_f], xs[m_f], s[m_f], q[m_f])
    n = int(m_f.sum())
    moon_1atm = loc(G_MOON, *P_f)
    earth_1atm = loc(1.0, *P_f)
    penalty = earth_1atm - moon_1atm
    pf = pressure_factor(n)
    moon_hab = moon_1atm * pf
    earth_hab = earth_1atm * pf
    gmin = np.exp(3 * P_f[1])

    results["forecast"] = {
        "valid": bool(passed),
        "accepted_draws": n,
        "material_and_mode": "thermally thin cellulose (~1e-3 g/cm2, tissue/paper class), downward (opposed) spread, quiescent air",
        "LOC_moon_1atm": pct(moon_1atm),
        "LOC_earth_1atm": pct(earth_1atm),
        "gravity_penalty_pts_(LOC1g-LOCmoon)": pct(penalty),
        "P(LOC_moon < LOC_earth)": float(np.mean(penalty > 0)),
        "most_flammable_gravity_g_star": pct(gmin),
        "LOC_moon_8.2psia": pct(moon_hab),
        "LOC_earth_8.2psia_(for_comparison)": pct(earth_hab),
        "margin_vs_34pct_O2_pts": pct(HAB_O2[0] - moon_hab),
        "margin_vs_37pct_O2_pts": pct(HAB_O2[1] - moon_hab),
        "P(burns_in_34pct_8.2psia_at_lunar_g)": float(np.mean(moon_hab < HAB_O2[0])),
    }
    m_f_b = final_mask(Ls, xs, s, q, use_T93b=False)
    results["forecast_without_T93b"] = {
        "LOC_moon_1atm": pct(loc(G_MOON, Ls[m_f_b], xs[m_f_b], s[m_f_b], q[m_f_b])),
        "gravity_penalty_pts": pct(loc(1.0, Ls[m_f_b], xs[m_f_b], s[m_f_b], q[m_f_b])
                                   - loc(G_MOON, Ls[m_f_b], xs[m_f_b], s[m_f_b], q[m_f_b])),
    }

    # ---------------- curves for the gravity-slider page ----------------
    gs = [round(float(v), 5) for v in np.geomspace(0.002, 1.0, 120)]
    pf_curve = pressure_factor(len(P_f[0]))
    hab = {"p5": [], "p50": [], "p95": []}
    for g in gs:
        v = loc(g, *P_f) * pf_curve
        a, b, c = pct(v)
        hab["p5"].append(round(a, 3)); hab["p50"].append(round(b, 3)); hab["p95"].append(round(c, 3))
    page = {
        "g": gs,
        "earth_check_fit_1atm": curves(P_tr, gs),
        "final_fit_1atm": curves(P_f, gs),
        "final_fit_8_2psia": hab,
    }
    return results, page


if __name__ == "__main__":
    import os
    res, page = run()
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/results.json", "w") as f:
        json.dump(res, f, indent=2)
    with open("outputs/curves.json", "w") as f:
        json.dump(page, f)
    print(json.dumps(res, indent=2))
