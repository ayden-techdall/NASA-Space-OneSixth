"""An original procedural relief for the illustrated lunar globe. No measured topography."""
from pathlib import Path
import math
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
SIZE = 800
rng = np.random.default_rng(6349)
axis = (np.arange(SIZE) + .5 - SIZE/2) / (SIZE*.477)
x,y = np.meshgrid(axis, -axis)
r2 = x*x+y*y
z = np.sqrt(np.maximum(0,1-r2))
# A topographic height field on a sphere, with overlapping bowls and ejecta rims.
height = np.zeros_like(z)
albedo = np.ones_like(z)*.78
for scale, amplitude in [(8,.11),(16,.065),(40,.045),(90,.033),(200,.022),(500,.016)]:
    noise = Image.fromarray(rng.normal(128,34,(scale,scale)).clip(0,255).astype('uint8'))
    field = (np.asarray(noise.resize((SIZE,SIZE),Image.Resampling.BICUBIC)).astype(float)-128)/45
    albedo += amplitude*field
    height += field*amplitude*.0065
for radius in sorted(np.exp(rng.uniform(np.log(.007),np.log(.135),1150)),reverse=True):
    a,b = rng.uniform(-1.12,1.12,2)
    if a*a+b*b>=.99: continue
    c = math.sqrt(1-a*a-b*b)
    selection = (slice(max(0,int(SIZE*(.5-.477*(b+radius*1.5)))),min(SIZE,int(SIZE*(.5-.477*(b-radius*1.5)))+1)),
                 slice(max(0,int(SIZE*(.5+.477*(a-radius*1.5)))),min(SIZE,int(SIZE*(.5+.477*(a+radius*1.5)))+1)))
    d=np.sqrt((x[selection]-a)**2+(y[selection]-b)**2+(z[selection]-c)**2)/radius
    angle=np.arctan2(y[selection]-b,x[selection]-a)
    d*=1+.045*np.sin(3*angle+12*a)+.031*np.sin(8*angle+3*b)
    rim=np.exp(-((d-.91)/.14)**2)
    bowl=np.maximum(1-d*d,0)
    height[selection]+=radius*(.040*rim-.12*bowl)
    albedo[selection]+=.035*rim-.032*bowl
dy,dx=np.gradient(height,abs(axis[1]-axis[0]))
# Apply gradients as normals tangent to the visible sphere.
nx=x-z*dx; ny=y+z*dy; nz=z
scale=np.sqrt(nx*nx+ny*ny+nz*nz)+1e-7
incidence=(-.76*nx+.47*ny+.18*nz)/scale
day=np.clip((-.76*x+.47*y+.18*z+.075)/.17,0,1)
light=.025+day*.99*np.maximum(incidence,0)**.67
grain=rng.normal(0,.012,(SIZE,SIZE))
value=np.clip(albedo*light+grain*np.sqrt(light),0,1.2)
base=np.array([12,20,25])
rgb=base+value[...,None]*np.array([226,216,196])
alpha=(np.clip((1-np.sqrt(r2))*SIZE*.477+.5,0,1)*255).astype('uint8')
image=Image.fromarray(np.dstack((rgb.clip(0,255).astype('uint8'),alpha)))
image.save(HERE/'renders'/'lunar_relief.png',optimize=True)
