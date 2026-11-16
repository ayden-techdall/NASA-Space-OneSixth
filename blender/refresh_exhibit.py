"""Refresh the self-contained exhibit from the local registered data and relief."""
import base64
import io
import json
import re
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent
out = root / 'one_sixth.html'
source = json.loads((root / 'scene_data.json').read_text())
snapshot = {key: source[key] for key in ('atmospheres', 'headline', 'earth_checks')}
moon = Image.open(root / 'renders/lunar_relief.png').convert('RGBA')
backing = Image.new('RGB', moon.size, '#142028')
backing.paste(moon, mask=moon.getchannel('A'))
buf = io.BytesIO()
backing.save(buf, format='JPEG', quality=87, optimize=True)
uri = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
html = out.read_text()
html, image_count = re.subn(r'(?<=<img src=")data:image/jpeg;base64,[A-Za-z0-9/+=]+', uri, html)
html, data_count = re.subn(r'(<script id="registered" type="application/json">).*?(</script>)',
                            lambda match:match[1]+json.dumps(snapshot,separators=(',',':'))+match[2],
                            html, flags=re.S)
if (image_count, data_count) != (1, 1):
    raise ValueError('Expected one embedded relief image and one data snapshot.')
out.write_text(html)
