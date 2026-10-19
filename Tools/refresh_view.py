import unreal as u,time
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
level.editor_set_viewport_realtime(True)
level.save_current_level()
state={'start':time.time(),'handle':None}
def tick(dt):
    level.editor_invalidate_viewports()
    if time.time()-state['start']>15:u.unregister_slate_post_tick_callback(state['handle'])
state['handle']=u.register_slate_post_tick_callback(tick)
