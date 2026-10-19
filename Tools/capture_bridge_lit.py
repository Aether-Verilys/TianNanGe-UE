import unreal as u,time,json,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];command=globals().get('COMMAND',{})
actors=u.get_editor_subsystem(u.EditorActorSubsystem);level=u.get_editor_subsystem(u.LevelEditorSubsystem)
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
mode=u.AutomationLibrary.get_editor_active_viewport_view_mode()
u.AutomationLibrary.set_editor_active_viewport_view_mode(u.ViewModeIndex.VMI_LIT)
level.pilot_level_actor(camera);level.editor_set_game_view(True);level.editor_set_viewport_realtime(True)
state={'time':time.time(),'requested':False,'task':None,'handle':None}
def tick(dt):
    level.editor_invalidate_viewports();elapsed=time.time()-state['time']
    if elapsed>8 and not state['requested']:
        state['requested']=True
        try:
            state['task']=u.AutomationLibrary.take_high_res_screenshot(command.get('width',1600),command.get('height',774),str(ROOT/'Captures/ReferenceLook'/(command.get('tag','Bridge_Curved_Lit')+'.png')),camera=camera,delay=0)
            level.save_current_level()
        except Exception:(ROOT/'Tools/Live/bridge-capture-error.txt').write_text(traceback.format_exc())
    if elapsed>28:
        u.AutomationLibrary.set_editor_active_viewport_view_mode(mode)
        level.pilot_level_actor(camera)
        u.unregister_slate_post_tick_callback(state['handle'])
state['handle']=u.register_slate_post_tick_callback(tick)
