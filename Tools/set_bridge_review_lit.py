import unreal as u,json
from pathlib import Path
p=(Path(__file__).resolve().parents[1] / 'Tools/Live/bridge-review-viewmode.json')
if not p.exists():p.write_text(json.dumps({'mode':str(u.AutomationLibrary.get_editor_active_viewport_view_mode())}))
u.AutomationLibrary.set_editor_active_viewport_view_mode(u.ViewModeIndex.VMI_LIT)
u.get_editor_subsystem(u.LevelEditorSubsystem).editor_invalidate_viewports()
