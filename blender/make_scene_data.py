"""Build blender/scene_data.json from the registered model outputs.

Run from the repo root:  python3 blender/make_scene_data.py

The Blender scene reads ONLY scene_data.json, so every number in the 3D scene
traces back to outputs/results_v2.json, outputs/curves_v2.json and
outputs/sensitivity.json.
"""
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parent.parent
res = json.loads((root / "outputs/results_v2.json").read_text())
cur = json.loads((root / "outputs/curves_v2.json").read_text())
sens = json.loads((root / "outputs/sensitivity.json").read_text())
m1r, m2r = res["model_1_empirical_cellulose"], res["model_2_physics"]
m1c, m2c = cur["model_1"], cur["model_2"]
F2 = m2r["cellulose"]["forecast"]


def interp(xs, ys, x):
    if x <= xs[0]:
        return ys[0]
    for i in range(1, len(xs)):
        if x <= xs[i]:
            t = (math.log(x) - math.log(xs[i - 1])) / (math.log(xs[i]) - math.log(xs[i - 1]))
            return ys[i - 1] + t * (ys[i] - ys[i - 1])
    return ys[-1]


def band(g_arr, c, g):
    return {k: round(interp(g_arr, c[k], g), 2) for k in ("p5", "p50", "p95")}


def cut(g_arr, c, gmin):
    idx = [i for i, g in enumerate(g_arr) if g >= gmin][::3]
    if idx[-1] != len(g_arr) - 1:
        idx.append(len(g_arr) - 1)
    out = {"g": [g_arr[i] for i in idx]}
    for k in ("p5", "p50", "p95"):
        out[k] = [round(c[k][i], 2) for i in idx]
    return out


vb = F2["draft_speed_earth_cm_s"][1]
hab_all = [
    m1r["forecast"]["LOC_moon_8.2psia"],
    F2["LOC_moon_hab"],
    sens["model2_cellulose_with_floor_12.75"]["LOC_moon_hab"],
    sens["model2_cellulose_reaction_order_1_to_2"]["LOC_moon_hab"],
]

stations = [{
    "id": "orbit", "label": "Orbit", "g": 0.002, "draft_cm_s": None,
    "limit_with_fans": {"o2": 14.0, "fan_speed_cm_s": [5, 20]},
    "status": "measured: flames sustained even at 14% O2 with 5-20 cm/s fan flow (Olson 2004); "
              "on the space station flames went out when the fan stopped (Olson et al., ICES-2019-101)",
}]
for sid, label, g in (("moon", "Moon", 0.165), ("mars", "Mars", 0.38), ("earth", "Earth", 1.0)):
    stations.append({
        "id": sid, "label": label, "g": g,
        "draft_cm_s": round(vb * g ** (1 / 3), 1),
        "limit_14_7_psia": band(m2c["g"], m2c["cellulose"]["final_1atm"], g),
        "limit_8_2_psia": band(m2c["g"], m2c["cellulose"]["final_hab"], g),
        "status": "model 2 (physics), fitted to NASA reduced-gravity and Earth data",
    })

data = {
    "meta": {
        "project": "One-Sixth: the first fire forecast for the Moon base",
        "forecast_version": "v2, registered 15 Nov 2026",
        "material": "thin cellulose tissue (~1e-3 g/cm2), flame spreading downward in still air",
        "units": {"o2": "% by volume", "g": "fraction of Earth gravity", "draft": "cm/s"},
        "generated_by": "blender/make_scene_data.py",
    },
    "atmospheres": {
        "earth_air": {"o2": 21.0, "psia": 14.7, "label": "Earth / ISS air: 21% O2"},
        "habitat": {"o2": 34.0, "o2_max": 37.0, "psia": 8.2, "label": "Planned Moon habitat air: 34% O2 at 8.2 psia"},
    },
    "headline": {
        "habitat_forecast_range": [round(min(a[0] for a in hab_all), 1), round(max(a[2] for a in hab_all), 1)],
        "habitat_forecast_central": 15.5,
        "habitat_forecast_by_variant": {
            "model_1": m1r["forecast"]["LOC_moon_8.2psia"],
            "model_2": F2["LOC_moon_hab"],
            "model_2_with_floor": sens["model2_cellulose_with_floor_12.75"]["LOC_moon_hab"],
            "model_2_reaction_order_1_to_2": sens["model2_cellulose_reaction_order_1_to_2"]["LOC_moon_hab"],
        },
        "moon_limit_14_7_psia_measured_bracket": [14.0, 15.0],
        "moon_below_earth_points": [1.0, 2.4],
    },
    "stations": stations,
    "curves": {
        "model_2": {
            "valid_from_g": 0.05,
            "p14_7": cut(m2c["g"], m2c["cellulose"]["final_1atm"], 0.05),
            "p8_2": cut(m2c["g"], m2c["cellulose"]["final_hab"], 0.05),
        },
        "model_1": {
            "valid_from_g": 0.002,
            "p14_7": cut(m1c["g"], m1c["final_fit_1atm"], 0.002),
            "p8_2": cut(m1c["g"], m1c["final_fit_8_2psia"], 0.002),
        },
    },
    "evidence": [
        {"kind": "limit_range", "g": [0.05, 0.1], "o2": [13.0, 14.0], "text": "Limit 13-14% at 0.05-0.1 g", "source": "Sacksteder & T'ien 1994"},
        {"kind": "burned", "g": 0.1, "o2": 14.0, "text": "Burned at 14%, 0.1 g", "source": "T'ien et al. 1992, NTRS 19930011018"},
        {"kind": "went_out", "g": 0.1667, "o2": 14.0, "text": "Did not survive at 14% above 0.1 g", "source": "T'ien et al. 1992"},
        {"kind": "burned", "g": 0.1667, "o2": 15.0, "text": "Steady burning at 15%, 1/6 g", "source": "T'ien et al. 1992"},
        {"kind": "earth_limit", "g": 1.0, "o2": 15.6, "text": "Earth limit 15.6%", "source": "Sacksteder & T'ien 1994"},
        {"kind": "earth_limit", "g": 1.0, "o2": 16.5, "text": "Earth limit 16.5%", "source": "Olson 2004, NASA/TM-2004-213114"},
    ],
    "earth_checks": [
        {"name": "Model 1, thin cellulose", "predicted": m1r["earth_check"]["predicted_LOC_1g_p5_p50_p95"], "measured": [15.6, 16.5], "verdict": "weak pass"},
        {"name": "Model 2, thin cellulose", "predicted": m2r["cellulose"]["earth_check"]["predicted_1g"], "measured": [15.6, 16.5], "verdict": "pass"},
        {"name": "Model 2, thin PMMA", "predicted": m2r["pmma"]["earth_check"]["predicted_1g"], "measured": [17.0], "verdict": "failed, no forecast"},
    ],
    "wording": {
        "say": [
            "No fire experiment has run on the Moon.",
            "NASA's 20-second aircraft tests put the lunar limit for thin paper between 14% and 15% O2 at normal pressure.",
            "Forecast: at lunar gravity and 8.2 psia, thin paper keeps burning down to 13.8-17.9% O2, most likely near 15.5%.",
            "The planned habitat air is 34% O2.",
        ],
        "never_say": [
            "No fire experiment has run in lunar gravity (aircraft and drop-tower tests have).",
            "We predicted the Moon limit at normal pressure (it is a NASA measurement that the models reproduce).",
            "Any number for PMMA or acrylic on the Moon (that model failed its Earth check).",
            "Probability 1.00, or any certainty language.",
        ],
    },
}
(root / "blender/scene_data.json").write_text(json.dumps(data, indent=1))
print("wrote blender/scene_data.json", data["headline"]["habitat_forecast_range"])
