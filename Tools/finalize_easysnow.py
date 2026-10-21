import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assert '/EasySnowIntegration/Maps/' in u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name()
main=next(a for a in actors.get_all_level_actors() if str(a.get_folder_path())=='EasySnow/Weather')
main.modify();main.set_editor_property('windBuildupOverride',1.);main.call_method('UserConstructionScript')
for c in main.get_components_by_class(u.NiagaraComponent):c.activate(True)
seq=u.load_asset('/Game/TianNanGe/EasySnowIntegration/Preview/LS_EasySnowMotion')
if seq:
    seq.set_playback_end(72)
    for track in seq.get_tracks():
        if isinstance(track,u.MovieSceneCameraCutTrack):
            for section in track.get_sections():section.set_range(0,72)
    u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(seq)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
