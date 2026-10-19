"""Preserve source rigs as independent assets; humanoid retargeting is a separate task."""
import unreal as u,json,traceback
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=Path('D:/Dev/TianNanGe/Project_TianNanGe/Assets')
results=[]
for name,path in [('SK_ChineseDragon',source/'ThirdParty/MAXDESIGNChineseDragon/ChineseDragon.fbx'),('SK_LittleGreen',source/'Character/little+green/tripo_convert_4dee5643-20cb-465c-a529-88f2794a3fe2.fbx')]:
    item={'source':str(path),'name':name}
    try:
        if not path.exists() or path.stat().st_size<512:raise RuntimeError('Missing source FBX / LFS pointer')
        options=u.FbxImportUI()
        for k,v in dict(import_mesh=True,import_as_skeletal=True,import_materials=False,import_textures=False,import_animations=True,automated_import_should_detect_type=False,mesh_type_to_import=u.FBXImportType.FBXIT_SKELETAL_MESH).items():options.set_editor_property(k,v)
        task=u.AssetImportTask()
        for k,v in dict(filename=str(path),destination_path='/Game/TianNanGe/Rigs/'+name,destination_name=name,automated=True,replace_existing=False,save=True,options=options).items():task.set_editor_property(k,v)
        u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);item['assets']=list(task.imported_object_paths)
    except Exception:item['error']=traceback.format_exc()
    results.append(item)
(root/'rig-import-result.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
