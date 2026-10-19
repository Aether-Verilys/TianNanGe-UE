"""Fetch only geometry and material maps needed by the export from the public source.
Large unrelated source textures continue downloading in the full checkout.
"""
from pathlib import Path
import urllib.request as req,json,re,hashlib,time,concurrent.futures,yaml,os
root=(Path(__file__).resolve().parents[1] / 'SourceSnapshot')
project=root/'Project_TianNanGe'
commit='43e985267fca227ab23816204ca6dc6deaa80078'
guid={}
for meta in (project/'Assets').rglob('*.meta'):
    m=re.search(r'^guid: (\w+)',meta.read_text(encoding='utf-8',errors='replace'),re.M)
    if m:guid[m[1]]=Path(str(meta)[:-5])
maps=set()
for pattern in ['*.png.meta','*.jpg.meta','*.jpeg.meta']:
    for meta in (project/'Assets/Character').rglob(pattern):maps.add(Path(str(meta)[:-5]))
for mat in (project/'Assets').rglob('*.mat'):
    text=mat.read_text(encoding='utf-8');text=re.sub(r'^%.*\n','',text,flags=re.M);text=re.sub(r'^--- !u!\d+ &-?\d+','---',text,flags=re.M)
    data=next(d['Material']['m_SavedProperties'] for d in yaml.safe_load_all(text) if d and 'Material' in d)
    for item in data.get('m_TexEnvs',[]):
        for key,value in item.items():
            if key in ['_BaseColorMap','_MainTex','_NormalMap','_BumpMap','_MaskMap']:
                path=guid.get(value.get('m_Texture',{}).get('guid'))
                if path and path.suffix.lower() in ['.png','.jpg','.jpeg']:maps.add(path)

def fetch_map(path):
    if path.exists():return
    url='https://raw.githubusercontent.com/Aether-Verilys/TianNanGe/'+commit+'/'+req.quote(path.relative_to(root).as_posix(),safe='/')
    for attempt in range(3):
        try:
            with req.urlopen(url,timeout=90) as response:content=response.read()
            path.write_bytes(content);print('Texture',path.name,len(content),flush=True);return
        except Exception:
            if attempt==2:raise
            time.sleep(1)

if os.environ.get('TIANNANGE_SKIP_TEXTURES')!='1':
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(fetch_map,sorted(maps)))
pointers=[]
if os.environ.get('TIANNANGE_TEXTURES_ONLY')=='1':raise SystemExit(0)
for path in (project/'Assets').rglob('*.fbx'):
    if path.stat().st_size>512:continue
    text=path.read_text();oid=re.search(r'oid sha256:(\w+)',text);size=re.search(r'size (\d+)',text)
    if oid and size:pointers.append((path,oid[1],int(size[1])))
if not pointers:
    print('SNAPSHOT_ASSETS_READY',flush=True)
    raise SystemExit(0)
body=json.dumps({'operation':'download','transfers':['basic'],'objects':[{'oid':oid,'size':size} for _,oid,size in pointers]}).encode()
request=req.Request('https://github.com/Aether-Verilys/TianNanGe.git/info/lfs/objects/batch',data=body,headers={'Accept':'application/vnd.git-lfs+json','Content-Type':'application/vnd.git-lfs+json'})
with req.urlopen(request,timeout=90) as response:objects=json.load(response)['objects']
downloads={o['oid']:o['actions']['download'] for o in objects}
def fetch_model(item):
    path,oid,size=item;action=downloads[oid]
    for attempt in range(3):
        try:
            if size>8*1024*1024:
                chunk_size=512*1024
                chunks=[(start,min(start+chunk_size,size)-1) for start in range(0,size,chunk_size)]
                def fetch_chunk(span):
                    start,end=span
                    headers=dict(action.get('header',{}));headers['Range']=f'bytes={start}-{end}'
                    cache=root/'.asset-parts'/f'{oid}.{start}.part';cache.parent.mkdir(exist_ok=True)
                    if cache.exists() and cache.stat().st_size==end-start+1:return cache.read_bytes()
                    for chunk_attempt in range(4):
                        try:
                            with req.urlopen(req.Request(action['href'],headers=headers),timeout=35) as response:
                                assert response.headers.get('Content-Range','').startswith(f'bytes {start}-{end}/')
                                part=response.read()
                            break
                        except Exception:
                            if chunk_attempt==3:raise
                    assert len(part)==end-start+1,(path.name,start,len(part))
                    cache.write_bytes(part)
                    return part
                with concurrent.futures.ThreadPoolExecutor(max_workers=12) as chunks_pool:content=b''.join(chunks_pool.map(fetch_chunk,chunks))
            else:
                request=req.Request(action['href'],headers=action.get('header',{}))
                with req.urlopen(request,timeout=180) as response:content=response.read()
            assert len(content)==size and hashlib.sha256(content).hexdigest()==oid,path
            path.write_bytes(content)
            cache=root/'.git/lfs/objects'/oid[:2]/oid[2:4]/oid;cache.parent.mkdir(parents=True,exist_ok=True);cache.write_bytes(content)
            print('Verified LFS',path.name,size,flush=True);return
        except Exception:
            if attempt==2:raise
            time.sleep(1)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch_model,pointers))
print('SNAPSHOT_ASSETS_READY',flush=True)
