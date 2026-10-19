import unreal, json
from pathlib import Path
names = ['EditorLevelLibrary','EditorActorSubsystem','EditorAssetSubsystem','AssetImportTask','FbxImportUI','ObjImportFactory','MaterialEditingLibrary','AutomationLibrary','MeshDescription','StaticMeshDescription','GeometryScriptLibrary_StaticMeshFunctions','InputSettings','EditorLoadingAndSavingUtils']
result = {n: hasattr(unreal,n) for n in names}
result['engine'] = unreal.SystemLibrary.get_engine_version()
(Path(__file__).resolve().parents[1] / 'Tools/probe.json').write_text(json.dumps(result,indent=2))
unreal.log('TIANNANGE_PROBE_OK '+json.dumps(result))
