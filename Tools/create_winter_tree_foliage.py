import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]; src=root/'SourceAssets/LowPolyWinterPlants'; report=json.loads((src/'ue-tree-import.json').read_text(encoding='utf-8')); assets=u.get_editor_subsystem(u.EditorAssetSubsystem); tools=u.AssetToolsHelpers.get_asset_tools(); out=[]
for entry in report:
    mesh=assets.load_asset(entry['mesh']); name=entry['name'].replace('SM_','FT_',1); path='/Game/TianNanGe/WinterPlants/Foliage/'+name
    ft=assets.load_asset(path)
    if not ft: ft=tools.create_asset(name,'/Game/TianNanGe/WinterPlants/Foliage',u.FoliageType_InstancedStaticMesh,u.FoliageType_InstancedStaticMeshFactory())
    assert ft
    ft.set_editor_property('mesh',mesh); ft.set_editor_property('align_to_normal',False); ft.set_editor_property('random_yaw',True)
    assert assets.save_loaded_asset(ft)
    out.append({'foliage':ft.get_path_name(),'mesh':ft.get_editor_property('mesh').get_path_name(),'align_to_normal':ft.get_editor_property('align_to_normal'),'random_yaw':ft.get_editor_property('random_yaw')})
(src/'ue-foliage-types.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
