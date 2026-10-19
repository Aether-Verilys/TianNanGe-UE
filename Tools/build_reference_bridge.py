"""Build real, editable centimetre-space bridge meshes, calibrated to the supplied painting.

No image planes: all snow, timber, ropes and ice have closed 3D geometry.
OBJ uses reflected Y and reversed winding to compensate the installed UE OBJ importer.
"""
import json,math,random
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Transfer_BridgeReference';OUT.mkdir(exist_ok=True)
ASPECT=4028/1949
PITCH=math.radians(4.2);TH=math.tan(math.radians(58.7979375/2));TV=TH/ASPECT
RNG=random.Random(233)

def unproject(x,uv):
    dx=x+460;q=(.5-uv[1])*2*TV
    dz=dx*(math.sin(PITCH)+q*math.cos(PITCH))/(math.cos(PITCH)-q*math.sin(PITCH))
    depth=dx*math.cos(PITCH)+dz*math.sin(PITCH)
    return np.array((x,(uv[0]-.5)*2*TH*depth,88+dz))

def project(p):
    dx,y,dz=np.array(p)-np.array((-460,0,88));d=dx*math.cos(PITCH)+dz*math.sin(PITCH)
    return (.5+y/(d*2*TH),.5-(-dx*math.sin(PITCH)+dz*math.cos(PITCH))/(d*2*TV))

class Mesh:
    def __init__(self,name,material):self.name=name;self.mat=material;self.v=[];self.uv=[];self.f=[]
    def vert(self,p,uv=(0,0)):
        self.v.append(tuple(p));self.uv.append(uv);return len(self.v)-1
    def tri(self,a,b,c,out=None):
        if out is not None and np.dot(np.cross(np.subtract(self.v[b],self.v[a]),np.subtract(self.v[c],self.v[a])),out)<0:b,c=c,b
        self.f.append((a,b,c))
    def quad(self,a,b,c,d,out=None):self.tri(a,b,c,out);self.tri(a,c,d,out)
    def save(self):
        p=np.array(self.v);n=np.zeros(p.shape);f=np.array(self.f)
        fn=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]])
        for j in range(3):np.add.at(n,f[:,j],fn)
        n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-12)
        with (OUT/(self.name+'.obj')).open('w',encoding='utf-8') as w:
            w.write('# Real bridge geometry; author Pleasant233\n')
            for x,y,z in p:w.write(f'v {x:.5f} {-y:.5f} {z:.5f}\n')
            for a,b in self.uv:w.write(f'vt {a:.6f} {b:.6f}\n')
            for x,y,z in n:w.write(f'vn {x:.6f} {-y:.6f} {z:.6f}\n')
            w.write('s 1\nusemtl '+self.mat+'\n')
            for a,b,c in self.f:w.write('f '+' '.join(f'{i+1}/{i+1}/{i+1}' for i in (a,c,b))+'\n')
        return dict(name=self.name,material=self.mat,vertices=len(p),triangles=len(self.f),bounds=[p.min(axis=0).tolist(),p.max(axis=0).tolist()])

wood=Mesh('SM_Bridge_Timber_Rails','timber')
posts=Mesh('SM_Bridge_Timber_Posts','timber')
snow=Mesh('SM_Bridge_Snow_Rails','snow')
caps=Mesh('SM_Bridge_Snow_Caps','snow')
ice=Mesh('SM_Bridge_Icicles','ice')
deck=Mesh('SM_Bridge_Snow_Deck','snow')
structure=Mesh('SM_Bridge_Structure','timber')

# Landmarks are centres of snow-covered rails, expressed in fractions of the original 4028 x 1949 image.
specs={
 'L_upper':dict(pts=[(-350,(-.12,-.124)),(70,(.413,.607)),(430,(.520,.686)),(1000,(.568,.728)),(2150,(.596,.750))],radius=3.5,cap=6.0,role='heavy',side=1),
 'L_middle':dict(pts=[(-350,(-.12,.5854)),(70,(.413,.739)),(430,(.520,.766)),(1000,(.568,.780)),(2150,(.596,.790))],radius=1.15,cap=2.3,role='rope',side=1),
 'L_lower':dict(pts=[(-350,(-.12,1.0051)),(70,(.413,.858)),(430,(.520,.826)),(1000,(.568,.806)),(2150,(.596,.798))],radius=3.0,cap=5.0,role='heavy',side=1),
 'R_upper':dict(pts=[(-350,(1.12,.1755)),(15,(.742,.600)),(300,(.682,.675)),(650,(.640,.716)),(1200,(.614,.740)),(2150,(.600,.753))],radius=3.7,cap=6.2,role='heavy',side=-1),
 'R_middle':dict(pts=[(-350,(1.12,.6342)),(15,(.742,.747)),(300,(.682,.772)),(650,(.640,.782)),(1200,(.614,.787)),(2150,(.600,.792))],radius=3.7,cap=6.8,role='heavy',side=-1),
 'R_lower':dict(pts=[(-350,(1.12,1.0110)),(15,(.742,.866)),(300,(.682,.830)),(650,(.640,.812)),(1200,(.614,.802)),(2150,(.600,.800))],radius=1.3,cap=2.7,role='rope',side=-1),
}
for name,s in specs.items():
    # The painting occludes the far span behind the character. Keep a usable real
    # bridge width there instead of collapsing both sides onto one vanishing pixel.
    fixed=[]
    for x,uv in s['pts']:
        if name.startswith('L_') and x==1000:uv=(.550,uv[1])
        if name.startswith('L_') and x==2150:uv=(.577,uv[1])
        if name.startswith('R_') and x==1200:uv=(.645,uv[1])
        if name.startswith('R_') and x==2150:uv=(.636,uv[1])
        fixed.append((x,uv))
    s['pts']=fixed;s['world']=[unproject(x,uv) for x,uv in fixed]

def line(s,x):
    ps=s['world'];xs=[p[0] for p in ps]
    if x<xs[0]:
        p=ps[0].copy();p[0]=x
        # Complete the approach behind the reference camera without crossing the two sides.
        p[2]=54+(78 if s['role']=='heavy' and s is specs.get('L_upper') else 76 if s is specs.get('R_upper') else 40 if s is specs.get('L_middle') or s is specs.get('R_middle') else 20)
        return p
    elif x>=xs[-1]:a,b=ps[-2:]
    else:
        j=int(np.searchsorted(xs,x));a,b=ps[max(0,j-1):j+1]
    t=(x-a[0])/(b[0]-a[0]);return a+(b-a)*t

def sweep(mesh,points,radius,section='wood',phase=0,side=1,nring=20):
    rings=[];distance=0;last=None
    for p in points:
        if last is not None:distance+=np.linalg.norm(p-last)
        last=p;x=p[0];ring=[]
        # Correlated variation creates coherent soft lobes rather than disconnected snowballs.
        wave=.13*math.sin(x*.055+phase)+.08*math.sin(x*.14+1.7*phase)+.05*math.sin(x*.31+phase)
        for j in range(nring):
            t=j*2*math.pi/nring;ct,st=math.cos(t),math.sin(t)
            if section=='snow':
                r=radius*(1+wave+.035*math.sin(5*t+x*.025))
                yy=r*ct
                zz=(radius*.85 if st>=0 else radius*.72)*st
                zz+=.23*math.sin(x*.13+ct*2.7)*max(st,0)
                # Rounded overhang with irregular attached tongues down the visible face.
                lobe=max(0,math.sin(x*.096+phase)+.42*math.sin(x*.237+.7))**3
                visible=max(0,ct*side)**9
                zz-=min(4,radius*.22*lobe)*visible
                pos=p+np.array((.08*math.sin(t*3+x*.13),yy,zz))
            else:
                r=radius*(1+.045*math.sin(x*.039+phase)+.025*math.sin(3*t+x*.08))
                pos=p+np.array((0,r*ct,r*st))
            ring.append(mesh.vert(pos,(distance/140,j/nring)))
        rings.append(ring)
        if len(rings)>1:
            old=rings[-2]
            for j in range(nring):
                k=(j+1)%nring;out=np.array((0,math.cos((j+.5)*2*math.pi/nring),math.sin((j+.5)*2*math.pi/nring)))
                mesh.quad(old[j],ring[j],ring[k],old[k],out)
    for end,sgn in [(0,-1),(-1,1)]:
        center=mesh.vert(points[end]);ring=rings[end]
        for j in range(nring):mesh.tri(center,ring[j],ring[(j+1)%nring],np.array((sgn,0,0)))

def ellipsoid(mesh,center,radii,phase=0,sides=20,steps=10):
    c=np.array(center);r=np.array(radii);rings=[]
    for i in range(steps+1):
        a=math.pi*(.0001+(1-.0002)*i/steps);ring=[]
        for j in range(sides):
            b=2*math.pi*j/sides;normal=np.array((math.sin(a)*math.cos(b),math.sin(a)*math.sin(b),math.cos(a)))
            noise=1+.055*math.sin(b*3+a*7+phase)+.025*math.cos(b*7-a*4+phase)
            ring.append(mesh.vert(c+normal*r*noise,(j/sides,i/steps)))
        rings.append(ring)
        if i:
            for j in range(sides):
                k=(j+1)%sides;out=np.array(mesh.v[ring[j]])-c
                mesh.quad(rings[-2][j],ring[j],ring[k],rings[-2][k],out)

def icicle(center,length,radius,phase):
    c=np.array(center);rings=[];sides=9
    for k,(fraction,scale) in enumerate([(0,1.30),(.09,1),(.3,.70),(.58,.42),(.84,.19),(1,.025)]):
        ring=[]
        for j in range(sides):
            t=2*math.pi*j/sides; rr=radius*scale*(1+.1*math.sin(3*t+phase))
            p=c+np.array((rr*math.cos(t)+fraction*fraction*.65*math.sin(phase),rr*math.sin(t)+fraction*fraction*.65*math.cos(phase),-length*fraction))
            ring.append(ice.vert(p,(j/sides,fraction)))
        rings.append(ring)
        if k:
            for j in range(sides):
                m=(j+1)%sides
                ice.quad(rings[-2][j],ring[j],ring[m],rings[-2][m],(math.cos((j+.5)*2*math.pi/sides),math.sin((j+.5)*2*math.pi/sides),0))

landmarks=[]
for index,(name,s) in enumerate(specs.items()):
    points=[]
    # Generate dense longitudinal rings with a tiny natural sag between real supports.
    full=[line(s,-1650)]+s['world']
    for a,b in zip(full[:-1],full[1:]):
        steps=max(2,math.ceil((b[0]-a[0])/3.5))
        for i in range(steps):
            t=i/steps;p=a+(b-a)*t;p[2]-=.55*math.sin(math.pi*t)**2
            points.append(p)
    points.append(s['world'][-1])
    woodpoints=[p-np.array((0,0,3.1 if s['role']=='heavy' else 0)) for p in points]
    sweep(wood,woodpoints,s['radius'],phase=index,nring=16)
    if s['role']=='heavy':
        sweep(snow,points,s['cap'],'snow',phase=index,side=s['side'],nring=24)
        x=-340
        while x<2150:
            x+=RNG.uniform(22,55)
            p=line(s,x)+np.array((0,s['side']*s['cap']*.65,-1.8))
            length=RNG.uniform(2.5,12)*(1.85 if RNG.random()<.18 else 1)
            icicle(p,length,RNG.uniform(.55,1.35),RNG.random()*7)
    else:
        x=-340
        while x<2150:
            x+=RNG.uniform(13,30);p=line(s,x)
            ellipsoid(caps,p+np.array((0,0,1.0)),(RNG.uniform(3,7),RNG.uniform(1.8,3.2),RNG.uniform(1.6,3.1)),RNG.random()*7,sides=12,steps=7)
    for (x,uv),p in zip(s['pts'],s['world']):landmarks.append(dict(rail=name,x=x,reference_uv=uv,visible_reference_anchor=(-350<x<=430),world=p.tolist(),projection=project(p)))

def floor(x):
    if x< -100:return 6.2+min(48,(-100-x)*.15)
    if x<=100:return 6.2
    target=(line(specs['L_lower'],x)[2]+line(specs['R_lower'],x)[2])*.5-19
    t=min(1,(x-100)/160);return 6.2*(1-t)+target*t

def post(side,x,i):
    s=specs[side+'_upper'];p=line(s,x);y=p[1];base=floor(x)-5;top=p[2]+12
    radius=5.6 if i==0 else 4.1
    # Slightly chamfered taper, less regular than the source cubes.
    rings=[]
    for z,sc in [(base,.91),(base+5,1),(top-5,.87),(top,.79)]:
        ring=[]
        for j in range(8):
            a=math.pi/8+j*math.pi/4
            ring.append(posts.vert((x+radius*sc*math.cos(a),y+radius*sc*math.sin(a),z),((j/8),z/100)))
        rings.append(ring)
        if len(rings)>1:
            for j in range(8):
                k=(j+1)%8;angle=math.pi/8+(j+.5)*math.pi/4
                posts.quad(rings[-2][j],ring[j],ring[k],rings[-2][k],(math.cos(angle),math.sin(angle),0))
    center=posts.vert((x,y,top))
    for j in range(8):posts.tri(center,rings[-1][j],rings[-1][(j+1)%8],(0,0,1))
    ellipsoid(caps,(x,y,top+2),(radius*1.3,radius*1.3,7.8 if i==0 else 5.6),phase=i+(0 if side=='L' else 3))
    # Snow drifts at feet, and wind-packed snow on the outside face of each pillar.
    ellipsoid(caps,(x+2,y,base+6),(13 if i==0 else 9,10 if i==0 else 7,10),phase=i)
    for z in np.arange(base+23,top-4,24):
        if RNG.random()<.68:ellipsoid(caps,(x+1,y+(1 if side=='R' else -1)*radius*.7,z),(radius*.85,radius*.62,16),phase=z,sides=14,steps=8)

for side,xs in [('L',[70,430,1000,1700,2150,-850,-1500]),('R',[15,300,650,1200,1800,2150,-850,-1500])]:
    for i,x in enumerate(xs):post(side,x,i)

# A fully three-dimensional snow deck: flat at the existing character's feet,
# then descending and bending right with the painting. No repeated dark joints.
xs=np.linspace(-2000,2150,510);rows=[]
for x in xs:
    yl=line(specs['L_lower'],x)[1]-5;yr=line(specs['R_lower'],x)[1]+5;row=[]
    for j,t in enumerate(np.linspace(0,1,41)):
        y=yl+(yr-yl)*t
        wind=.15*math.sin(x*.11+y*.13)+.10*math.sin(x*.29-y*.07)
        edge=3.2*math.exp(-(t/.065)**2)+4.3*math.exp(-((1-t)/.075)**2)
        z=floor(x)+wind+edge*(1+.23*math.sin(x*.035))
        row.append(deck.vert((x,y,z),(x/180,y/180)))
    rows.append(row)
    if len(rows)>1:
        for j in range(40):deck.quad(rows[-2][j],row[j],row[j+1],rows[-2][j+1],(0,0,1))
for side in ['L','R']:
    points=[]
    for x in np.linspace(-2000,2150,510):
        p=line(specs[side+'_lower'],x);p[2]=floor(x)-11;points.append(p)
    sweep(structure,points,11,phase=3,nring=12)
    # A soft snowbank hides the hard edge of the old deck's silhouette.
    points=[p+np.array((0,0,16)) for p in points]
    sweep(caps,points,6.5,'snow',phase=7,side=1 if side=='L' else -1,nring=18)

meshes=[m.save() for m in [wood,posts,snow,caps,ice,deck,structure]]
manifest=dict(author='Pleasant233',units='cm',camera=dict(position=[-460,0,88],pitch=4.2,hfov=58.7979375,aspect=ASPECT),meshes=meshes,landmarks=landmarks,total_triangles=sum(m['triangles'] for m in meshes),primary_posts=11,notes=['real 3D geometry','preserve existing lighting and camera','sparse asymmetric pillars','left middle and right lower are snow-clumped ropes'])
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k not in ('landmarks',)},indent=2))
