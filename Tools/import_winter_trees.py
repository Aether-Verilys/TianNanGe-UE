import unreal as u, json, traceback
from pathlib import Path
root=Path(__file__).resolve().parents[1]; src=root/'SourceAssets/LowPolyWinterPlants'; assets=u.get_editor_subsystem(u.EditorAssetSubsystem); tools=u.AssetToolsHelpers.get_asset_tools(); result=[]
for name in ['SM_LowPoly_DeadTree_Short_01','SM_LowPoly_DeadTree_Tall_01']:
    dest='/Game/TianNanGe/WinterPlants/'+name
    task=u.AssetImportTask()
    for k,v in dict(filename=str(src/(name+'.glb')),destination_path=dest,destination_name=name,automated=True,replace_existing=False,save=True).items():task.set_editor_property(k,v)
    tools.import_asset_tasks([task])
    paths=list(task.get_editor_property('imported_object_paths'))
    meshes=[assets.load_asset(p) for p in paths if isinstance(assets.load_asset(p),u.StaticMesh)]
    assert len(meshes)==1,(name,paths)
    mesh=meshes[0]; result.append({'name':name,'mesh':mesh.get_path_name(),'objects':paths,'bounds':str(mesh.get_bounds()),'materials':[x.material_interface.get_path_name() if x.material_interface else None for x in mesh.static_materials]})
(src/'ue-tree-import.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
