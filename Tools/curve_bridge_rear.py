"""Increase the rear-span bend without moving foreground support landmarks or lighting."""
from pathlib import Path
import numpy as np,json,shutil,sys
ROOT=(Path(__file__).resolve().parents[1] / 'Transfer_BridgeReference')
BASE=ROOT/'BeforeRearCurve';BASE.mkdir(exist_ok=True)

def deformation(x):
    t=np.clip((x-250)/2050,0,1)
    sag=np.sin(np.pi*t)**2
    e=np.clip((x-1550)/600,0,1);rise=e*e*(3-2*e)
    return np.column_stack((135*sag-285*rise,-115*sag+172*rise))

for path in ROOT.glob('*.obj'):
    src=BASE/path.name
    if not src.exists() or '--refresh-base' in sys.argv:shutil.copy2(path,src)
    text=src.read_text().splitlines();vs=[];ns=[];vi=[];ni=[]
    for i,line in enumerate(text):
        if line.startswith('v '):vi.append(i);vs.append([float(v) for v in line[2:].split()])
        elif line.startswith('vn '):ni.append(i);ns.append([float(v) for v in line[3:].split()])
    v=np.array(vs);n=np.array(ns);x=v[:,0];d=deformation(x)
    # OBJ Y is reflected relative to UE; preserve the installed import transform.
    derivative=(deformation(x+.05)-deformation(x-.05))/.1
    v[:,1]-=d[:,0];v[:,2]+=d[:,1]
    n[:,0]+=derivative[:,0]*n[:,1]-derivative[:,1]*n[:,2]
    n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-12)
    for i,p in zip(vi,v):text[i]='v '+' '.join(f'{a:.5f}' for a in p)
    for i,p in zip(ni,n):text[i]='vn '+' '.join(f'{a:.6f}' for a in p)
    path.write_text('\n'.join(text)+'\n')
    print(path.name)
manifest=json.loads((ROOT/'manifest.json').read_text())
manifest['rear_curve']=dict(start_x_cm=250,max_extra_sag_cm=115,max_right_bow_cm=135,far_end_lift_cm=172,far_end_left_return_cm=285,foreground_posts_preserved=True)
manifest['primary_posts']=15
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
