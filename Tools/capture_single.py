import unreal as u,time,json,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];command=globals().get('COMMAND',{})
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
capture=actors.spawn_actor_from_class(u.SceneCapture2D,camera.get_actor_location(),camera.get_actor_rotation(),transient=True)
c=capture.get_component_by_class(u.SceneCaptureComponent2D)
target=u.RenderingLibrary.create_render_target2d(world,command.get('width',1600),command.get('height',774),u.TextureRenderTargetFormat.RTF_RGBA8)
for key,value in dict(texture_target=target,capture_source=u.SceneCaptureSource.SCS_FINAL_COLOR_LDR,fov_angle=camera.camera_component.field_of_view,capture_every_frame=False,always_persist_rendering_state=True).items():c.set_editor_property(key,value)
settings=next(a for a in actors.get_all_level_actors() if isinstance(a,u.PostProcessVolume)).get_editor_property('settings')
c.set_editor_property('post_process_settings',settings);c.set_editor_property('post_process_blend_weight',1.0)
state={'time':time.time(),'stage':0,'handle':None}
def tick(dt):
    if state['stage']==0 and time.time()-state['time']>5:
        state['stage']=1;c.capture_scene()
    elif state['stage']==1 and time.time()-state['time']>10:
        try:u.RenderingLibrary.export_render_target(world,target,str(ROOT/'Captures/ReferenceLook'),command.get('tag','Look_single')+'.png')
        except Exception:(ROOT/'Tools/Live/single-error.txt').write_text(traceback.format_exc())
        finally:actors.destroy_actor(capture);u.unregister_slate_post_tick_callback(state['handle'])
state['handle']=u.register_slate_post_tick_callback(tick)
