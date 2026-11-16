# AGENTS.md: briefing for AI agents working in this repo

Read this file first. It tells you what the project is, which numbers are safe to use, what you must not claim, and what your task is. It was written on 15 November 2026 for GPT-6 Astra working in Blender, and applies to any agent.

## 1. The project in five lines

- **One-Sixth** is a NASA Space Apps Challenge 2026 entry for the challenge "Flame in Freefall". The team is Ayden Tindall and Charles Andrade.
- NASA plans Moon habitats with oxygen-rich air: 34% O2 at 8.2 psia. No fire experiment has run on the Moon.
- We gathered NASA's reduced-gravity fire data, fitted two models, and made each one predict Earth results it had never seen. One passed, one passed weakly, one failed and was dropped.
- A separate reviewer attacked the claims. We withdrew or weakened what it broke.
- The result is a timestamped forecast for one material (thin paper-like cellulose, flame spreading downward in still air).

Full write-up: `FORECAST.md`. Plain-language summary: `README.md`.

## 2. Numbers you may use

Take numbers from `blender/scene_data.json`. It is generated from the registered model outputs, so do not type numbers by hand. The key ones:

| Quantity | Value | Status |
|---|---|---|
| Planned habitat air | 34% O2 at 8.2 psia (up to 37%) | NASA plan |
| Earth and space-station air | 21% O2 at 14.7 psia | fact |
| Lunar limit for thin paper at 14.7 psia | between 14% and 15% O2 | **measured** by NASA aircraft tests of about 20 s; our models reproduce it (14.2–14.4%) |
| Earth limit for thin paper | 15.6% and 16.5% O2 | measured |
| Moon limit sits below Earth limit by | 1.0–2.4 points | measured, reproduced |
| **Forecast: limit at lunar gravity and 8.2 psia** | **13.8–17.9% O2, most likely near 15.5%** | **the forecast; no test exists here** |
| Natural draft in still air | about 19 cm/s on the Moon, 35 cm/s on Earth | scaling estimate |

"Limit" means the lowest oxygen level at which the material keeps burning. Above it the paper burns; below it the flame goes out.

## 3. What you must not say or show

- Do not say "no fire experiment has run in lunar gravity". Aircraft and drop-tower tests have. Say "no fire experiment has run on the Moon".
- Do not say we predicted the Moon limit at normal pressure. That is NASA's measurement.
- Do not show any Moon number for acrylic (PMMA). That model failed its Earth check.
- Do not use certainty language ("proves", "will", "100%"). Use "forecast" and ranges.
- Do not use NASA logos, mission patches, or the Space Apps logo. Do not imitate official NASA graphics.
- Do not depict injured people or a burning crewed habitat. Show a lab-style test strip, not a disaster.
- Label anything decorative as illustrative. Flame shapes in the scene are illustrative; the columns, ribbons and markers are data.

## 4. Repo map

| Path | What it is | May you edit it? |
|---|---|---|
| `FORECAST.md`, `HASHES.txt` | The registered forecast and file hashes | **No** |
| `data/`, `model/`, `outputs/` | Evidence, models and results (hashed) | **No** |
| `web/`, `docs/` | The gravity-slider page (`docs/index.html` is a copy for GitHub Pages) | Only via `python3 web/build.py` |
| `blender/` | **Your workspace** | Yes |
| `README.md`, `SUBMISSION.md` | Project text | Small additions only |

If you believe a number in a protected file is wrong, do not change it. Open an issue or leave a note in `blender/NOTES.md`.

## 5. Your task: the Blender scene

**Goal.** A 3D picture that lets a hackathon judge grasp the result in ten seconds: thin paper burns far below the oxygen level planned for Moon habitats, and the Moon is a slightly easier place to burn than Earth.

**Starting point.** `blender/build_scene.py` already builds a working scene from `blender/scene_data.json`, and `blender/renders/one_sixth_hero.png` shows the current state. `blender/one_sixth.blend` is the saved file. Improve on these; do not start from nothing.

```bash
python3 blender/make_scene_data.py                                  # refresh the data file
blender --background --python blender/build_scene.py -- --render --save
```

**What the scene encodes (keep this mapping):**

- X axis: gravity on a log scale, with stations Orbit, Moon, Mars, Earth.
- Z axis: oxygen in the air, 0–40%.
- Front row (blue): 14.7 psia. Back row (orange): 8.2 psia, the habitat pressure.
- Ribbons: the oxygen limit with its 90% range. The solid ribbon is model 2 and exists only from 0.05 g upward. The ghost ribbon is model 1.
- Columns: the lit part is where paper burns. Rings mark 21% and 34% air.
- The hero is the Moon-base column on the back row: forecast range 13.8–17.9%, with the 34% ring far above it.
- Markers: NASA measurements (burned, went out, limit range, Earth limit).
- Frames 1–240: a gate travels from orbit to Earth, the 3D version of the page's gravity slider.

**Known weaknesses to fix, in priority order:**

1. Legibility. Labels overlap in places and some text is small. Every label must be readable at 1920×1080.
2. The hero does not stand out enough. Make the Moon-base column and the gap up to the 34% ring the first thing the eye lands on.
3. Flames look like plain blobs. Make them read as flames: round and blue in weak gravity, tall and yellow on Earth. Keep them clearly illustrative.
4. The ground is a flat grey slab. A simple lunar surface and a visible habitat dome behind the Moon station would help, as long as they stay in the background.
5. Camera. Find a three-quarter view where both rows separate cleanly.

**Deliverables, all under `blender/`:**

- `one_sixth.blend` — the editable scene, with objects named and grouped as now.
- `renders/one_sixth_hero.png` — 1920×1080 still.
- `renders/one_sixth_slider.mp4` — optional, 8–10 s, the gate travelling from orbit to Earth. Useful for the 30-second demo video.
- `build_scene.py` — updated so that running it reproduces the scene. Keep it data-driven.
- `NOTES.md` — what you changed, and which parts are data and which are illustrative.

**Acceptance checklist:**

- [ ] Every number in the scene comes from `scene_data.json`.
- [ ] The words in section 3 do not appear.
- [ ] "Forecast" is attached only to the 8.2 psia Moon column.
- [ ] Flames are labelled illustrative.
- [ ] `build_scene.py` runs headless without errors on Blender 4.2 or later.
- [ ] No protected file changed (`git status` shows only `blender/`).

## 6. Working rules

- Work on a branch named `blender-scene` and open a pull request. Do not push to `main`.
- Keep commits small and say what changed in plain words.
- Space Apps submissions close at 11:30 PM US Eastern on 15 November 2026. The Blender scene is a bonus. Nothing here should delay the submission itself.
- If something in this file conflicts with what the team tells you directly, the team wins. Ask them when unsure.
