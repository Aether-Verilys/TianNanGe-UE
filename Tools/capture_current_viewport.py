"""Read and screenshot the user's viewport without moving it or saving the level."""
import unreal as u,json,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Captures/DirectLightDiagnosis'
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
key=level.get_active_viewport_config_key()
report={'viewport_key':str(key),'game_view':level.editor_get_game_view(),'saved_map':False}
for name in ['get_level_viewport_camera_info','get_level_viewport_fov']:
    try:report[name]=str(getattr(level,name)(key))
    except Exception as error:report[name]=str(error)
(OUT/'viewport-state.json').write_text(json.dumps(report,indent=2))
state={'task':None,'handle':None,'started':time.time()}
state['task']=u.AutomationLibrary.take_high_res_screenshot(1280,620,str(OUT/'Current_Editor_Viewport.png'),camera=None,force_game_view=False)
def tick(dt):
    level.editor_invalidate_viewports()
    if time.time()-state['started']>20:u.unregister_slate_post_tick_callback(state['handle'])
state['handle']=u.register_slate_post_tick_callback(tick)
