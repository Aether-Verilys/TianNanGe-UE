"""Prefetch and verify every LFS object for the pinned public source commit."""
import json,urllib.request as req,concurrent.futures as cf,subprocess,re,hashlib,shutil,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
snapshot=root/'SourceSnapshot'
checkout=Path('D:/Dev/TianNanGe')
sha='43e985267fca227ab23816204ca6dc6deaa80078'
paths=subprocess.check_output(['git','-C',str(snapshot),'ls-tree','-r','--name-only','origin/main'],text=True).splitlines()
paths=[p for p in paths if Path(p).suffix.lower() in ['.fbx','.blend','.exr','.hdr']]
def pointer(path):
    for attempt in range(3):
        try:
            with req.urlopen('https://raw.githubusercontent.com/Aether-Verilys/TianNanGe/'+sha+'/'+req.quote(path,safe='/'),timeout=35) as r:text=r.read().decode()
            oid=re.search(r'oid sha256:(\w+)',text);size=re.search(r'size (\d+)',text)
            return (path,oid[1],int(size[1])) if oid and size else None
        except Exception:
            if attempt==2:raise
with cf.ThreadPoolExecutor(max_workers=10) as pool:items=[v for v in pool.map(pointer,paths) if v]
objects={oid:size for _,oid,size in items}
def cache_path(base,oid):return base/'.git/lfs/objects'/oid[:2]/oid[2:4]/oid
pending={}
for oid,size in objects.items():
    dest=cache_path(checkout,oid);dest.parent.mkdir(parents=True,exist_ok=True)
    local=cache_path(snapshot,oid)
    if dest.exists() and dest.stat().st_size==size:continue
    if local.exists() and local.stat().st_size==size:shutil.copy2(local,dest)
    else:pending[oid]=size
print('LFS_PREFETCH',len(items),'files',len(objects),'unique; remaining',len(pending),sum(pending.values()),'bytes',flush=True)
if pending:
    body=json.dumps({'operation':'download','transfers':['basic'],'objects':[{'oid':oid,'size':size} for oid,size in pending.items()]}).encode()
    request=req.Request('https://github.com/Aether-Verilys/TianNanGe.git/info/lfs/objects/batch',data=body,headers={'Accept':'application/vnd.git-lfs+json','Content-Type':'application/vnd.git-lfs+json'})
    with req.urlopen(request,timeout=60) as response:actions={o['oid']:o['actions']['download'] for o in json.load(response)['objects']}
    def fetch(item):
        oid,size=item;action=actions[oid]
        parts=root/'LfsParts';parts.mkdir(exist_ok=True)
        def chunk(start):
            end=min(start+512*1024,size)-1
            cache=parts/f'{oid}.{start}.part'
            if cache.exists() and cache.stat().st_size==end-start+1:return cache.read_bytes()
            for attempt in range(5):
                try:
                    headers=dict(action.get('header',{}));headers['Range']=f'bytes={start}-{end}'
                    with req.urlopen(req.Request(action['href'],headers=headers),timeout=35) as response:
                        if size>512*1024:assert response.headers.get('Content-Range','').startswith(f'bytes {start}-{end}/')
                        content=response.read()
                    assert len(content)==end-start+1
                    cache.write_bytes(content);return content
                except Exception:
                    if attempt==4:raise
            raise RuntimeError('No downloaded content')
        with cf.ThreadPoolExecutor(max_workers=8) as pool:content=b''.join(pool.map(chunk,range(0,size,512*1024)))
        assert hashlib.sha256(content).hexdigest()==oid,oid
        cache_path(checkout,oid).write_bytes(content)
        print('LFS_VERIFIED',oid[:12],size,flush=True)
    with cf.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(fetch,pending.items()))
(root/'source-lfs-manifest.json').write_text(json.dumps([{'path':p,'sha256':oid,'size':size} for p,oid,size in items],indent=2))
print('ALL_LFS_VERIFIED',flush=True)
