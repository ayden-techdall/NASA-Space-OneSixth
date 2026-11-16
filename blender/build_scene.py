"""Build the editable One-Sixth research plate with Blender's Python interpreter.

blender --background --python-exit-code 1 --python blender/build_scene.py -- --save --render
"""
from pathlib import Path
import math
import sys
import bpy

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from plate import H, W, plate

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = 'One-Sixth | The lunar burn limit'
bpy.context.preferences.filepaths.save_version = 0
scene.render.engine = 'CYCLES'
scene.cycles.samples = 4
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
scene.view_settings.exposure = 0

def group(name):
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    return col

page = group('Paper and rules')
labels = group('Editable typography')
data_marks = group('Oxygen scale and data')
illustration = group('Illustrative lunar relief')
materials = {}

def color_material(hex_color):
    if hex_color in materials:
        return materials[hex_color]
    color = [int(hex_color[i:i+2], 16)/255 for i in (1,3,5)]
    linear = [(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for v in color]
    mat = bpy.data.materials.new('Ink '+hex_color)
    mat.diffuse_color = (*linear,1)
    mat.use_nodes = True
    tree = mat.node_tree
    out = tree.nodes.get('Material Output')
    em = tree.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*linear,1)
    tree.links.new(em.outputs[0],out.inputs['Surface'])
    materials[hex_color] = mat
    return mat

def mesh(name, verts, faces, collection, material=None):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts,[],faces)
    data.update()
    obj = bpy.data.objects.new(name,data)
    collection.objects.link(obj)
    if material:
        data.materials.append(material)
    return obj

def vertex(x,y,z):
    return ((x-W/2)/100,(H/2-y)/100,z)

def polygon(name, points, z, color, collection):
    return mesh(name,[vertex(x,y,z) for x,y in points],[list(range(len(points)))],collection,color_material(color))

def rule(name,start,end,width,z,color,collection):
    dx,dy=end[0]-start[0],end[1]-start[1]
    d=math.hypot(dx,dy)
    nx,ny=-dy/d*width/2,dx/d*width/2
    return polygon(name,[(start[0]+nx,start[1]+ny),(end[0]+nx,end[1]+ny),(end[0]-nx,end[1]-ny),(start[0]-nx,start[1]-ny)],z,color,collection)

face_names = {'serif':('Georgia.ttf','DejaVuSerif.ttf'),'italic':('Georgia Italic.ttf','DejaVuSerif-Italic.ttf'),
              'bold':('Arial Bold.ttf','DejaVuSans-Bold.ttf'),'regular':('Arial.ttf','DejaVuSans.ttf'),
              'mono':('Courier New Bold.ttf','DejaVuSansMono-Bold.ttf')}
def load_face(face):
    for location in [Path('/System/Library/Fonts/Supplemental'),Path('/usr/share/fonts/truetype/dejavu'),Path('C:/Windows/Fonts')]:
        for file in face_names[face]:
            path=location/file
            if path.exists():
                return bpy.data.fonts.load(str(path),check_existing=True)
    return bpy.data.fonts.get('Bfont')

def add_text(name,x,y,text,size,face,color,z):
    curve=bpy.data.curves.new(name,'FONT')
    font=load_face(face)
    if font:curve.font=font
    curve.body=text
    curve.size=size/100
    obj=bpy.data.objects.new(name,curve)
    labels.objects.link(obj)
    curve.materials.append(color_material(color))
    # Use the actual glyph bounds for the top alignment of this line.
    bpy.context.view_layer.update()
    top=max(v[1] for v in obj.bound_box)
    X,Y,_=vertex(x,y,z)
    obj.location=(X,Y-top,z)

def add_globe(box,src,z):
    # A spherical shell with an orthographic UV projection of the original relief.
    # The rear uses the same illustrative texture reflected by the projection.
    x1,y1,x2,y2=box
    cx,cy=(x1+x2)/2,(y1+y2)/2
    radius=(x2-x1)*.477
    rings,sectors=80,160
    coords=[];uv=[];faces=[]
    for i in range(rings+1):
        lat=math.pi*i/rings
        for j in range(sectors):
            lon=2*math.pi*j/sectors
            nx,ny,nz=math.sin(lat)*math.cos(lon),math.cos(lat),math.sin(lat)*math.sin(lon)
            coords.append(vertex(cx+radius*nx,cy-radius*ny,z+radius/100*(nz-1)))
            uv.append((.5+.477*nx,.5+.477*ny))
    for i in range(rings):
        for j in range(sectors):
            a=i*sectors+j;b=i*sectors+(j+1)%sectors
            faces.append((a,b,b+sectors,a+sectors))
    obj=mesh('Moon | illustrative relief',coords,faces,illustration)
    layer=obj.data.uv_layers.new(name='Orthographic relief')
    for loop in obj.data.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
    image=bpy.data.images.load(str(ROOT/src))
    image.pack()
    mat=bpy.data.materials.new('Original lunar relief')
    mat.use_nodes=True
    tree=mat.node_tree
    tex=tree.nodes.new('ShaderNodeTexImage');tex.image=image
    glow=tree.nodes.new('ShaderNodeEmission')
    tree.links.new(tex.outputs['Color'],glow.inputs['Color'])
    tree.links.new(glow.outputs[0],tree.nodes.get('Material Output').inputs['Surface'])
    obj.data.materials.append(mat)

for idx,(kind,name,*args) in enumerate(plate()):
    # Clear the page plane behind the three-dimensional sphere.
    z=idx*.003
    col=data_marks if name.startswith(('Forecast','Scale','Central','Habitat reference')) else page
    if kind=='rect':
        (a,b,c,d),color=args
        polygon(name,[(a,b),(a,d),(c,d),(c,b)],z,color,col)
    elif kind=='line':
        points,color,width=args
        for a,b in zip(points,points[1:]):rule(name,a,b,width,z,color,col)
    elif kind=='dot':
        x,y,r,color=args
        pts=[(x+r*math.cos(i*math.tau/48),y+r*math.sin(i*math.tau/48)) for i in range(48)]
        polygon(name,pts,z,color,data_marks)
    elif kind=='text':add_text(name,*args,z)
    elif kind=='image':add_globe(*args,z+6)
camera_data=bpy.data.cameras.new('Orthographic plate camera')
camera_data.type='ORTHO'
camera_data.ortho_scale=W/100
camera=bpy.data.objects.new('Plate camera',camera_data)
scene.collection.objects.link(camera)
camera.location=(0,0,18)
camera.rotation_euler=(0,0,0)
scene.camera=camera
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.color_type='MATERIAL'
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(ROOT/'renders/one_sixth_hero.png')
options=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['--save','--render']
if '--save' in options:bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'one_sixth.blend'))
if '--render' in options:bpy.ops.render.render(write_still=True)
