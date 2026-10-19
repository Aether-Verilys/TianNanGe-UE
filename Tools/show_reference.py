import unreal as u
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
u.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
level.pilot_level_actor(camera);level.set_exact_camera_view(True);level.editor_set_viewport_realtime(True);level.editor_set_game_view(True)
actors.set_selected_level_actors([])
