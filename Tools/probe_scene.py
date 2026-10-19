import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sample={'unityVersion':'probe','nodes':[],'materials':[],'warnings':[], 'lights':[{'name':'Sun','forward':{'x':.5,'y':.5,'z':-.5},'color':{'r':1,'g':.92,'b':.78,'a':1},'intensity':50000}], 'camera':{'position':{'x':-460,'y':0,'z':88},'forward':{'x':1,'y':0,'z':.08},'up':{'x':0,'y':0,'z':1},'fov':32,'aspect':1280/620}}
(root/'Transfer/probe-scene.json').write_text(json.dumps(sample))
code=(root/'Tools/import_scene.py').read_text().replace("Transfer/scene.json","Transfer/probe-scene.json").replace('/Game/TianNanGe','/Game/MigrationProbe').replace('TianNanGe_Main','ProbeMap').replace('migration-result.json','probe-scene-result.json')
exec(compile(code,'probe_import_scene','exec'))
