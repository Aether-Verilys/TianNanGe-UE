"""Restore the user's reference light transform; keep EasySnow independent of light direction."""
import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/' in world.get_path_name()
baseline=json.loads((root/'Tools/Baselines/bridge-actors-before.json').read_text())
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors();out=[]
for d in baseline:
    if d['class_name']!='DirectionalLight':continue
    a=next(a for a in actors if isinstance(a,u.DirectionalLight) and a.get_name()==d['path'].rsplit('.',1)[-1])
    before=a.get_actor_rotation();pitch,yaw,roll=d['rotation'];a.modify()
    assert a.set_actor_rotation(u.Rotator(pitch=pitch,yaw=yaw,roll=roll),False)
    actual=a.get_actor_rotation()
    assert max(abs(actual.pitch-pitch),abs(actual.yaw-yaw),abs(actual.roll-roll))<.00001
    out.append({'light':a.get_actor_label(),'before':[before.pitch,before.yaw,before.roll],'restored':[actual.pitch,actual.yaw,actual.roll]})
assert out
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(root/'Saved/EasySnow/restored-sun-direction.json').write_text(json.dumps(out,indent=2))
