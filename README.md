# One-Sixth: the first fire forecast for the Moon base

NASA Space Apps Challenge 2026, **Flame in Freefall**

No fire experiment has run on the Moon. NASA plans landers, habitats and rovers with oxygen-rich air (34% O₂ at 8.2 psia). One-Sixth gathers NASA's reduced-gravity fire data and fits a published physics model to it. It checks that model against Earth results the model never saw, then forecasts how thin materials will burn at one-sixth gravity in habitat air. The forecast is timestamped so it can be scored when lunar data arrives.

**Headline:** at the same pressure, a thin paper-like material at lunar gravity keeps burning at **1.6 points (1.0–2.4) less oxygen than on Earth**. In habitat air its limit is about 16% O₂, roughly 18 points below the planned 34%.

## What's here

| Path | What it is |
|---|---|
| `web/index.html` | Gravity slider: drag from orbit to Moon to Earth and watch the burn / won't-burn line move. Self-contained; open it in any browser. |
| `FORECAST.md` | The registered forecast: scope, evidence, model, Earth check, numbers, scorable claims, references. |
| `data/flammability_evidence.csv` | 25 curated evidence rows. Each has gravity, pressure, O₂, flow, outcome, citation, and its role in the model (training, held out, dataset only). |
| `data/raw/PSI-25_Experimental_table_BASS-II.csv` | The full BASS-II ISS test table from NASA PSI (129 tests, CC0, DOI 10.60555/4qc4-de67), unmodified. |
| `model/one_sixth_model.py` | The model, the Earth check (pass rule written in the file before the first run), and the forecast. |
| `outputs/results.json`, `outputs/curves.json` | Model output and the curves the slider draws. |
| `web/build.py` | Rebuilds `web/index.html` from the template and the outputs. |

## Run it

```bash
pip install numpy
python3 model/one_sixth_model.py   # ~2 s, fixed seed
python3 web/build.py               # rebuild the page
open web/index.html
```

## How it works

1. **Gather.** We pulled the BASS-II experimental table from NASA's PSI archive. We extracted thin-fuel limits from NASA technical reports on NTRS: aircraft partial-gravity tests, drop-tower and ISS tests.
2. **Extract.** Each observation became one row with conditions, outcome and citation. Ambiguous readings are flagged in the `notes` column and tested in a sensitivity run.
3. **Prove it on Earth first.** We fitted the model only to reduced-gravity data, then predicted the 1 g limit. Result: 15.1% O₂ (90% range 14.0–22.0%), against 15.6% and 16.5% measured. It passes our pre-set rule, but loosely; see `FORECAST.md` §5.
4. **Forecast.** We refitted with the Earth data and ran the model at 0.165 g, then at the habitat's 8.2 psia using NASA White Sands pressure slopes. Uncertainty bands widen where the data runs out.

## Honest limits

- The scope is thin cellulose spreading downward in still air. Thick materials, upward spread and ventilated cabins are next.
- The pressure correction is an extrapolation from 1 g upward-test data.
- Partial-gravity data come from ~20 s aircraft parabolas.

## License

Code and data are released under CC0 1.0 (public domain). The BASS-II table is NASA data released under CC0 by NASA PSI.
