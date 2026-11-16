"""Sensitivity runs prompted by the independent review (v2). Not part of the registered models."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import one_sixth_model as m1
import physics_model as m2

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}

# (a) Model 1 Earth check under other priors on the blowoff slope s
def m1_check(kind):
    rng = np.random.default_rng(7)
    n = 4_000_000
    Ls = rng.uniform(13.0, 14.5, n)
    xs = np.log(10.0 ** rng.uniform(-3.0, 0.0, n)) / 3.0
    q = rng.uniform(0.0, 20.0, n)
    s = {"uniform_0_20": rng.uniform(0, 20, n), "loguniform_0.1_20": np.exp(rng.uniform(np.log(0.1), np.log(20), n)),
         "uniform_0_40": rng.uniform(0, 40, n)}[kind]
    m = m1.training_mask(Ls, xs, s, q)
    return m1.pct(m1.loc(1.0, Ls[m], xs[m], s[m], q[m]))
out["model1_earth_check_by_prior_on_s"] = {k: m1_check(k) for k in ("uniform_0_20", "loguniform_0.1_20", "uniform_0_40")}
# what simple alternatives predict at 1 g
out["null_models_1g"] = {"no_gravity_effect": 14.5, "note": "midpoint of the 1/6-g bracket carried to 1 g"}

gs = [0.165, 1.0]
def m2_variant(floor=None, n_range=None, seed=11, draws=600_000):
    rng = np.random.default_rng(seed)
    base_mask, base_prior = m2.training_mask, m2.draw_prior
    if floor is not None:
        m2.training_mask = lambda mat, par, curve, skip=(): base_mask(mat, par, curve, skip) & (curve.min(axis=1) >= floor)
    if n_range is not None:
        def dp(r, n, mat):
            p = base_prior(r, n, mat); p["n"] = r.uniform(n_range[0], n_range[1], n); return p
        m2.draw_prior = dp
    try:
        res, _ = m2.run_material("cellulose", rng, draws, gs)
    finally:
        m2.training_mask, m2.draw_prior = base_mask, base_prior
    f = res["forecast"] or {}
    return dict(earth_check=res["earth_check"], LOC_moon_1atm=f.get("LOC_moon_1atm"), gravity_penalty=f.get("gravity_penalty"),
                LOC_moon_hab=f.get("LOC_moon_hab"), pressure_rise_1g_relative=f.get("pressure_rise_1g_relative"),
                min_limit_microgravity=f.get("min_limit_microgravity"))
out["model2_cellulose_with_floor_12.75"] = m2_variant(floor=12.75)
out["model2_cellulose_reaction_order_1_to_2"] = m2_variant(n_range=(-1.0, 0.0))
json.dump(out, open(os.path.join(root, "outputs/sensitivity.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
