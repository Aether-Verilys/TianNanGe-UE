"""Load migrated map and capture rendered frames using native editor automation."""
import unreal as u,time,json,traceback
from pathlib import Path
root=Path(__file__).resolve().parents[1]
root.joinpath('Captures').mkdir(exist_ok=True)
u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/TianNanGe/Maps/TianNanGe_Main')
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor))
u.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
u.EditorLevelLibrary.pilot_level_actor(camera)
started=time.time()
stage=0
task=None
handle=None
def tick(dt):
    global stage,task,handle
    try:
        elapsed=time.time()-started
        if stage==0 and elapsed>20:
            stage=1
            # Keep the exposure pass active: the volume already uses fixed manual EV.
            u.SystemLibrary.execute_console_command(None,'r.EyeAdaptationQuality 2')
            task=u.AutomationLibrary.take_high_res_screenshot(1280,620,str(root/'Captures/UE58_Main.png'),camera=camera,delay=2.0)
        elif stage==1 and (((root/'Captures/UE58_Main.png').exists() and (root/'Captures/UE58_Main.png').stat().st_mtime>=started) or elapsed>160):
            (root/'Captures/capture-result.json').write_text(json.dumps({'engine':u.SystemLibrary.get_engine_version(),'actors':len(actors.get_all_level_actors()),'camera_location':str(camera.get_actor_location()),'camera_rotation':str(camera.get_actor_rotation()),'screenshot_exists':(root/'Captures/UE58_Main.png').exists()},indent=2))
            u.unregister_slate_post_tick_callback(handle)
    except Exception:
        (root/'Captures/capture-error.txt').write_text(traceback.format_exc());u.unregister_slate_post_tick_callback(handle)
handle=u.register_slate_post_tick_callback(tick)
