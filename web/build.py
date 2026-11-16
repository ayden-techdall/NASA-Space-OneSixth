"""Embed model outputs into the gravity-slider page."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
t = (root / "web/template.html").read_text()
t = t.replace("__CURVES__", (root / "outputs/curves_v2.json").read_text())
t = t.replace("__RESULTS__", (root / "outputs/results_v2.json").read_text())
rev = root / "outputs/review.json"
t = t.replace("__REVIEW__", rev.read_text() if rev.exists() else "[]")
t = t.replace("__SENS__", (root / "outputs/sensitivity.json").read_text())
(root / "web/index.html").write_text(t)
(root / "docs").mkdir(exist_ok=True)
(root / "docs/index.html").write_text(t)
print("wrote web/index.html and docs/index.html")
