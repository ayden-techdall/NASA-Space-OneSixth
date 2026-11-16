"""Camera-space marks for the One-Sixth oxygen-limit figure."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "scene_data.json").read_text())
W, H = 1920, 1080

INK = "#171717"
WHITE = "#ffffff"
GRID = "#dedede"
BOUND = "#777777"
BLUE = "#315f82"


def plate():
    shapes = [("rect", "Page", (0, 0, W, H), WHITE)]

    def label(name, x, y, text, size=26, bold=False):
        shapes.append(("text", name, x, y, text, size, "bold" if bold else "regular", INK))

    def line(name, x0, y0, x1, y1, color=INK, width=2):
        shapes.append(("line", name, [(x0, y0), (x1, y1)], color, width))

    def dot(name, x, y, radius, color):
        shapes.append(("dot", name, x, y, radius, color))

    headline = DATA["headline"]
    habitat = DATA["atmospheres"]["habitat"]
    pressure = DATA["atmospheres"]["earth_air"]["psia"]
    low, high = headline["habitat_forecast_range"]
    central = headline["habitat_forecast_central"]
    aircraft = headline["moon_limit_14_7_psia_measured_bracket"]
    earth = [row["o2"] for row in DATA["evidence"] if row["kind"] == "earth_limit"]
    version, date = DATA["meta"]["forecast_version"].split(", registered ")
    stations = DATA["stations"]

    label("Title", 80, 46, "Oxygen limits for flame spread in thin cellulose tissue", 54, True)
    label("Scope", 82, 123, "Downward flame spread in still air", 31)
    line("Title rule", 82, 185, 1838, 185)

    label("Habitat panel", 82, 218, f"Lunar gravity at habitat pressure ({habitat['psia']:g} psia)", 31, True)
    label("Gravity panel", 1000, 218, f"Oxygen limit versus gravity at {pressure:g} psia", 31, True)

    # Left panel. The concentration of the atmosphere and the limiting interval
    # refer to the same pressure and use the same linear oxygen scale.
    oxygen_max = 10 * math.ceil(habitat["o2_max"] / 10)
    left, right = 112, 868
    def oxygen_x(value):
        return left + (right - left) * value / oxygen_max

    axis = 505
    for value in range(0, oxygen_max + 1, 5):
        x = oxygen_x(value)
        line("Scale grid", x, 329, x, axis, GRID)
        line("Scale tick", x, axis, x, axis + 8)
        label("Scale value", x - len(str(value)) * 6.7, axis + 17, str(value), 24)
    line("Scale axis", left, axis, right, axis)
    label("Scale units", 344, 563, "Oxygen by volume (%)", 27)
    a, b = oxygen_x(low), oxygen_x(high)
    label("Forecast interval label", a - 110, 295, f"Forecast limit: {low:g}–{high:g}%", 28, True)
    line("Forecast interval", a, 359, b, 359, BLUE, 10)
    for x in (a, b):
        line("Forecast endpoint", x, 345, x, 373, BLUE, 4)
    dot("Central estimate", oxygen_x(central), 359, 3.7, WHITE)
    planned_x = oxygen_x(habitat["o2"])
    dot("Habitat reference", planned_x, 449, 8, INK)
    label("Habitat reference label", planned_x - 216, 394, f"Planned habitat air: {habitat['o2']:g}%", 28, True)

    # Right panel. Use the empirical curve throughout its own domain, including
    # its finite near-orbit grid point. Do not extend the physics fit to orbit.
    curve = DATA["curves"]["model_1"]["p14_7"]
    gravity = curve["g"]
    gravity_min, gravity_max = gravity[0], gravity[-1]
    y_step = 5
    y_min = y_step * math.floor(min(curve["p5"]) / y_step)
    y_max = y_step * math.ceil(max(curve["p95"]) / y_step)
    gx0, gx1, gy0, gy1 = 1060, 1792, 334, 505

    def gx(g):
        return gx0 + (gx1 - gx0) * math.log(g / gravity_min) / math.log(gravity_max / gravity_min)

    def gy(o2):
        return gy1 - (gy1 - gy0) * (o2 - y_min) / (y_max - y_min)

    label("Gravity units", 1000, 279, "Oxygen by volume (%)", 23)
    for value in range(y_min, y_max + 1, y_step):
        y = gy(value)
        label("Oxygen tick label", gx0 - 39, y - 9, str(value), 21)
        line("Oxygen grid", gx0, y, gx1, y, GRID)
    line("Gravity left axis", gx0, gy0, gx0, gy1)
    line("Gravity bottom axis", gx0, gy1, gx1, gy1)

    for station in stations:
        x = gx(station["g"])
        line("Gravity tick", x, gy1, x, gy1 + 8)
        label("Station", x - len(station["label"]) * 5.6, gy1 + 17, station["label"], 22)
        value = f"{station['g']:g}"
        label("Station gravity", x - len(value) * 5.6, gy1 + 45, value, 20)
    label("Gravity axis title", 1195, 589, "Gravity relative to Earth (log scale)", 25)

    for field, name, color, width in (("p5", "Lower bound", BOUND, 2),
                                      ("p95", "Upper bound", BOUND, 2),
                                      ("p50", "Median", INK, 4)):
        points = [(gx(g), gy(v)) for g, v in zip(gravity, curve[field])]
        shapes.append(("line", name, points, color, width))
    line("Median key", 1342, 291, 1378, 291, INK, 4)
    label("Median key label", 1389, 279, "Median", 23)
    line("Interval key", 1495, 291, 1531, 291, BOUND, 2)
    label("Interval key label", 1543, 279, "90% model bounds", 23)

    label("Table title", 82, 660, f"Measured oxygen limits at {pressure:g} psia", 31, True)
    line("Table top", 82, 704, 1838, 704)
    label("Test header", 98, 717, "Test condition", 24, True)
    label("Measurement header", 959, 717, "Measured oxygen limit (% by volume)", 24, True)
    line("Table header rule", 82, 755, 1838, 755, BOUND)
    label("Aircraft test", 98, 770, "Lunar gravity, aircraft tests", 27)
    label("Aircraft value", 959, 770, f"{aircraft[0]:g}–{aircraft[1]:g} (bracket)", 27)
    label("Earth test", 98, 816, "Earth gravity", 27)
    label("Earth value", 959, 816, " and ".join(f"{v:g}" for v in earth), 27)
    line("Table bottom", 82, 860, 1838, 860)

    label("Caption label", 82, 888, "Figure 1.", 25, True)
    label("Caption first sentence", 195, 888,
          f"At habitat pressure, the central estimate for sustained spread is near {central:g}% oxygen.", 25)
    label("Caption second sentence", 195, 922,
          f"At normal pressure, the empirical model has its widest interval near orbit ({gravity_min:g} g on the model grid).", 25)
    label("Source", 82, 983, f"Source: One-Sixth forecast {version}, NASA PSI and NTRS data", 23)
    label("Report identifiers", 82, 1017, "NTRS 19930011018, 20260001966, 20040084156", 21)
    label("Team", 1295, 1017, f"Ayden Tindall and Charles Andrade  |  {date}", 21)
    return shapes
