"""Fetch attributed cloud volume data and repack its slice atlas for UE."""
from pathlib import Path
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
import json,hashlib
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1];out=root/'SourceAssets/CloudNoise';out.mkdir(parents=True,exist_ok=True)
repo='https://raw.githubusercontent.com/TylerDodds/VolumetricCloudsTutorial/master/'
(out/'LICENSE-TylerDodds.txt').write_bytes(urlopen(repo+'LICENSE',timeout=20).read())
records=[]
for stem,n,columns,total in [('noiseShape',128,16,8388647),('noiseErosion',32,8,131111)]:
    url=repo+'Assets/VolumetricCloudsTutorial/CloudDensity/NoiseTextures/'+stem+'.tga'
    def chunk(pair):
        start,finish=pair
        req=Request(url,headers={'Range':f'bytes={start}-{finish}','Accept-Encoding':'identity'})
        with urlopen(req,timeout=40) as response:
            data=response.read()
            assert len(data)==finish-start+1,(start,len(data),response.status)
            return data
    ranges=[(i,min(i+262143,total-1)) for i in range(0,total,262144)]
    with ThreadPoolExecutor(max_workers=6) as pool:data=b''.join(pool.map(chunk,ranges))
    p=out/(stem+'.tga');p.write_bytes(data)
    img=np.array(Image.open(p).convert('RGBA'));assert img.shape[:2]==(n,n*n)
    atlas=np.empty((n*(n//columns),n*columns,4),dtype=np.uint8)
    for z in range(n):atlas[(z//columns)*n:(z//columns+1)*n,(z%columns)*n:(z%columns+1)*n]=img[:,z*n:(z+1)*n]
    target=out/(stem+'_atlas.png');Image.fromarray(atlas).save(target)
    records.append({'source':url,'volume_resolution':[n]*3,'original_sha256':hashlib.sha256(data).hexdigest(),'atlas':str(target.relative_to(root)),'atlas_size':[atlas.shape[1],atlas.shape[0]],'tile_size':n,'license':'MIT, Tyler Dodds 2019'})
    print(stem,'downloaded and repacked',flush=True)
(out/'sources.json').write_text(json.dumps(records,indent=2))
