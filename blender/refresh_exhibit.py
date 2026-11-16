"""Refresh the standalone exhibit and its identical GitHub Pages copy."""
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parent
source = json.loads((root / "scene_data.json").read_text())
snapshot = {key: source[key] for key in ("meta", "atmospheres", "headline", "earth_checks")}
exhibit = root / "one_sixth.html"
html, count = re.subn(
    r'(<script id="registered" type="application/json">).*?(</script>)',
    lambda match: match[1] + json.dumps(snapshot, separators=(",", ":")) + match[2],
    exhibit.read_text(), flags=re.S,
)
if count != 1:
    raise ValueError("Expected one registered data snapshot.")
exhibit.write_text(html)
(root.parent / "docs" / "exhibit.html").write_text(html)
