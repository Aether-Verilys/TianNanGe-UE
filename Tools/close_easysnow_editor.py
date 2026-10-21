import unreal as u
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/TianNanGe/EasySnowIntegration/Maps/')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.SystemLibrary.quit_editor()
