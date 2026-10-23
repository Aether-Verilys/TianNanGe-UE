"""One-time Blueprint generation; build Tools/CloudBlueprintBuilder first.

RunUAT.bat BuildPlugin -Plugin=<project>/Tools/CloudBlueprintBuilder/CloudBlueprintBuilder.uplugin
    -Package=<project>/Saved/CloudBlueprintBuilder -NoTargetPlatforms
Then dispatch this script inside UE 5.8. The generated asset is standalone.
"""
import ctypes, datetime, json, runpy, shutil
from pathlib import Path
import unreal as u
r=Path(__file__).resolve().parents[1]
path='/Game/TianNanGe/CloudSea/Blueprints/BP_CloudSeaController'
assert not u.load_asset(path), 'Existing Blueprint preserved; do not regenerate over user edits.'
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/TianNanGe_EasySnow.' in world.get_path_name()
backup=r/'Backups'/('CloudBlueprint_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir()
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
shutil.copy2(r/'Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap',backup/'TianNanGe_EasySnow.umap')
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
(r/'Saved/cloud-blueprint-before.json').write_text(json.dumps({'backup':str(backup),'transforms':{a.get_path_name():a.get_actor_transform().export_text() for a in actors}}))
dll=r/'Saved/CloudBlueprintBuilder/Binaries/Win64/UnrealEditor-CloudBlueprintBuilder.dll'
u._cloud_builder=ctypes.CDLL(str(dll))  # Keep loaded for the editor lifetime.
assert u._cloud_builder.BuildCloudController()==0
runpy.run_path(str(r/'Tools/install_cloud_blueprint.py'),run_name='__main__')
