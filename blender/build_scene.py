"""One-Sixth in 3D: build the Blender scene from blender/scene_data.json.

Run headless from the repo root:
    blender --background --python blender/build_scene.py -- --render
or inside Blender: open this file in the Text Editor and press Run Script.

Options after "--":
    --render            render a still to blender/renders/one_sixth_hero.png
    --engine CYCLES     CYCLES (default, works without a GPU) or EEVEE
    --samples 64        Cycles samples
    --res 1920x1080     output resolution
    --save              save blender/one_sixth.blend
    --frame 120         which frame to render (1 = orbit ... 240 = Earth)

What the scene shows (every number comes from scene_data.json):
  X axis  gravity, log scale: Orbit, Moon, Mars, Earth
  Z axis  oxygen in the air (% by volume)
  Y rows  front row = 14.7 psia (blue); back row = 8.2 psia habitat pressure (orange)
  Ribbons the oxygen limit: above a ribbon thin paper burns, below it the flame goes out.
          Solid ribbon = model 2 (shown only where it has data, 0.05 g and up).
          Ghost ribbon = model 1 (whole range; widens where there is no data).
  Columns one per station: the lit part is where paper burns. Rings mark the air people breathe.
  Markers NASA measurements used to fit the models.
  Flames  illustrative only: rounder and bluer in weak gravity, taller and yellower on Earth.
  Slider  a glowing gate that travels from orbit to Earth over frames 1-240.
"""
import json
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.path.join(os.getcwd(), "blender")
DATA = json.load(open(os.path.join(HERE, "scene_data.json")))

# ---------------- options ----------------
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def opt(name, default=None):
    if name in argv:
        i = argv.index(name)
        return argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("--") else True
    return default


# ---------------- layout ----------------
G_MIN, G_MAX = 0.002, 1.0
X_MIN, X_MAX = -9.0, 9.0
Z_PER_PCT = 0.22          # 1 % O2 = 0.22 Blender units
O2_TOP = 40.0
Y_ROW = {"p14_7": 0.0, "p8_2": 3.2}
COL = {
    "blue": (0.10, 0.36, 0.85, 1), "orange": (0.93, 0.36, 0.12, 1), "ink": (0.92, 0.91, 0.88, 1),
    "muted": (0.45, 0.47, 0.52, 1), "regolith": (0.16, 0.16, 0.17, 1), "glass": (0.55, 0.65, 0.80, 1),
    "paper": (0.95, 0.94, 0.90, 1), "red": (0.85, 0.20, 0.18, 1),
}


def gx(g):
    g = max(G_MIN, min(G_MAX, g))
    return X_MIN + (math.log10(g) - math.log10(G_MIN)) / (math.log10(G_MAX) - math.log10(G_MIN)) * (X_MAX - X_MIN)


def oz(o2):
    return o2 * Z_PER_PCT


# ---------------- helpers ----------------
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, color, emission=0.0, alpha=1.0, rough=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = rough
    if emission:
        for key in ("Emission Color", "Emission"):
            if key in b.inputs:
                b.inputs[key].default_value = color
                break
        if "Emission Strength" in b.inputs:
            b.inputs["Emission Strength"].default_value = emission
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
            try:
                setattr(m, attr, val)
            except Exception:
                pass
    m.diffuse_color = (color[0], color[1], color[2], alpha)
    return m


def link(obj, coll):
    coll.objects.link(obj)
    return obj


def mesh_obj(name, verts, faces, mat, coll):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    return link(ob, coll)


def box(name, center, size, mat, coll, rot=(0, 0, 0)):
    sx, sy, sz = (s / 2 for s in size)
    v = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz), (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
    f = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    ob = mesh_obj(name, v, f, mat, coll)
    ob.location = center
    ob.rotation_euler = rot
    return ob


def cylinder(name, base, top_z, radius, mat, coll, seg=32):
    x, y, z0 = base
    v, f = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        v.append((x + radius * math.cos(a), y + radius * math.sin(a), z0))
        v.append((x + radius * math.cos(a), y + radius * math.sin(a), top_z))
    for i in range(seg):
        j = (i + 1) % seg
        f.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    f.append(tuple(2 * i for i in range(seg))[::-1])
    f.append(tuple(2 * i + 1 for i in range(seg)))
    return mesh_obj(name, v, f, mat, coll)


def ring(name, center, radius, tube, mat, coll, seg=40, tseg=10):
    cx, cy, cz = center
    v, f = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(tseg):
            b = 2 * math.pi * j / tseg
            r = radius + tube * math.cos(b)
            v.append((cx + r * math.cos(a), cy + r * math.sin(a), cz + tube * math.sin(b)))
    for i in range(seg):
        for j in range(tseg):
            a, b = i * tseg + j, i * tseg + (j + 1) % tseg
            c, d = ((i + 1) % seg) * tseg + (j + 1) % tseg, ((i + 1) % seg) * tseg + j
            f.append((a, b, c, d))
    return mesh_obj(name, v, f, mat, coll)


def blob(name, center, scale, mat, coll, seg=24, rings=14, taper=0.0):
    """UV sphere; taper > 0 pulls the top into a teardrop (a flame shape)."""
    cx, cy, cz = center
    v, f = [], []
    for i in range(rings + 1):
        phi = math.pi * i / rings
        zz = -math.cos(phi)                      # -1 bottom .. +1 top
        rr = math.sin(phi) * (1.0 - taper * max(0.0, zz)) ** 1.5
        for j in range(seg):
            a = 2 * math.pi * j / seg
            v.append((cx + scale[0] * rr * math.cos(a), cy + scale[1] * rr * math.sin(a), cz + scale[2] * (zz + 1)))
    for i in range(rings):
        for j in range(seg):
            a, b = i * seg + j, i * seg + (j + 1) % seg
            f.append((a, b, b + seg, a + seg))
    ob = mesh_obj(name, v, f, mat, coll)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def text(name, body, loc, size, mat, coll, align="CENTER", rot=(math.pi / 2, 0, 0), extrude=0.01):
    cu = bpy.data.curves.new(name, type="FONT")
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.extrude = extrude
    ob = bpy.data.objects.new(name, cu)
    ob.location = loc
    ob.rotation_euler = rot
    ob.data.materials.append(mat)
    return link(ob, coll)


def ribbon(name, g_arr, lo, hi, y, mat, coll, thick=0.06):
    """A band in the X-Z plane between lo and hi (O2 %), with a little thickness in Y."""
    v, f = [], []
    for g, a, b in zip(g_arr, lo, hi):
        x = gx(g)
        v += [(x, y - thick, oz(a)), (x, y - thick, oz(b)), (x, y + thick, oz(a)), (x, y + thick, oz(b))]
    n = len(g_arr)
    for i in range(n - 1):
        a, b = 4 * i, 4 * (i + 1)
        f += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a + 1, b + 1, b + 3, a + 3), (a, a + 2, b + 2, b)]
    f += [(0, 1, 3, 2), (4 * (n - 1), 4 * (n - 1) + 2, 4 * (n - 1) + 3, 4 * (n - 1) + 1)]
    return mesh_obj(name, v, f, mat, coll)


def tube_line(name, pts, radius, mat, coll):
    cu = bpy.data.curves.new(name, type="CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, co in zip(sp.points, pts):
        p.co = (co[0], co[1], co[2], 1)
    cu.bevel_depth = radius
    cu.bevel_resolution = 3
    ob = bpy.data.objects.new(name, cu)
    ob.data.materials.append(mat)
    return link(ob, coll)


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


# ---------------- build ----------------
def build():
    reset()
    scene = bpy.context.scene
    scene.name = "One-Sixth"
    M = {
        "blue": material("limit_14_7_psia", COL["blue"], emission=0.7),
        "blue_ghost": material("model1_14_7_psia", COL["blue"], emission=0.2, alpha=0.12),
        "orange": material("limit_8_2_psia", COL["orange"], emission=0.7),
        "orange_ghost": material("model1_8_2_psia", COL["orange"], emission=0.2, alpha=0.12),
        "burn": material("burns_zone", COL["orange"], emission=0.45, alpha=0.28),
        "noburn": material("wont_burn_zone", COL["glass"], alpha=0.30, rough=0.2),
        "ink": material("label", COL["ink"], emission=0.75),
        "muted": material("label_muted", COL["muted"], emission=0.6),
        "ground": material("regolith", COL["regolith"], rough=0.95),
        "paper": material("paper", COL["paper"], rough=0.8),
        "ring_air": material("air_ring", COL["ink"], emission=1.2),
        "went_out": material("went_out", COL["red"], emission=1.5),
        "dome": material("habitat_dome", COL["glass"], alpha=0.16, rough=0.1),
        "gate": material("gravity_slider", COL["ink"], emission=0.3, alpha=0.05),
    }
    c_env, c_rib, c_sta = collection("Environment"), collection("Limit ribbons"), collection("Stations")
    c_evi, c_lab, c_anim = collection("NASA evidence"), collection("Labels"), collection("Gravity slider")

    # ground
    box("Regolith", (0, 2.0, -0.05), (30, 16, 0.1), M["ground"], c_env)

    # ribbons: model 1 ghost over the whole range, model 2 solid where it has data
    for row, solid, ghost in (("p14_7", "blue", "blue_ghost"), ("p8_2", "orange", "orange_ghost")):
        y = Y_ROW[row]
        c1 = DATA["curves"]["model_1"][row]
        ribbon(f"Model1_band_{row}", c1["g"], c1["p5"], [min(v, O2_TOP) for v in c1["p95"]], y, M[ghost], c_rib)
        c2 = DATA["curves"]["model_2"][row]
        ribbon(f"Model2_band_{row}", c2["g"], c2["p5"], c2["p95"], y, M[solid], c_rib, thick=0.05)
        tube_line(f"Model2_median_{row}", [(gx(g), y - 0.07, oz(v)) for g, v in zip(c2["g"], c2["p50"])], 0.035, M["ink"], c_rib)

    # air reference lines
    hab, air = DATA["atmospheres"]["habitat"], DATA["atmospheres"]["earth_air"]
    tube_line("Habitat_air_34pct", [(X_MIN - 0.5, Y_ROW["p8_2"], oz(hab["o2"])), (X_MAX + 0.8, Y_ROW["p8_2"], oz(hab["o2"]))], 0.03, M["orange"], c_env)
    tube_line("Earth_air_21pct", [(X_MIN - 0.5, Y_ROW["p14_7"], oz(air["o2"])), (X_MAX + 0.8, Y_ROW["p14_7"], oz(air["o2"]))], 0.03, M["blue"], c_env)
    text("Label_habitat_air", hab["label"], (X_MIN - 0.4, Y_ROW["p8_2"], oz(hab["o2"]) + 0.18), 0.42, M["ink"], c_lab, align="LEFT")
    text("Label_earth_air", air["label"], (X_MIN - 0.4, Y_ROW["p14_7"] - 0.1, oz(air["o2"]) + 0.18), 0.42, M["ink"], c_lab, align="LEFT")

    # oxygen axis
    for pct in (10, 20, 30, 40):
        text(f"Tick_{pct}", f"{pct}%", (X_MIN - 1.0, Y_ROW["p14_7"], oz(pct) - 0.12), 0.38, M["muted"], c_lab, align="RIGHT")
        box(f"Tickline_{pct}", (X_MIN - 0.7, Y_ROW["p14_7"], oz(pct)), (0.35, 0.03, 0.03), M["muted"], c_env)
    text("Axis_o2", "oxygen in the air", (X_MIN - 1.9, Y_ROW["p14_7"], oz(25)), 0.38, M["muted"], c_lab, rot=(math.pi / 2, -math.pi / 2, 0))
    text("Axis_g", "weaker gravity   <   >   stronger gravity", (-3.2, -1.7, 0.2), 0.36, M["muted"], c_lab)

    # stations
    for s in DATA["stations"]:
        x, g = gx(s["g"]), s["g"]
        y0 = Y_ROW["p14_7"]
        lim = s.get("limit_14_7_psia", {}).get("p50") or s["limit_with_fans"]["o2"]
        cylinder(f"{s['label']}_wont_burn", (x, y0, 0), oz(lim), 0.28, M["noburn"], c_sta)
        cylinder(f"{s['label']}_burns", (x, y0, oz(lim)), oz(O2_TOP), 0.28, M["burn"], c_sta)
        ring(f"{s['label']}_limit_ring", (x, y0, oz(lim)), 0.36, 0.035, M["blue"], c_sta)
        ring(f"{s['label']}_earth_air_ring", (x, y0, oz(air["o2"])), 0.36, 0.025, M["ring_air"], c_sta)
        text(f"Name_{s['label']}", s["label"], (x, -1.7, 0.42), 0.62, M["ink"], c_lab)
        sub = "burns only while fans run" if s["id"] == "orbit" else f"{g:g} g"
        text(f"Sub_{s['label']}", sub, (x, -1.7, 0.05), 0.27, M["muted"], c_lab)
        lim_txt = f"{lim:.1f}%" if s["id"] != "orbit" else "14% with fans"
        text(f"Limit_{s['label']}", lim_txt, (x + 0.45, y0 - 0.3, oz(lim) - 0.45), 0.36, M["ink"], c_lab, align="LEFT")
        # illustrative flame on a paper strip
        draft = s.get("draft_cm_s") or 0.0
        k = (draft / 36.0) if draft else 0.0                      # 0 orbit .. ~1 Earth
        col = (0.25 + 0.75 * k, 0.45 + 0.35 * k, 1.0 - 0.85 * k, 1)
        fm = material(f"flame_{s['label']}", col, emission=2.2)
        box(f"{s['label']}_paper", (x, -0.75, 0.55), (0.32, 0.02, 1.1), M["paper"], c_sta)
        blob(f"{s['label']}_flame_illustrative", (x, -0.80, 0.95), (0.20, 0.12, 0.16 + 0.42 * k), fm, c_sta, taper=0.75 * k)

    # the hero: Moon base column on the habitat-pressure row
    moon = next(s for s in DATA["stations"] if s["id"] == "moon")
    xm, yh = gx(moon["g"]), Y_ROW["p8_2"]
    lo, hi = DATA["headline"]["habitat_forecast_range"]
    mid = DATA["headline"]["habitat_forecast_central"]
    cylinder("MoonBase_wont_burn", (xm, yh, 0), oz(lo), 0.34, M["noburn"], c_sta)
    cylinder("MoonBase_forecast_range", (xm, yh, oz(lo)), oz(hi), 0.34, M["orange"], c_sta)
    cylinder("MoonBase_burns", (xm, yh, oz(hi)), oz(O2_TOP), 0.34, M["burn"], c_sta)
    ring("MoonBase_habitat_air_ring", (xm, yh, oz(hab["o2"])), 0.46, 0.05, M["ring_air"], c_sta)
    text("Label_forecast", f"Forecast: burns down to {lo}-{hi}% O2", (xm - 0.7, yh, oz(27.5)), 0.46, M["ink"], c_lab, align="RIGHT")
    text("Label_forecast_sub", "lunar gravity + habitat pressure: no test exists here", (xm - 0.7, yh, oz(25.3)), 0.32, M["muted"], c_lab, align="RIGHT")
    tube_line("Forecast_leader", [(xm - 0.6, yh, oz(25.0)), (xm - 0.36, yh, oz(hi))], 0.02, M["ink"], c_lab)
    blob("Habitat_dome", (xm, yh + 3.4, -1.3), (2.3, 2.3, 1.3), M["dome"], c_env, seg=40, rings=20)

    # NASA evidence on the 14.7 psia row
    y_e = Y_ROW["p14_7"] - 0.12
    for i, e in enumerate(DATA["evidence"]):
        if e["kind"] == "limit_range":
            x0, x1 = gx(e["g"][0]), gx(e["g"][1])
            z0, z1 = oz(e["o2"][0]), oz(e["o2"][1])
            for a, b in (((x0, z0), (x1, z0)), ((x1, z0), (x1, z1)), ((x1, z1), (x0, z1)), ((x0, z1), (x0, z0))):
                tube_line(f"Evidence_{i}_range", [(a[0], y_e, a[1]), (b[0], y_e, b[1])], 0.025, M["ink"], c_evi)
        elif e["kind"] == "burned":
            blob(f"Evidence_{i}_burned", (gx(e["g"]), y_e, oz(e["o2"]) - 0.11), (0.11, 0.11, 0.11), M["ring_air"], c_evi)
        elif e["kind"] == "went_out":
            for r in (math.pi / 4, -math.pi / 4):
                box(f"Evidence_{i}_went_out", (gx(e["g"]), y_e, oz(e["o2"])), (0.34, 0.05, 0.05), M["went_out"], c_evi, rot=(0, r, 0))
        else:
            box(f"Evidence_{i}_earth_limit", (gx(e["g"]) + 0.42, y_e, oz(e["o2"])), (0.2, 0.06, 0.2), M["ring_air"], c_evi, rot=(0, math.pi / 4, 0))

    # title and legend
    text("Title", "ONE-SIXTH", (X_MIN - 0.4, 7.5, 9.2), 1.3, M["ink"], c_lab, align="LEFT", extrude=0.03)
    text("Subtitle", "Where thin paper stops burning, from orbit to the Moon to Earth", (X_MIN - 0.4, 7.5, 8.3), 0.44, M["muted"], c_lab, align="LEFT")
    text("Legend_blue", "blue: limit at 14.7 psia", (X_MAX + 0.8, 7.5, 9.6), 0.42, M["blue"], c_lab, align="RIGHT")
    text("Legend_orange", "orange: limit at 8.2 psia (habitat)", (X_MAX + 0.8, 7.5, 8.95), 0.42, M["orange"], c_lab, align="RIGHT")
    text("Legend_zone", "lit column = paper burns; flames are illustrative", (X_MAX + 0.8, 7.5, 7.55), 0.36, M["muted"], c_lab, align="RIGHT")

    # gravity slider: a gate travelling from orbit to Earth, frames 1-240
    scene.frame_start, scene.frame_end = 1, 240
    gate = box("Gravity_slider_gate", (X_MIN, 1.6, oz(O2_TOP) / 2), (0.05, 5.4, oz(O2_TOP)), M["gate"], c_anim)
    gate.location.x = X_MIN
    gate.keyframe_insert("location", frame=1)
    gate.location.x = X_MAX
    gate.keyframe_insert("location", frame=240)

    # camera and lights
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 30
    cam = link(bpy.data.objects.new("Camera", cam_data), c_env)
    cam.location = (2.2, -22.0, 9.0)
    target = link(bpy.data.objects.new("Camera_target", None), c_env)
    target.location = (0.3, 2.0, 4.5)
    con = cam.constraints.new("TRACK_TO")
    con.target, con.track_axis, con.up_axis = target, "TRACK_NEGATIVE_Z", "UP_Y"
    scene.camera = cam
    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 2.0
    sun = link(bpy.data.objects.new("Sun", sun_data), c_env)
    sun.rotation_euler = (math.radians(55), 0, math.radians(35))
    fill = bpy.data.lights.new("Fill", "AREA")
    fill.energy, fill.size = 900, 12
    fl = link(bpy.data.objects.new("Fill", fill), c_env)
    fl.location = (0, -10, 12)
    fl.rotation_euler = (math.radians(40), 0, 0)

    world = bpy.data.worlds.new("Space")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.006, 0.008, 0.014, 1)
    scene.world = world
    return scene


def configure_render(scene):
    engine = str(opt("--engine", "CYCLES")).upper()
    if engine == "EEVEE":
        for name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                scene.render.engine = name
                break
            except Exception:
                continue
    else:
        scene.render.engine = "CYCLES"
        scene.cycles.samples = int(opt("--samples", 64))
        scene.cycles.use_denoising = False
    w, h = (int(v) for v in str(opt("--res", "1920x1080")).split("x"))
    scene.render.resolution_x, scene.render.resolution_y = w, h
    scene.render.image_settings.file_format = "PNG"


if __name__ == "__main__":
    scene = build()
    configure_render(scene)
    scene.frame_set(int(opt("--frame", 1)))
    if opt("--save"):
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "one_sixth.blend"))
    if opt("--render"):
        scene.render.filepath = os.path.join(HERE, "renders", "one_sixth_hero.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", scene.render.filepath)
