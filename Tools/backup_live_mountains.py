"""Save and back up the original editor's current scene before replacements."""
import unreal as u, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
backup=ROOT/'Backups/RealisticMountains_20261027/TianNanGe_EasySnow_live.umap'
assert not backup.exists(),'Live backup already exists; preserve it.'
shutil.copy2(ROOT/'Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap',backup)
