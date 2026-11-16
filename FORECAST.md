# One-Sixth Forecast v2: How thin materials burn at lunar gravity in Moon-base air

**Registered:** 15 November 2026, before any fire experiment has run on the Moon.
**Author:** Ayden Tindall (NASA Space Apps Challenge 2026, "Flame in Freefall")
**License:** CC0 1.0 (public domain)
**Archive:** Zenodo DOI: *to be added on deposit*

v2 replaces v1 from earlier the same day. It adds a second model, a second material, an independent review, and weaker wording where the review showed v1 overclaimed. §8 lists every change.

## 1. The question

NASA plans lunar landers, habitats and rovers with **8.2 psia total pressure and 34% oxygen** (control bands allow up to 37%) [1]. NASA screens materials with an upward-burning test at Earth gravity. Microgravity research has shown that Earth gravity may not be the most flammable condition [1, 2].

No fire experiment has run on the Moon. The first, Flammability of Materials on the Moon (FM2), is planned for an uncrewed lunar delivery [1]. Lunar gravity itself has been reached before, but only briefly: aircraft parabolas of about 20 seconds [3, 4] and drop-tower centrifuge tests [1].

We ask two things. Do NASA's short reduced-gravity tests agree with Earth results under a simple physical model? And what does that model say about the combination nobody has tested: lunar gravity at habitat pressure?

## 2. Scope

- **Material:** thin cellulose tissue, about 1×10⁻³ g/cm² (Kimwipe class).
- **Mode:** downward (opposed-flow) flame spread in still air, where buoyancy supplies the only draft.
- **Not covered:** upward spread, thick materials, ventilated cabins, ignition. Thin acrylic (PMMA) was attempted and failed its Earth check (§5), so no PMMA forecast is made.

## 3. Evidence

`data/flammability_evidence.csv` holds 41 rows, each with a citation and its role. `data/raw/` holds NASA's test tables for BASS-II (129 tests), BASS (122), and Saffire I, II and III, as served by NASA PSI [6].

| Gravity | What was observed | Role |
|---|---|---|
| 0.05–0.1 g | Oxygen limit 13–14% (KC-135 aircraft) [3] | training |
| 0.1 g | Flame propagated at 14% O₂ [4] | training |
| 1/6 g | Steady burning at 15% O₂; flames at 14% O₂ did not survive ignition above 0.1 g [4] | training |
| orbit, 5–20 cm/s flow | Flames sustained even at 14% O₂ [5] | training |
| **1 g** | **Limit 15.6% [3]; 16.5% [5]** | **held out for the Earth check** |

Two things in the wider dataset matter for context:

- **Orbit has already seen near-habitat air.** Saffire-VI burned cotton-fiberglass fabric at 54.1 kPa and 31.0% O₂, and thick PMMA at about 55 kPa and 29–30% O₂ [9]. What is untested is lunar gravity in that air.
- **Earth is not always the safer case.** In Saffire-II, three silicone samples did not burn in orbit but burned, fully or in part, in Earth-gravity tests [6]. The direction of the gravity effect depends on the material.

## 4. Models

**Model 1 (simple curve).** In still air the buoyant draft scales as g^(1/3). The oxygen limit is a two-sided line in x = ln(g)/3:

    LOC(g) = L* + s·max(0, x − x*) + q·max(0, x* − x)

The step from 14.7 to 8.2 psia uses NASA White Sands slopes for upward tests (0.251–0.975 points of O₂ per psia [7]), applied as a relative increase.

**Model 2 (physics).** A flame survives while R_rad + 1/Da < 1, the structure of the simplified model of Takahashi and co-workers [8]:

    R_rad = a / (p·V·(Tf − Tv))          radiative loss against conduction from the flame
    1/Da  = b·V²·exp(θ/Tf) / (X·pⁿ)      chemical time against flow time
    Tf    = T∞ + ΔT·X/0.21               flame temperature rises with oxygen
    V     = Vb1·(g/p)^(1/3)              buoyant draft in still air

We could not read the paywalled equations, so this is our own implementation of that structure. The scale constants a and b are calibrated from data. The pressure exponent n is a choice: we sample 0–1 (overall reaction order 2–3) because that range brackets the measured White Sands pressure trend, and we rerun with −1 to 0 (order 1–2) as a sensitivity case.

Both models are fitted by rejection sampling: draw parameters from broad ranges, and keep only the sets consistent with every training observation within ±0.25% O₂.

## 5. Earth checks (rules fixed in the code before each model's first run)

> Fit with all Earth-gravity data hidden. Predict the Earth limit. PASS if every measured value falls inside the 90% predictive interval AND the median is within 1.5 points of the measured mean. A model that fails does not forecast.

| Model, material | Predicted Earth limit | Measured | Result |
|---|---|---|---|
| Model 1, cellulose | 15.1% (14.0–22.0) | 15.6, 16.5 | **Weak pass** |
| Model 2, cellulose | 16.2% (15.4–17.2) | 15.6, 16.5 | **Pass** |
| Model 2, thin PMMA | 20.5% (19.1–22.0) | 17.0 | **Fail: no forecast** |

- **Model 1's pass is weak and depends on a modelling choice.** Its interval is 8 points wide. With a log-uniform prior on the blow-off slope it predicts 14.3% (13.9–16.1) and fails. The independent review found this and we confirmed it (`model/sensitivity.py`).
- **Model 2 passes on cellulose** and still passes in both variants we ran: with a floor on the starved side, 15.8% (15.0–16.6); with reaction order 1–2, 16.2% (15.4–17.2).
- **Model 2 fails on thin PMMA.** Its training data are fan-driven tests on the space station, and this simple model did not carry them over to Earth's buoyant flow. A diagnostic run after the failure, without the low-speed BASS-II rows, predicts 18.0% (15.8–21.2). That locates the tension, and it is not a pass. Likely causes are the low-speed flow readings, mixed film thicknesses (0.1–0.2 mm), and the missing boundary-layer correction that the literature applies [8].
- **What the check rules out.** "Gravity makes no difference" would predict about 14.5% on Earth and fails. The check does not distinguish one curve shape from another.

## 6. Results

| Thin cellulose tissue, downward, still air | Model 1 | Model 2 |
|---|---|---|
| Limit at lunar gravity, 14.7 psia | 14.4% (13.8–14.7) | 14.2% (13.8–14.6) |
| Limit at Earth gravity, 14.7 psia | 15.9% (15.4–16.6) | 16.1% (15.5–16.7) |
| Lunar limit below Earth limit by | 1.6 points (1.0–2.4) | 1.9 points (1.5–2.3) |
| Limit at lunar gravity, 8.2 psia | 16.4% (15.0–17.9) | 15.4% (14.7–16.1) |
| Same, Model 2 with a starved-side floor | | 15.7% (15.1–16.4) |
| Same, Model 2 with reaction order 1–2 | | 14.5% (13.8–15.1) |

Median, with the 90% range in brackets.

**The first three rows are measurements restated, not predictions.** NASA's aircraft tests already bracket the lunar limit at 14.7 psia between 14% and 15% [4], and the fits are constrained to that bracket and to the Earth values. The two models share this evidence, so their agreement is not independent confirmation.

### Scorable forecasts

1. **Habitat air.** For thin cellulose tissue spreading downward in still air at lunar gravity and 8.2 psia, the oxygen limit lies between **13.8% and 17.9%**, most likely near 15.5%. No test exists at this combination. The range covers both models and every variant above. A measurement outside it falsifies the forecast.
2. **A long burn on the Moon.** The 20-second aircraft result will hold for a steady flame: at 14.7 psia the lunar limit for this material lies between 13.8% and 14.7%, below its Earth limit. A long lunar or lunar-gravity test that finds the limit at or above the Earth limit falsifies this.
3. **Sanity check, not discovery.** In 34% O₂ at 8.2 psia this material burns with a wide margin. Paper with an Earth limit near 16% was always going to.

### What this means for fire rules

- For thin cellulosic materials, an Earth screening result carries no built-in margin to the Moon. The lunar limit sits 1 to 2.4 points lower in the data we have.
- NASA has flagged that stopping ventilation, which puts flames out on the space station [2], may not work in partial gravity. Scaling Earth's buoyant draft of roughly 35 cm/s [8] by g^(1/3) puts the natural draft at lunar gravity near 19 cm/s, inside the 5–20 cm/s range where these flames survive in orbit [5].
- The biggest open number is pressure, not gravity. We recommend that lunar experiments include **one thin cellulosic sample burned downward at 8.2 psia across 13–19% O₂**. It tests forecast 1 directly.

## 7. Risks and limits

- **Short tests may bias low-gravity limits low.** A flame that has not yet died when a 20-second parabola ends counts as burning. That would overstate the lunar penalty. Forecast 2 is exposed to this.
- **The two Earth values come from different sources.** 15.6% is from the same apparatus as the partial-gravity data [3]. 16.5% is quoted for opposed flow without the fuel or apparatus stated [5].
- **Pressure is an extrapolation in both models.** Model 1 borrows upward-test slopes. Model 2 depends on an assumed reaction order.
- **Model 2 has no cellulose data below about 10 cm/s.** It cannot place the starved side of the curve, and we do not report it there.
- **One material class.** High-pyrolysis-temperature materials can behave the opposite way [8], and Saffire-II's silicone did.

## 8. Changes from v1

- Added Model 2, the PMMA attempt, the BASS and Saffire tables, and 16 evidence rows.
- Corrected two dataset rows (BII-B18, BII-B19). v1 read "10 blowoff" as 10 cm/s; the air-speed display tops out at 10, so the true speed was higher.
- Withdrew "no fire experiment has run in lunar gravity". Aircraft and drop-tower tests have.
- Withdrew "probability 1.00 that the lunar limit is below the Earth limit". It was built into the constraints.
- Reclassified the lunar limit at 14.7 psia and the gravity penalty from forecasts to restated measurements.
- Downgraded Model 1's Earth check to a weak pass.
- Widened the habitat forecast from 15.0–17.9% to 13.8–17.9%.
- Narrowed the material from "thin charring fuel" to thin cellulose tissue.

## 9. The attack round

A separate reviewer model, in a fresh context with no view of how the work was built, was asked to break each claim. It found no bug that changes a number. Its eight findings and our responses are in `outputs/review.json`, and the changes in §8 follow from them. We reran its two main numerical checks ourselves (`model/sensitivity.py`, `outputs/sensitivity.json`).

## 10. Reproducibility

```
python3 model/run_all.py        # both models; about 2.5 minutes; fixed seeds
python3 model/sensitivity.py    # review-prompted variants; about 2 minutes
python3 web/build.py            # rebuild the page
```

SHA-256 at registration: see `HASHES.txt`.

## References

1. Ferkul, P., "Flammability of Materials on the Moon (FM2)," Lunar and Planetary Science Conference, March 2026. NTRS 20260001966.
2. Olson, S.L., Ferkul, P.V., et al., "Flammability Limits from BASS-II Testing in Microgravity Compared to Normal Gravity Limits," ICES-2019-101.
3. Sacksteder, K.R., T'ien, J.S., "Buoyant downward diffusion flame spread and extinction in partial-gravity accelerations," Proc. Combust. Inst. 25 (1994) 1685–1692.
4. T'ien, J.S., Sacksteder, K.R., Ferkul, P.V., Grayson, G.D., "Combustion of solid fuel in very low speed oxygen streams," NTRS 19930011018.
5. Olson, S.L., NASA/TM-2004-213114, p. 123. NTRS 20040084156.
6. NASA Physical Sciences Informatics: BASS-II (PSI-25, DOI 10.60555/4qc4-de67), BASS (PSI-26, DOI 10.60555/58h4-dy80), Saffire-I (PSI-98), Saffire-II (PSI-99), Saffire-III (PSI-100). CC0.
7. Hirsch, D.B., Juarez, A., Peyton, G.J., Harper, S.A., Olson, S.L., "Selected Parametric Effects on Materials Flammability Limits," NTRS 20110008636.
8. Takahashi, S., Ebisawa, T., Bhattacharjee, S., Ihara, T., "Simplified model for predicting difference between flammability limits of a thin material in normal gravity and microgravity environments," Proc. Combust. Inst. 35 (2015) 2535–2543; Takahashi, S., Maruta, K., Trans. JSASS Aerospace Tech. Japan 16 (2018) 28–34; Takahashi, Tsuboi & Maruta, FLARE poster, Gifu University (PMMA values).
9. "Preliminary Results from the Saffire VI Experiment," ICES 2024. NTRS 20240007488.
10. Olson, S.L., et al., "Microgravity Flame Spread in Exploration Atmospheres," NTRS 20080034883.
