# One-Sixth Forecast v1: How thin materials burn at lunar gravity in Moon-base air

**Registered:** 15 November 2026, before any fire experiment has run on the Moon.
**Authors:** Ayden Tindall, Charles Andrade (NASA Space Apps Challenge 2026, "Flame in Freefall")
**License:** CC0 1.0 (public domain)
**Archive:** Zenodo DOI: *to be added on deposit*

## 1. The question

NASA plans lunar landers, habitats and rovers with **8.2 psia total pressure and 34% oxygen** (control bands allow up to 37%) [1]. NASA screens materials with a 1 g upward-burning test. Microgravity research has shown that 1 g may not be the most flammable condition [1, 2]. No fire experiment has yet run in lunar gravity. The first, Flammability of Materials on the Moon (FM2), is planned for an uncrewed lunar delivery [1].

We forecast how the oxygen limit for flame spread over a thin material changes between Earth and lunar gravity. We then carry that forecast to the habitat atmosphere.

## 2. Scope

- **Material class:** thermally thin cellulose, about 1×10⁻³ g/cm² (tissue or paper class).
- **Mode:** downward (opposed-flow) flame spread in still air, where buoyancy supplies the only flow.
- **Not covered:** upward (concurrent) spread, thick materials, ventilated cabins, ignition. These are listed as next steps in §7.

## 3. Evidence

All rows are in `data/flammability_evidence.csv`, each with a citation and its role in the model.

| Gravity | What was observed | Role |
|---|---|---|
| 0.05–0.1 g | Oxygen limit 13–14% (KC-135 aircraft) [3] | training |
| 0.1 g | Steady burning at 14% O₂ [4] | training |
| 1/6 g | Steady burning at 15% O₂; no survival at 14% O₂ above 0.1 g [4] | training |
| orbit, 5–20 cm/s flow | Flames sustained even at 14% O₂ [5] | prior on the minimum |
| **1 g** | **Limit 15.6% [3]; 16.5% [5]** | **held out for the Earth check** |

We also archive the full BASS-II test table from NASA PSI (129 ISS tests, DOI 10.60555/4qc4-de67) [6] and 21 extinction, ignition and spread observations for thin PMMA films and SIBAL fabric. These are part of the dataset but are not used by this version of the model.

## 4. Model

We use published physics:

1. In still air, buoyancy drives the flow that feeds a downward flame. Its characteristic speed scales as U_b ∝ (g·α·ΔT/T)^(1/3), so ln U_b = ln(g)/3 + constant.
2. Opposed-flow flammability maps for thin fuels in microgravity are U-shaped. Radiative heat loss quenches the flame at low flow, and kinetic blowoff ends it at high flow [2, 4, 5].
3. On the blowoff side, extinction occurs at a critical Damköhler number. Because flame temperature rises roughly linearly with O₂ over a few points, the limit is close to linear in ln U.

The resulting model is:

    LOC(g) = L* + s·max(0, x − x*) + q·max(0, x* − x),   x = ln(g)/3

It has four parameters: the minimum limit L*, where that minimum sits (g*), and the slopes of the blowoff and quench branches. We fit it by rejection sampling (approximate Bayesian computation). We draw 4 million parameter sets from broad priors and keep those consistent with every training observation within ±0.25% O₂.

**Pressure.** To move from 14.7 to 8.2 psia, we use NASA White Sands data for 1 g upward tests: the oxygen limit rises 0.251 to 0.975 percentage points per psia of pressure drop for materials with limits of 25–35% [7]. We apply this as a relative increase, sampled uniformly over that range. **This is the largest extrapolation in the forecast.**

## 5. Earth check (rule fixed before the first run)

> Fit using only reduced-gravity evidence. Predict the 1 g limit. PASS if both measured 1 g values (15.6%, 16.5%) fall inside the 90% predictive interval AND the median is within 1.5 points of their mean.

| | Value |
|---|---|
| Predicted 1 g limit, no Earth data | **15.1% O₂** (90% range 14.0–22.0%) |
| Measured | 15.6% [3], 16.5% [5] |
| Result | **PASS**: both inside; median 1.0 point from their mean |
| Without the ambiguous "no survival at 1/6 g" row | 14.9% (13.5–21.8%), both still inside |

**Caveat.** The interval is wide and the median runs about one point low. The check shows the reduced-gravity data and the physics agree with Earth results. It does not show that the model is precise at 1 g.

## 6. Forecast (model refitted with the 1 g data added)

| Quantity (thin cellulose, downward, still air) | Median | 90% range |
|---|---|---|
| Oxygen limit, lunar gravity (0.165 g), 14.7 psia | **14.4%** | 13.8–14.7% |
| Oxygen limit, Earth gravity, 14.7 psia | 15.9% | 15.4–16.6% |
| **Lunar gravity penalty** (Earth limit minus lunar limit, same pressure) | **1.6 points** | 1.0–2.4 points |
| Probability the lunar limit is below the Earth limit | 1.00 (all accepted draws) | |
| Gravity of maximum flammability, g* | 0.053 g | 0.023–0.47 g |
| Oxygen limit, lunar gravity, **8.2 psia** | **16.4%** | 15.0–17.9% |
| Margin below 34% O₂ habitat air | 17.6 points | 16.1–19.0 points |

### Scorable claims

1. **Gravity penalty.** At the same pressure, the downward oxygen limit of a thin charring fuel at lunar gravity is **1.0–2.4 points lower** than at 1 g. This would be falsified by a lunar or lunar-g centrifuge measurement outside that range for a comparable thin cellulosic fuel.
2. **Direction.** Lunar gravity is more flammable than Earth gravity for downward spread of thin fuels. This would be falsified if the lunar limit is at or above the 1 g limit.
3. **Habitat.** In 34% O₂ at 8.2 psia, thin cellulosic materials will sustain downward spread at lunar gravity with a large margin. Their limit is near 16%, so materials of this class cannot be made safe by atmosphere choice within NASA's planned bands.

### What this means for fire rules

- A 1 g screening result does not carry an automatic margin to the Moon. For thin fuels, the lunar limit sits about 1.6 points lower.
- The headline uncertainty is pressure, not gravity. We recommend that LUCI, FM2 and follow-on lunar experiments include **at least one thin cellulosic sample tested downward at 8.2 psia across 14–20% O₂**. That directly tests the pressure-gravity extrapolation this forecast relies on.

## 7. Limits and next steps

- The 1 g, 0.05–0.1 g and 1/6 g data come from short (~20 s) aircraft parabolas and drop towers. Long-duration lunar data may shift limits.
- Thin cellulose stands in for papers and light fabrics. It does not stand in for Nomex, Kapton or thick PMMA. Takahashi et al. found that high-pyrolysis-temperature materials can behave the opposite way [8].
- Next steps: add upward (concurrent) spread to compare directly with FM2's Synergy Pro fabric (NASA expects a lunar limit of 24–26% at 8.2 psia [1]); fit the BASS-II thin-PMMA and SIBAL extinctions; replace the empirical pressure slope with a Damköhler-based pressure term.

## 8. Reproducibility

```
python3 model/one_sixth_model.py      # numpy 2.x, Python 3.10+; ~2 s; fixed seed 20261115
```

SHA-256 at registration:

```
bb0828583c36c35c40c0ece0c7f5372ff9571d3df8d6d0dcab4ca9a732536555  model/one_sixth_model.py
a9c60daf87dbb2211e236ed7b3ce48d63efd24b8826fd664c5f9bfd5b97dbe22  outputs/results.json
1ae730705517c7ae5acb3984d41c4d3f5bca1264f0ab7fe853d466f89661df85  data/flammability_evidence.csv
db4f5fcc2416fd2150e58c2d73d761090106271a640ecd189297eb7c3cf2951f  data/raw/PSI-25_Experimental_table_BASS-II.csv
```

## References

1. Ferkul, P., "Flammability of Materials on the Moon (FM2)," Lunar and Planetary Science Conference, March 2026. NTRS 20260001966.
2. Olson, S.L., Ferkul, P.V., et al., "Flammability Limits from BASS-II Testing in Microgravity Compared to Normal Gravity Limits," ICES-2019-101.
3. Sacksteder, K.R., T'ien, J.S., "Buoyant downward diffusion flame spread and extinction in partial-gravity accelerations," Proc. Combust. Inst. 25 (1994) 1685–1692.
4. T'ien, J.S., Sacksteder, K.R., Ferkul, P.V., Grayson, G.D., "Combustion of solid fuel in very low speed oxygen streams," NTRS 19930011018.
5. Olson, S.L., NASA/TM-2004-213114, p. 123. NTRS 20040084156.
6. NASA Physical Sciences Informatics, "Burning and Suppression of Solids – II (BASS-II)," PSI-25, v4, DOI 10.60555/4qc4-de67 (CC0).
7. Hirsch, D.B., Juarez, A., Peyton, G.J., Harper, S.A., Olson, S.L., "Selected Parametric Effects on Materials Flammability Limits," NTRS 20110008636.
8. Takahashi, S., et al., Proc. Combust. Inst. 37 (2019) 4257–4265, DOI 10.1016/j.proci.2018.06.102.
