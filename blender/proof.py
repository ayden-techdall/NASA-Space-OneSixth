"""Render the same orthographic composition with Pillow when Blender is unavailable."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from plate import ROOT,W,H,plate
S=2
fonts={'serif':('Georgia.ttf','DejaVuSerif.ttf'),'italic':('Georgia Italic.ttf','DejaVuSerif-Italic.ttf'),
       'regular':('Arial.ttf','DejaVuSans.ttf'),'bold':('Arial Bold.ttf','DejaVuSans-Bold.ttf'),
       'mono':('Courier New Bold.ttf','DejaVuSansMono.ttf')}
def font(face,size):
    for folder in [Path('/System/Library/Fonts/Supplemental'),Path('/usr/share/fonts/truetype/dejavu')]:
        for fname in fonts[face]:
            f=folder/fname
            if f.is_file():return ImageFont.truetype(str(f),size*S)
    return ImageFont.load_default(size=size*S)
def coords(box):return tuple(round(v*S) for v in box)
image=Image.new('RGB',(W*S,H*S))
draw=ImageDraw.Draw(image)
for kind,name,*args in plate():
    if kind=='rect':draw.rectangle(coords(args[0]),fill=args[1])
    elif kind=='dot':
        x,y,r,c=args;draw.ellipse(coords((x-r,y-r,x+r,y+r)),fill=c)
    elif kind=='line':draw.line([coords(v) for v in args[0]],fill=args[1],width=args[2]*S)
    elif kind=='text':
        x,y,s,n,f,c=args;draw.text(coords((x,y)),s,font=font(f,n),fill=c,anchor='lt')
    elif kind=='image':
        (a,b,c,d),src=args;im=Image.open(ROOT/src).resize(coords((c-a,d-b)),Image.Resampling.LANCZOS)
        image.paste(im,coords((a,b)),im)
image.resize((W,H),Image.Resampling.LANCZOS).save(ROOT/'renders/one_sixth_hero.png',optimize=True)
