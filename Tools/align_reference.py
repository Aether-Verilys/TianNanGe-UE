"""Art-direction transforms based on source positions, so reruns do not accumulate."""
import unreal as u,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'Transfer_fdf5e67/scene.json').read_text())
nodes={n['path']:n for n in data['nodes']}
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
changes=[]
for actor in actors.get_all_level_actors():
    if not isinstance(actor,u.StaticMeshActor):continue
    path=str(actor.get_folder_path())+'/'+actor.get_actor_label()
    node=nodes.get(path)
    if not node:continue
    if path.startswith('PlayerArmature/'):
        actor.modify()
        p=node['position'];angle=math.radians(20);dx=p['x'];dy=p['y']-64.1
        actor.set_actor_location(u.Vector(math.cos(angle)*dx-math.sin(angle)*dy,math.sin(angle)*dx+math.cos(angle)*dy+32,p['z']),False,False)
        r=node['rotation'];rot=u.Quat(r['x'],r['y'],r['z'],r['w']).rotator();rot.yaw+=20
        actor.set_actor_rotation(rot,False);changes.append(actor.get_actor_label())
u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(ROOT/'alignment-result.json').write_text(json.dumps({'character_yaw_adjustment_degrees':20,'character_lateral_offset_cm':-32.1,'actors_adjusted':changes},indent=2))
