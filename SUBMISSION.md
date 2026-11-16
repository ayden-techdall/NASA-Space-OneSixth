# Space Apps submission text

## Project name
One-Sixth: the first fire forecast for the Moon base

## High-level summary
No fire experiment has run on the Moon, yet NASA plans habitats with oxygen-rich air (34% O₂ at 8.2 psia). One-Sixth gathers NASA's reduced-gravity fire data into one cited dataset and fits two models to it. Each model must predict Earth results it never saw before it is allowed to forecast: one passed, one passed weakly, and one failed and was dropped. A separate AI reviewer then attacked every claim, and we withdrew or weakened what it broke. What survives is a timestamped forecast: at lunar gravity and habitat pressure, thin paper-like material keeps burning down to 13.8–17.9% oxygen, far below the planned 34%. It can be scored when NASA's first lunar fire experiment (FM2) and later tests report.

## Project details
- **What it does:** an open dataset, two models with held-out Earth checks, a registered forecast, an interactive gravity slider, and a published attack round.
- **How it works:** in still air, buoyancy drives the draft that feeds a flame, and its speed scales as g^(1/3). Too little draft starves a flame and too much blows it off. Model 1 fits a two-sided curve in gravity. Model 2 balances radiative loss and reaction time against draft speed, which also gives a physical pressure step. Both are fitted by rejection sampling.
- **What we found:** NASA's 20-second aircraft tests already bracket the lunar limit for thin paper between 14% and 15% oxygen at normal pressure, 1 to 2.4 points below Earth. Our models tie those tests to Earth results and carry them to habitat pressure, where no test exists.
- **Benefits:** it shows where the evidence stops (lunar gravity at low pressure), names the single test that would settle it (thin cellulose, downward, 8.2 psia, 13–19% O₂), and shows that an Earth screening result carries no built-in margin to the Moon for this material class.
- **Honesty:** one of three Earth checks failed and is reported. The reviewer's eight findings and our responses are published with the project.
- **Tools:** Python (NumPy), plain HTML/SVG. Claude (Anthropic) retrieved data, extracted evidence, wrote code and text, and ran the independent review. The team chose the approach and is responsible for the claims.

## NASA data used
- NASA PSI: BASS-II (PSI-25, DOI 10.60555/4qc4-de67), BASS (PSI-26, DOI 10.60555/58h4-dy80), Saffire-I, -II, -III (PSI-98, PSI-99, PSI-100)
- NTRS 20260001966 (FM2), 19930011018, 20040084156, 20150008962, 20110008636, 20080034883, 20240007488 (Saffire-VI)
- Sacksteder & T'ien, Proc. Combust. Inst. 25 (1994) (NASA Glenn partial-gravity aircraft tests)

## Project Demo
The 7-slide deck is the demo. If you prefer a 30-second video, screen-record the slider page with this script:

| Time | Picture | Voice |
|---|---|---|
| 0–5 s | Page title | "No fire experiment has ever run on the Moon. NASA plans a base there with oxygen-rich air." |
| 5–13 s | Earth-check scoreboard | "We fitted two models to NASA's low-gravity fire data, hid the Earth results, and asked for them. One passed. One failed, so we dropped it." |
| 13–22 s | Drag the slider to the Moon, Model 2 | "Then we asked about the Moon base: thin paper keeps burning down to about 15 percent oxygen. The air will be 34." |
| 22–30 s | Attack-round table, then the DOI | "A second AI tried to break it, and we published what it found. The forecast is timestamped, so NASA's first lunar fire test can score it." |
