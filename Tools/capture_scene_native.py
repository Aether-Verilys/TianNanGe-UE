"""Render the migrated scene with an explicit fixed-exposure UE scene capture."""
import unreal as u,time,json,traceback
from pathlib import Path
root=Path(__file__).resolve().parents[1]
root.joinpath('Captures').mkdir(exist_ok=True)
u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/TianNanGe/Maps/TianNanGe_Main')
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
review=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label()=='Review Overview')
u.EditorLevelLibrary.set_level_viewport_camera_info(review.get_actor_location(),review.get_actor_rotation())
u.EditorLevelLibrary.eject_pilot_level_actor()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
capture=actors.spawn_actor_from_class(u.SceneCapture2D,camera.get_actor_location(),camera.get_actor_rotation(),transient=True)
component=capture.get_component_by_class(u.SceneCaptureComponent2D)
target=u.RenderingLibrary.create_render_target2d(world,1280,620,u.TextureRenderTargetFormat.RTF_RGBA8)
component.set_editor_property('texture_target',target)
component.set_editor_property('capture_source',u.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
component.set_editor_property('fov_angle',camera.camera_component.field_of_view)
component.set_editor_property('capture_every_frame',False)
component.set_editor_property('always_persist_rendering_state',True)
settings=next(a for a in actors.get_all_level_actors() if isinstance(a,u.PostProcessVolume)).get_editor_property('settings')
component.set_editor_property('post_process_settings',settings)
component.set_editor_property('post_process_blend_weight',1.0)
u.EditorLevelLibrary.set_level_viewport_camera_info(review.get_actor_location(),review.get_actor_rotation())
started=time.time();stage=0;handle=None
def tick(dt):
    global stage,handle
    try:
        if stage==0 and time.time()-started>15:
            stage=1
            component.capture_scene()
        elif stage==1 and time.time()-started>20:
            stage=2
            u.RenderingLibrary.export_render_target(world,target,str(root/'Captures'),'UE58_Hero.png')
            capture.set_actor_location(review.get_actor_location(),False,False);capture.set_actor_rotation(review.get_actor_rotation(),False)
            component.set_editor_property('fov_angle',review.camera_component.field_of_view)
        elif stage==2 and time.time()-started>25:
            stage=3;component.capture_scene()
        elif stage==3 and time.time()-started>30:
            stage=4
            u.RenderingLibrary.export_render_target(world,target,str(root/'Captures'),'UE58_Overview.png')
        elif stage==4 and time.time()-started>35:
            (root/'Captures/native-capture-result.json').write_text(json.dumps({'engine':u.SystemLibrary.get_engine_version(),'width':1280,'height':620,'source':'SceneCapture2D FinalColorLDR','fixed_ev':12,'actors':len(actors.get_all_level_actors()),'camera':str(camera.get_actor_location())},indent=2))
            actors.destroy_actor(capture)
            u.unregister_slate_post_tick_callback(handle)
    except Exception:
        (root/'Captures/native-capture-error.txt').write_text(traceback.format_exc());u.unregister_slate_post_tick_callback(handle)
handle=u.register_slate_post_tick_callback(tick)
