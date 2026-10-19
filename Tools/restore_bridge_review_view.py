import unreal as u,json
from pathlib import Path
p=(Path(__file__).resolve().parents[1] / 'Tools/Live/bridge-review-viewmode.json')
original=json.loads(p.read_text())['mode']
name=original.split('.')[1].split(':')[0]
u.AutomationLibrary.set_editor_active_viewport_view_mode(getattr(u.ViewModeIndex,name))
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
camera=next(a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
level.pilot_level_actor(camera);level.editor_invalidate_viewports()
