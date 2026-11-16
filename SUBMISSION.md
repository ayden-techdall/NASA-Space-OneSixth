# Space Apps submission text

## Project name
One-Sixth: the first fire forecast for the Moon base

## High-level summary (short)
No fire experiment has run on the Moon, yet NASA plans habitats with oxygen-rich air (34% O₂ at 8.2 psia). One-Sixth gathers NASA's reduced-gravity fire data into one cited dataset. It fits a published physics model and checks it against Earth results the model never saw. It then forecasts how thin materials burn at one-sixth gravity. Result: on the Moon, thin paper-like materials keep burning at about 1.6 points less oxygen than on Earth at the same pressure. In habitat air their limit is about 16% O₂, far below the planned 34%. The forecast is timestamped and archived so it can be scored when NASA's first lunar fire experiment (FM2) reports.

## Project details
- **What it does:** a dataset, a validated model, a registered forecast and an interactive gravity slider.
- **How it works:** buoyant flow scales as g^(1/3). In orbit, flammability maps are U-shaped (quench at low flow, blowoff at high flow). We fit a four-parameter limit curve to aircraft and orbital data by rejection sampling, test it on held-out 1 g data, then forecast.
- **Benefits:** shows exactly where evidence stops (high oxygen, low pressure, lunar gravity), which tells LUCI and FM2 what to test first. It also shows that a 1 g screening result carries no automatic margin to the Moon.
- **Tools:** Python (NumPy), plain HTML/SVG. AI assistance (Claude) helped with literature retrieval, data extraction, code and the write-up. The team chose the model and the pass rule, and checked the extracted rows against their sources.

## NASA data used
- NASA PSI, BASS-II (PSI-25), DOI 10.60555/4qc4-de67
- NTRS 20260001966 (FM2, Ferkul 2026), 19930011018 (T'ien et al.), 20040084156 (Olson 2004), 20150008962 (BASS/BASS-II SIBAL), 20110008636 (Hirsch et al.)
- Sacksteder & T'ien, Proc. Combust. Inst. 25 (1994) (NASA Glenn partial-gravity aircraft tests)

## 30-second video script
| Time | Picture | Voice |
|---|---|---|
| 0–5 s | Lunar surface, then a habitat render | "No fire experiment has ever run on the Moon." |
| 5–10 s | Text: 34% O₂, 8.2 psia | "NASA plans a base there with oxygen-rich air." |
| 10–18 s | Slider in Earth check view, the band landing on the hidden Earth points | "We fitted a model to NASA's low-gravity fire data, hid the Earth results, and asked it to predict them. It did." |
| 18–26 s | Drag the slider to the Moon; readout shows 14.4% and 1.6 points | "Then we asked it about the Moon. Thin materials burn at 1.6 points less oxygen than on Earth." |
| 26–30 s | Zenodo DOI and timestamp | "The forecast is timestamped. When NASA's first lunar fire test lands, it gets scored." |
