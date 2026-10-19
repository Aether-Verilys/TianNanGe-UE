"""Warm Lumen/temporal history and export an actual UE camera render."""
import unreal as u,json,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
command=globals().get('COMMAND',{})
tag=command.get('tag','Look_v01');width=command.get('width',1600);height=command.get('height',774)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
u.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
capture=actors.spawn_actor_from_class(u.SceneCapture2D,camera.get_actor_location(),camera.get_actor_rotation(),transient=True)
component=capture.get_component_by_class(u.SceneCaptureComponent2D)
target=u.RenderingLibrary.create_render_target2d(world,width,height,u.TextureRenderTargetFormat.RTF_RGBA8)
for key,value in dict(texture_target=target,capture_source=u.SceneCaptureSource.SCS_FINAL_COLOR_LDR,fov_angle=camera.camera_component.field_of_view,capture_every_frame=True,always_persist_rendering_state=True).items():component.set_editor_property(key,value)
settings=next(a for a in actors.get_all_level_actors() if isinstance(a,u.PostProcessVolume) and a.get_actor_label().startswith('Lookdev')).get_editor_property('settings')
component.set_editor_property('post_process_settings',settings);component.set_editor_property('post_process_blend_weight',1.0)
u.SystemLibrary.execute_console_command(world,'r.Streaming.PoolSize 4096')
u.SystemLibrary.execute_console_command(world,'r.Shadow.Virtual.Enable 1')
state={'start':time.time(),'frames':0,'handle':None}
output=ROOT/'Captures/ReferenceLook';output.mkdir(exist_ok=True)
def tick(dt):
    state['frames']+=1
    if state['frames']<90 or time.time()-state['start']<20:return
    try:
        u.RenderingLibrary.export_render_target(world,target,str(output),tag+'.png')
        (output/(tag+'.json')).write_text(json.dumps({'width':width,'height':height,'frames':state['frames'],'warmup_seconds':time.time()-state['start'],'camera_location':str(camera.get_actor_location()),'camera_rotation':str(camera.get_actor_rotation()),'horizontal_fov':camera.camera_component.field_of_view,'engine':u.SystemLibrary.get_engine_version(),'source':'UE SceneCapture2D FinalColorLDR; no external compositing'},indent=2))
        u.log('TIANNANGE_CAPTURE_OK '+tag)
    except Exception:(output/(tag+'-error.txt')).write_text(traceback.format_exc())
    finally:
        actors.destroy_actor(capture);u.unregister_slate_post_tick_callback(state['handle'])
state['handle']=u.register_slate_post_tick_callback(tick)
