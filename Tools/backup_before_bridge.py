import unreal as u,json,shutil,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
backup=root/'Backups/Bridge_20261019'
backup.mkdir(parents=True,exist_ok=True)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/TianNanGe/Maps/TianNanGe_ReferenceLook.')
src=root/'Content/TianNanGe/Maps/TianNanGe_ReferenceLook.umap'
if not (backup/'ReferenceLook_disk_before.umap').exists():shutil.copy2(src,backup/'ReferenceLook_disk_before.umap')
# Preserve the user's live lighting edits in a complete map backup before changing geometry.
assert level.save_current_level()
shutil.copy2(src,backup/'ReferenceLook_live_before_bridge.umap')
shutil.copy2(root/'Tools/Live/bridge-before.json',backup/'bridge-actors-before.json')
(backup/'backup.json').write_text(json.dumps({'map':world.get_path_name(),'live_saved':True,'timestamp':time.time()},indent=2))
