import unreal as u,json,math
from pathlib import Path
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
camera=next(a for a in actors if isinstance(a,u.CameraActor))
result={'camera_location':str(camera.get_actor_location()),'camera_rotation':str(camera.get_actor_rotation()),'fov':camera.camera_component.field_of_view,'subjects':{}}
for a in actors:
    if a.get_actor_label() not in ('dragon','tripo_node_4dee5643'):continue
    p,e=a.get_actor_bounds(False)
    local=u.MathLibrary.inverse_transform_location(camera.get_actor_transform(),p)
    tan=math.tan(math.radians(camera.camera_component.field_of_view/2))
    result['subjects'][a.get_actor_label()]={'actor_position':str(a.get_actor_location()),'actor_rotation':str(a.get_actor_rotation()),'bounds_center':str(p),'bounds_extent':str(e),'projected_center':[.5+local.y/local.x/tan/2,.5-local.z/local.x/tan*2.0667/2]}
(Path(__file__).resolve().parents[1] / 'Tools/Live/composition.json').write_text(json.dumps(result,indent=2))
