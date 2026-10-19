import unreal as u,json
from pathlib import Path
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
data={'level_methods':[x for x in dir(level) if 'view' in x.lower()], 'automation':[x for x in dir(u.AutomationLibrary) if 'view' in x.lower()], 'viewmodes':str(list(u.ViewModeIndex)), 'editor_library':[x for x in dir(u.EditorLevelLibrary) if 'exec' in x.lower() or 'view' in x.lower()], 'console':u.SystemLibrary.execute_console_command.__doc__}
data.update(current=str(u.AutomationLibrary.get_editor_active_viewport_view_mode()),setter=u.AutomationLibrary.set_editor_active_viewport_view_mode.__doc__)
((Path(__file__).resolve().parents[1] / 'Tools/Live')/'viewmode-api.json').write_text(json.dumps(data,indent=2))
