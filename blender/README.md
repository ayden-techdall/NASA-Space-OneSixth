# One-Sixth in Blender

This folder holds the visual representation of the result, built by GPT-6 Astra: a research plate (`renders/one_sixth_hero.png`, editable in `one_sixth.blend`) and an interactive exhibit (`one_sixth.html`). `NOTES.md` explains what each mark means and how to rebuild them.

![The lunar burn limit](renders/one_sixth_hero.png)

## What is here

| File | What it is |
|---|---|
| `scene_data.json` | Every number the scene needs, generated from the registered model outputs |
| `make_scene_data.py` | Regenerates `scene_data.json` (`python3 blender/make_scene_data.py`) |

The brief, the numbers that are safe to use and the wording to avoid are in `AGENTS.md` at the repo root, section 5.

## Prompt to start GPT-6 Astra

> Clone https://github.com/ayden-techdall/NASA-Space-OneSixth and read AGENTS.md first. Your task is section 5: design and build a Blender scene that shows the One-Sixth result. Take every number from `blender/scene_data.json` and write a `blender/build_scene.py` that builds the scene from that file. Work on a branch called `blender-scene`, keep all changes inside `blender/`, render a 1920×1080 still to `blender/renders/one_sixth_hero.png`, write `blender/NOTES.md`, and open a pull request. Show me the render before you open it.
