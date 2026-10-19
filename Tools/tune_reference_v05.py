import unreal as u,json,math,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
runpy.run_path(str(ROOT/'Tools/align_reference.py'),run_name='__main__')
character=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='tripo_node_4dee5643')
center,extent=character.get_actor_bounds(False)
feet_offset=7.3-(center.z-extent.z)
for a in actors.get_all_level_actors():
    if a.get_actor_label().startswith('Lookdev Snow detail icicle'):
        a.set_actor_rotation(u.Rotator(roll=180,pitch=0,yaw=0),False)
    if str(a.get_folder_path()).startswith('PlayerArmature/'):
        a.modify();p=a.get_actor_location();p.z+=feet_offset;a.set_actor_location(p,False,False)
    if isinstance(a,u.ExponentialHeightFog):
        c=a.get_component_by_class(u.ExponentialHeightFogComponent)
        c.set_editor_property('fog_density',.16);c.set_editor_property('fog_inscattering_luminance',u.LinearColor(1200,2400,3800))
        c.set_editor_property('directional_inscattering_luminance',u.LinearColor(0,0,0))
    elif a.get_actor_label()=='Lookdev Cool soft fill':a.get_component_by_class(u.DirectionalLightComponent).set_intensity(10000)
    elif a.get_actor_label()=='Lookdev Warm backlight':a.get_component_by_class(u.DirectionalLightComponent).set_intensity(35000)
    elif isinstance(a,u.PostProcessVolume):
        s=a.get_editor_property('settings')
        s.set_editor_property('color_gain_shadows',u.Vector4(.97,1,1.06,1));s.set_editor_property('color_offset_shadows',u.Vector4(.016,.02,.03,0))
        a.set_editor_property('settings',s)
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
u.get_editor_subsystem(u.LevelEditorSubsystem).eject_pilot_level_actor()
camera.modify();camera.set_actor_location(u.Vector(-460,0,88),False,False);camera.set_actor_rotation(u.Rotator(pitch=4.2,yaw=0,roll=0),False)
aspect=4028/1949;fov=math.degrees(2*math.atan(math.tan(math.radians(30.5)/2)*aspect))
camera.camera_component.set_field_of_view(fov);camera.camera_component.set_editor_property('aspect_ratio',aspect)
u.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
u.get_editor_subsystem(u.LevelEditorSubsystem).pilot_level_actor(camera)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(ROOT/'Tools/Live/tuning-v05.json').write_text(json.dumps({'key_lux':35000,'fill_lux':10000,'fog_density':.16,'fog_inscattering_luminance':[1200,2400,3800],'fixed_ev':12,'character_feet_offset_cm':feet_offset,'character_feet_z_cm':7.3,'camera_pitch':4.2,'camera_vertical_fov':30.5,'camera_horizontal_fov':fov,'aspect':aspect},indent=2))
