"""Save the current migrated scene and project assets before a repository snapshot."""
import unreal as u,json,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/TianNanGe/Maps/TianNanGe_ReferenceLook.'),world.get_path_name()
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_directory('/Game/TianNanGe',True,True)
live=root/'Tools/Live';live.mkdir(exist_ok=True)
(live/'repository-save.json').write_text(json.dumps({'world':world.get_path_name(),'saved':True,'time':time.time()},indent=2))
