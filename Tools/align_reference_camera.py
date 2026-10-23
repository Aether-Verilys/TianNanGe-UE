"""Align only the main camera to the painting-calibrated bridge projection."""
import datetime
import json
import shutil
import time
from pathlib import Path
import unreal as u

root=Path(__file__).resolve().parents[1]
api=u.get_editor_subsystem(u.EditorActorSubsystem)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
actors=api.get_all_level_actors()
cameras=[a for a in actors if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera')]
assert len(cameras)==1
camera=cameras[0]; component=camera.get_component_by_class(u.CameraComponent)
key=level.get_active_viewport_config_key()
state_path=root/'Saved/reference-camera-alignment-before.json'
if not globals().get('COMMAND',{}).get('reuse_snapshot',False):
 backup=root/'Backups'/('ReferenceCamera_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
 backup.mkdir()
 assert level.save_current_level()
 shutil.copy2(root/'Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap',backup/'TianNanGe_EasySnow.umap')
 state={'time':time.time(),'backup':str(backup),'camera':camera.get_path_name(),
        'camera_transform':camera.get_actor_transform().export_text(),
        'camera_fov':component.field_of_view,'camera_aspect':component.aspect_ratio,
        'camera_postprocess':component.post_process_settings.export_text(),
        'actors':{a.get_path_name():a.get_actor_transform().export_text() for a in actors},
        'cloud':{}}
 for a in actors:
  if a.get_actor_label()=='Cloud Sea Controls - TianNanGe':
   vol=a.get_editor_property('TargetVolume');mat=vol.get_material(0)
   state['cloud']={str(k):mat.get_scalar_parameter_value(k) for k in u.MaterialEditingLibrary.get_scalar_parameter_names(mat)}
 state_path.write_text(json.dumps(state,indent=2))
state=json.loads(state_path.read_text())
assert state['camera']==camera.get_path_name()
params=globals().get('COMMAND',{})
level.eject_pilot_level_actor(key)
camera.modify();component.modify()
camera.set_actor_location(u.Vector(*params.get('position',[-460.,0.,88.])),False,False)
camera.set_actor_rotation(u.Rotator(pitch=params.get('pitch',4.2),yaw=params.get('yaw',0.),roll=0.),False)
component.set_field_of_view(float(params.get('fov',58.7979375)))
component.set_editor_property('aspect_ratio',4028/1949)
component.set_editor_property('constrain_aspect_ratio',True)
level.pilot_level_actor(camera,key)
level.set_exact_camera_view(True,key)
api.set_selected_level_actors([])
for a in actors:
 if a!=camera:assert a.get_actor_transform().export_text()==state['actors'][a.get_path_name()]
assert component.post_process_settings.export_text()==state['camera_postprocess']
report={'time':time.time(),'camera':camera.get_path_name(),
 'position':camera.get_actor_location().to_tuple(),'rotation':camera.get_actor_rotation().export_text(),
 'fov':component.field_of_view,'aspect':component.aspect_ratio,'other_actor_transforms_preserved':True,
 'postprocess_preserved':True,'backup':state['backup']}
(root/'Saved/reference-camera-alignment-applied.json').write_text(json.dumps(report,indent=2))
u.log('REFERENCE_CAMERA_ALIGNED '+json.dumps(report))
