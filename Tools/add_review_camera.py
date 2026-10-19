import unreal as u
level=u.get_editor_subsystem(u.LevelEditorSubsystem);level.load_level('/Game/TianNanGe/Maps/TianNanGe_Main')
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
for a in actors.get_all_level_actors():
    if isinstance(a,u.CameraActor) and a.get_actor_label()=='Review Overview':actors.destroy_actor(a)
location=u.Vector(-950,-550,550)
rotation=u.MathLibrary.find_look_at_rotation(location,u.Vector(350,0,220))
camera=actors.spawn_actor_from_class(u.CameraActor,location,rotation)
camera.set_actor_label('Review Overview');camera.set_folder_path('Cameras')
camera.camera_component.set_field_of_view(68.0)
camera.camera_component.set_editor_property('aspect_ratio',1280/620)
camera.camera_component.set_editor_property('constrain_aspect_ratio',True)
u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
