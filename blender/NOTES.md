# The lunar burn limit

Open **one_sixth.html** in a browser for the interactive exhibit. It works offline, including its illustration, data and controls. The source references open online. The presentation still is **renders/one_sixth_hero.png** (1920 × 1080).

## What the visitor can do

- Compare the registered habitat-pressure envelope with the planned oxygen fraction on a linear scale. Enter a hypothetical limit to score a future matched experiment. Both endpoints belong to the registered interval.
- Inspect the two edges of the normal-pressure aircraft bracket separately. Section 3.1 and Figure 7 of the flight paper document steady spread at 15% O₂. The team interprets the paper’s description of the 14% runs at higher accelerations as applying to lunar gravity. A short parabola can end before extinction.
- Compare a prediction with the Earth measurements hidden from its fit. Revealing the observations shows a weak empirical-cellulose pass, a physics-cellulose pass and an acrylic failure. The held-out test checks transfer to Earth. Transfer to lunar gravity at habitat pressure remains untested for this material and spread mode.

## What the marks mean

On the habitat panel the rust segment spans the rounded envelope of the model and sensitivity intervals. The light point marks the registered central estimate. The dark reference point in the still and the green reference point in the interactive are the planned atmosphere. The model-specific intervals are 90% intervals. The envelope itself has no assigned coverage probability. All concentrations are oxygen percentages by volume. The drawable Moon is original procedural artwork with invented relief. Its light direction, crater distribution and apparent size are illustrative.

Values come from the repository’s scene_data.json. Its source outputs and the forecast can be inspected at commit 96fa82ede00242230b767c24d234e47e3c2b2913. Sources include [the flight paper, §3.1 and Fig. 7](https://ntrs.nasa.gov/api/citations/19930011018/downloads/19930011018.pdf) and [NASA’s lunar flammability presentation](https://ntrs.nasa.gov/citations/20260001966).

## Rebuild

The offline HTML contains its own presentation code. After regenerating the registered scene data, run the following to refresh its embedded snapshot, illustration and still. The relief and portable proof require NumPy and Pillow. Typefaces follow the installed Georgia, Arial and Courier New families on macOS, with DejaVu fallbacks on Linux.

```sh
python3 blender/lunar_relief.py
python3 blender/refresh_exhibit.py
python3 blender/proof.py
```

The Blender builder uses the same layout and original artwork. It creates an orthographic camera, a textured spherical Moon, editable type, and named meshes for the chart and reference marks.

```sh
blender --background --python-exit-code 1 --python blender/build_scene.py -- --save --render
```

This command writes blender/one_sixth.blend and the Blender render. The committed PNG was rendered with the portable proof renderer. Blender was unavailable on the authoring host, so a native project and a headless render verification are pending.

## Verification

The registered model code and sensitivity script were rerun with their fixed seeds in an isolated directory. Each source script matched its registered SHA-256. The regenerated curves matched their registered hash. Field comparisons of results and sensitivity outputs found five last-place floating-point differences, with maximum absolute difference 3.56 × 10⁻¹⁵. All displayed values and verdicts reproduced. This checks reproducibility using the original evidence.

The 1920 × 1080 proof was visually inspected. JavaScript checks exercised all three tabs, keyboard selection, the three model reveals, disclosure controls and boundary scoring. The environment blocked the in-app browser from opening a local HTML file, so those checks do not include a browser screenshot.

## Blender verification (added 15 Nov 2026, after the plate was built)

The builder was run headless on Blender 5.3 with `--save --render`. It completed without errors. `one_sixth.blend` is now committed, with its typefaces and the relief image packed inside so it opens the same on any computer. The file was generated on Linux, so its type is set in the DejaVu families. Rebuilding on macOS uses Georgia, Arial and Courier New instead. The committed PNG is still the portable proof render.
