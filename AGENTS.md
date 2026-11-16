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

## 5. Your task: build the Blender scene

**The scene is yours to build. Nothing has been built yet.** The team wants GPT-6 Astra to design and build the 3D representation. This repo gives you the context and the numbers, not a starting scene.

**Goal.** A 3D picture that lets a hackathon judge grasp the result in ten seconds: thin paper burns far below the oxygen level planned for Moon habitats, and the Moon is a slightly easier place to burn than Earth.

**Your data.** `blender/scene_data.json` holds every number you need, generated from the registered model outputs by `blender/make_scene_data.py`:

- `atmospheres`: Earth air (21% O2) and the planned habitat air (34% O2 at 8.2 psia).
- `headline`: the forecast range at lunar gravity and 8.2 psia (13.8–17.9%, central 15.5%), and the measured Moon bracket at normal pressure.
- `stations`: Orbit, Moon, Mars, Earth, each with gravity, the oxygen limit at 14.7 psia and 8.2 psia with its 90% range, and the natural draft speed.
- `curves`: the oxygen limit against gravity for both models at both pressures. Model 2 is valid only from 0.05 g upward. Model 1 covers the whole range and widens where there is no data.
- `evidence`: the NASA measurements the models were fitted to.
- `earth_checks`: the three Earth checks and their verdicts.
- `wording`: sentences you may use and sentences you must never use.

**What the scene must get right:**

- The forecast (13.8–17.9% O2) belongs to one place only: lunar gravity at habitat pressure. Show the planned 34% habitat air against it, so the gap is obvious.
- Keep measured and forecast visibly different. The Moon limit at normal pressure is a NASA measurement.
- Show uncertainty as ranges, not single sharp values.
- Anything decorative (flame shapes, a habitat, a lunar surface) is illustrative. Say so in the scene or the caption.
- Every label readable at 1920×1080.

**The design is your call.** One idea that maps cleanly onto the data: gravity left to right (Orbit, Moon, Mars, Earth), oxygen as height, one row per pressure, the limit as a ribbon with its range, and the Moon-base forecast as the hero. You may do something different if it tells the story better.

**Deliverables, all under `blender/`:**

- `one_sixth.blend` — the editable scene, with objects named and grouped.
- `build_scene.py` — a Blender Python script that rebuilds the scene from `scene_data.json`, so the numbers are never typed by hand.
- `renders/one_sixth_hero.png` — 1920×1080 still.
- `renders/one_sixth_slider.mp4` — optional, 8–10 s, travelling from orbit to Earth. Useful for the 30-second demo video.
- `NOTES.md` — what you built, and which parts are data and which are illustrative.

**Acceptance checklist:**

- [ ] Every number in the scene comes from `scene_data.json`.
- [ ] The words in section 3 do not appear.
- [ ] "Forecast" is attached only to lunar gravity at 8.2 psia.
- [ ] Decorative elements are labelled illustrative.
- [ ] `build_scene.py` runs headless without errors.
- [ ] No protected file changed (`git status` shows only `blender/`).

## 6. Working rules

- Work on a branch named `blender-scene` and open a pull request. Do not push to `main`.
- Keep commits small and say what changed in plain words.
- Space Apps submissions close at 11:30 PM US Eastern on 15 November 2026. The Blender scene is a bonus. Nothing here should delay the submission itself.
- If something in this file conflicts with what the team tells you directly, the team wins. Ask them when unsure.
