"""Import one user-generated mountain at a time; never rebuild the scene."""
import unreal as u, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SourceAssets/RealisticMountains/UserGenerated_20261027'
FILES=['SM_TNG_Mountain_01_Rocky','SM_TNG_Mountain_02_Peak','SM_TNG_Mountain_03_Cliff']
command=globals().get('COMMAND',{})
index=int(command.get('index',0))
name=FILES[index]
source=OUT/(name+'.glb')
assert source.exists(),source
dest='/Game/TianNanGe/RealisticMountains/'+name
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
task=u.AssetImportTask()
for k,v in dict(filename=str(source),destination_path=dest,destination_name=name,automated=True,replace_existing=False,save=True).items():task.set_editor_property(k,v)
u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
paths=list(task.get_editor_property('imported_object_paths'))
meshes=[assets.load_asset(p) for p in paths if isinstance(assets.load_asset(p),u.StaticMesh)]
assert len(meshes)==1,paths
m=meshes[0]
settings=m.get_editor_property('nanite_settings')
settings.set_editor_property('enabled',True)
u.get_editor_subsystem(u.StaticMeshEditorSubsystem).set_nanite_settings(m,settings,True)
assert assets.save_loaded_asset(m)
report=dict(index=index,name=name,mesh=m.get_path_name(),objects=paths,materials=[s.material_interface.get_path_name() if s.material_interface else None for s in m.static_materials],bounds=str(m.get_bounds()),nanite_enabled=m.get_editor_property('nanite_settings').enabled)
(OUT/('ue-import-%02d.json'%(index+1))).write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('REALISTIC_MOUNTAIN_IMPORTED '+name)
