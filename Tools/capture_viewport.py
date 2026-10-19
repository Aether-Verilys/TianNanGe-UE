import unreal as u,time,json,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
command=globals().get('COMMAND',{})
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
u.get_editor_subsystem(u.LevelEditorSubsystem).pilot_level_actor(camera)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
level.editor_set_game_view(True)
level.editor_set_viewport_realtime(True)
state={'start':time.time(),'handle':None,'task':None,'requested':False}
def tick(dt):
    level.editor_invalidate_viewports()
    if time.time()-state['start']<5:return
    if state['requested']:
        if time.time()-state['start']>35:u.unregister_slate_post_tick_callback(state['handle'])
        return
    try:
        state['requested']=True
        filename=str(ROOT/'Captures/ReferenceLook'/(command.get('tag','Look_viewport')+'.png'))
        state['task']=u.AutomationLibrary.take_high_res_screenshot(command.get('width',1600),command.get('height',774),filename,camera=camera,delay=0.0)
        level.save_current_level()
    except Exception:(ROOT/'Tools/Live/viewport-error.txt').write_text(traceback.format_exc())
    except BaseException:u.unregister_slate_post_tick_callback(state['handle']);raise
state['handle']=u.register_slate_post_tick_callback(tick)
