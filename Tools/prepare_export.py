"""Build an isolated, minimal Unity project to evaluate serialized scene geometry."""
import json, shutil, argparse
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--source',default='D:/Dev/TianNanGe/Project_TianNanGe')
args=parser.parse_args()
source=Path(args.source)
target=(Path(__file__).resolve().parents[1] / 'UnityExportProject')
if (target/'Assets').exists():raise RuntimeError('Export project already exists; inspect it before rebuilding')
shutil.copytree(source/'Assets',target/'Assets',ignore=shutil.ignore_patterns('*.cs','*.cs.meta','*.asmdef','*.asmdef.meta','*.asmref','*.asmref.meta'))
(target/'Packages').mkdir(parents=True,exist_ok=True)
# Built-in modules only. Missing HDRP MonoBehaviours do not prevent mesh export.
(target/'Packages/manifest.json').write_text(json.dumps({'dependencies':{f'com.unity.modules.{n}':'1.0.0' for n in ['animation','physics','particlesystem','imageconversion','audio','ui','terrain','terrainphysics','jsonserialize'] }},indent=2))
(target/'Assets/Editor').mkdir(exist_ok=True)
shutil.copy2(Path(__file__).with_name('TianNanGeExport.cs'),target/'Assets/Editor/TianNanGeExport.cs')
print('Export copy prepared:',target)
