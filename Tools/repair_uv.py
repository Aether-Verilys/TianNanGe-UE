from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
fixed=[]
for path in (root/'Transfer/Meshes').glob('*.obj'):
    text=path.read_text()
    if '\nvt ' in text:continue
    vertices=sum(line.startswith('v ') for line in text.splitlines())
    uv='vt 0 0\n'*vertices
    at=text.find('\nvn ')
    if at<0:at=text.find('\nusemtl ')
    text=text[:at+1]+uv+text[at+1:]
    text=re.sub(r'(\d+)//(\d+)',r'\1/\1/\2',text)
    path.write_text(text)
    fixed.append(path.stem)
(root/'Tools/uv-repair.json').write_text(json.dumps(fixed))
print('Explicit zero UV channel added:',len(fixed),'untextured procedural meshes')
