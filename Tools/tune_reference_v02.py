import unreal as u,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
for a in actors.get_all_level_actors():
    if a.get_actor_label()=='Lookdev Cool soft fill':
        c=a.get_component_by_class(u.DirectionalLightComponent);c.set_intensity(16000);c.set_editor_property('cast_shadows',False)
    elif isinstance(a,u.SkyLight):a.get_component_by_class(u.SkyLightComponent).set_intensity(7000)
    elif isinstance(a,u.ExponentialHeightFog):
        c=a.get_component_by_class(u.ExponentialHeightFogComponent);c.set_editor_property('fog_density',.10);c.set_editor_property('start_distance',450.0)
    elif isinstance(a,u.StaticMeshActor) and str(a.get_folder_path()).endswith('/ExtendedRailings'):
        if (a.get_actor_label().startswith('Post_') or a.get_actor_label().startswith('SnowCap_')) and a.get_actor_location().x<0 and a.get_actor_location().y<0:
            a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
level.editor_set_viewport_realtime(True);level.editor_set_game_view(True)
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
level.eject_pilot_level_actor()
data=json.loads((ROOT/'Transfer_fdf5e67/scene.json').read_text())['camera']
camera.set_actor_location(u.Vector(**data['position']),False,False)
camera.set_actor_rotation(u.MathLibrary.make_rot_from_xz(u.Vector(**data['forward']),u.Vector(**data['up'])),False)
u.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
level.pilot_level_actor(camera);level.set_exact_camera_view(True)
u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
level.save_current_level()
(ROOT/'Tools/Live/tuning-v02.json').write_text(json.dumps({'fill_lux':16000,'sky_strength':7000,'fog_density':.1,'realtime_viewport':True}))
