"""Render a transient scene capture at the saved camera; do not move the viewport."""
import unreal as u, time, json, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Captures/RealisticMountains';OUT.mkdir(parents=True,exist_ok=True)
tag=globals().get('COMMAND',{}).get('tag','mountains-before')
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
capture=actors.spawn_actor_from_class(u.SceneCapture2D,camera.get_actor_location(),camera.get_actor_rotation(),transient=True)
c=capture.get_component_by_class(u.SceneCaptureComponent2D)
target=u.RenderingLibrary.create_render_target2d(world,1600,774,u.TextureRenderTargetFormat.RTF_RGBA8)
c.set_editor_property('texture_target',target)
c.set_editor_property('capture_source',u.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
c.set_editor_property('fov_angle',camera.camera_component.field_of_view)
c.set_editor_property('capture_every_frame',False)
c.set_editor_property('always_persist_rendering_state',True)
pp=next((a for a in actors.get_all_level_actors() if isinstance(a,u.PostProcessVolume)),None)
if pp:
    c.set_editor_property('post_process_settings',pp.get_editor_property('settings'))
    c.set_editor_property('post_process_blend_weight',1.0)
state={'start':time.time(),'frames':0,'handle':None}
def tick(dt):
    try:
        c.capture_scene();state['frames']+=1
        if state['frames']>=16:
            u.RenderingLibrary.export_render_target(world,target,str(OUT),tag+'.png')
            actors.destroy_actor(capture)
            u.unregister_slate_post_tick_callback(state['handle'])
    except Exception:
        (OUT/(tag+'-error.txt')).write_text(traceback.format_exc())
        actors.destroy_actor(capture);u.unregister_slate_post_tick_callback(state['handle'])
state['handle']=u.register_slate_post_tick_callback(tick)
