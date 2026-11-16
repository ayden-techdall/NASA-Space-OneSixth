"""Draw the One-Sixth technical figure in camera-space coordinates."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "scene_data.json").read_text())
W, H = 1920, 1080

BLACK = "#181818"
WHITE = "#ffffff"
GRID = "#e1e1e1"
RULE = "#888888"
BLUE = "#315f82"


def plate():
    shapes = [("rect", "White page", (0, 0, W, H), WHITE)]

    def label(name, x, y, value, size=32, bold=False):
        face = "bold" if bold else "regular"
        shapes.append(("text", name, x, y, value, size, face, BLACK))

    def line(name, x1, y1, x2, y2, color=RULE, width=2):
        shapes.append(("line", name, [(x1, y1), (x2, y2)], color, width))

    headline = DATA["headline"]
    habitat = DATA["atmospheres"]["habitat"]
    normal_pressure = DATA["atmospheres"]["earth_air"]["psia"]
    low, high = headline["habitat_forecast_range"]
    center = headline["habitat_forecast_central"]
    aircraft_low, aircraft_high = headline["moon_limit_14_7_psia_measured_bracket"]
    earth_limits = [row["o2"] for row in DATA["evidence"] if row["kind"] == "earth_limit"]
    date = DATA["meta"]["forecast_version"].split(", registered ")[1]
    tick_step = 5
    maximum = tick_step * math.ceil(habitat["o2_max"] / tick_step)
    plot_left, plot_right = 450, 1790

    def oxygen_x(value):
        return plot_left + value * (plot_right - plot_left) / maximum

    label("Title", 92, 52, "Oxygen limits for thin cellulose tissue", 60, True)
    label("Spread mode", 94, 135, "Downward flame spread in still air", 34)
    line("Title rule", 94, 197, 1826, 197, BLACK)
    label("Conditions", 94, 233, f"Lunar gravity at habitat pressure ({habitat['psia']:g} psia)", 35, True)

    axis_y = 512
    for value in range(0, maximum + 1, tick_step):
        x = oxygen_x(value)
        line("Scale grid", x, 306, x, axis_y, GRID)
        line("Scale tick", x, axis_y, x, axis_y + 10, BLACK)
        digits = str(value)
        label("Scale value", x - len(digits) * 8, axis_y + 20, digits, 28)
    line("Scale baseline", plot_left, axis_y, plot_right, axis_y, BLACK)
    label("Scale units", 946, 577, "Oxygen by volume (%)", 30)

    range_y, air_y = 367, 455
    label("Forecast row", 95, range_y - 13, "Forecast oxygen limit", 31)
    label("Air row", 95, air_y - 13, "Planned habitat air", 31)
    left, right = oxygen_x(low), oxygen_x(high)
    line("Forecast interval", left, range_y, right, range_y, BLUE, 12)
    for edge in (left, right):
        line("Forecast range endpoint", edge, range_y - 14, edge, range_y + 14, BLUE, 4)
    label("Forecast value", right + 24, range_y - 16, f"{low:g}–{high:g}%", 36, True)
    point = oxygen_x(habitat["o2"])
    shapes.append(("dot", "Habitat reference point", point, air_y, 9, BLACK))
    label("Habitat reference value", point + 23, air_y - 16, f"{habitat['o2']:g}%", 36, True)

    label("Measured table title", 94, 654, f"Measured oxygen limits at normal pressure ({normal_pressure:g} psia)", 35, True)
    line("Table top", 94, 711, 1826, 711, BLACK)
    label("Test header", 109, 728, "Test condition", 26, True)
    label("Measurement header", 1050, 728, "Measured oxygen limit (% by volume)", 26, True)
    line("Table header rule", 94, 769, 1826, 769)
    label("Aircraft test", 109, 786, "Lunar gravity, aircraft tests", 30)
    label("Aircraft result", 1050, 786, f"{aircraft_low:g}–{aircraft_high:g} (bracket)", 30)
    label("Earth test", 109, 835, "Earth gravity", 30)
    label("Earth result", 1050, 835, " and ".join(f"{v:g}" for v in earth_limits), 30)
    line("Table bottom", 94, 881, 1826, 881, BLACK)

    label("Caption", 94, 910, "Figure 1.", 27, True)
    label("Caption text", 211, 910,
          f"At habitat pressure, the estimated lower limit for sustained spread is near {center:g}% oxygen.", 27)
    label("Caption continuation", 211, 947,
          "The table gives the measured limits at normal pressure for comparison.", 27)
    label("Sources", 94, 1014, "Sources: NASA NTRS 19930011018, 20260001966, 20040084156.", 23)
    label("Credit", 1255, 1014, f"One-Sixth  |  Ayden Tindall  |  {date}", 21)
    return shapes
