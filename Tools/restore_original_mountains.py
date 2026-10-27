"""Restore original mountain visibility and remove only generated replacement actors."""
import unreal as u,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SourceAssets/RealisticMountains/UserGenerated_20261027'
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
originals=json.loads((OUT/'original-visibility.json').read_text())
all_actors=list(actors.get_all_level_actors());by_path={a.get_path_name():a for a in all_actors}
missing=[s['path'] for s in originals if s['path'] not in by_path]
assert not missing,('Original mountain actors were removed by the later scene cleanup. Restore the scene backup in Backups/SceneCleanupNanite_20261027 before using this historical visibility restore.',missing)
with u.ScopedEditorTransaction('Restore original TianNanGe mountains'):
    for s in originals:
        a=by_path[s['path']];a.modify();a.static_mesh_component.modify()
        a.static_mesh_component.set_visibility(s['visible'],True)
        a.set_actor_hidden_in_game(s['hidden_game'])
        a.set_is_temporarily_hidden_in_editor(s['temporary_hidden'])
    for a in all_actors:
        if 'RealisticMountainReplacement_20261027' in [str(t) for t in a.tags]:actors.destroy_actor(a)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
