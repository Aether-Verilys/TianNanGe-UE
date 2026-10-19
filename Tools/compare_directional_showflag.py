"""Compare per-capture directional-light visibility without touching any live light."""
import unreal as u,time,json,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'Captures/DirectLightDiagnosis'
actors=u.get_editor_subsystem(u.EditorActorSubsystem);world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
settings=next(a for a in actors.get_all_level_actors() if isinstance(a,u.PostProcessVolume)).get_editor_property('settings')
items=[]
for enabled in (False,True):
    actor=actors.spawn_actor_from_class(u.SceneCapture2D,camera.get_actor_location(),camera.get_actor_rotation(),transient=True)
    c=actor.get_component_by_class(u.SceneCaptureComponent2D)
    target=u.RenderingLibrary.create_render_target2d(world,1280,620,u.TextureRenderTargetFormat.RTF_RGBA8)
    flag=u.EngineShowFlagsSetting();flag.set_editor_property('show_flag_name','DirectionalLights');flag.set_editor_property('enabled',enabled)
    for key,value in dict(texture_target=target,capture_source=u.SceneCaptureSource.SCS_FINAL_COLOR_LDR,fov_angle=camera.camera_component.field_of_view,capture_every_frame=False,always_persist_rendering_state=True,post_process_settings=settings,post_process_blend_weight=1.0,show_flag_settings=[flag]).items():c.set_editor_property(key,value)
    items.append((actor,c,target,enabled))
state={'start':time.time(),'stage':0,'handle':None}
report={'live_lights_modified':False,'saved_map':False,'method':'Same-frame separate captures; DirectionalLights show flag off/on'}
def tick(dt):
    try:
        if state['stage']==0 and time.time()-state['start']>2:
            state['stage']=1
            report['lights_at_capture']={a.get_actor_label():a.get_component_by_class(u.DirectionalLightComponent).get_editor_property('intensity') for a in actors.get_all_level_actors() if isinstance(a,u.DirectionalLight)}
            for a,c,rt,enabled in items:c.capture_scene()
        elif state['stage']==1 and time.time()-state['start']>5:
            state['stage']=2
            for a,c,rt,enabled in items:u.RenderingLibrary.export_render_target(world,rt,str(OUT),'Directional_'+('ON' if enabled else 'OFF')+'.png')
            (OUT/'showflag-comparison.json').write_text(json.dumps(report,indent=2))
            for a,c,rt,enabled in items:actors.destroy_actor(a)
            u.unregister_slate_post_tick_callback(state['handle'])
    except Exception:
        report['error']=traceback.format_exc();(OUT/'showflag-comparison.json').write_text(json.dumps(report,indent=2))
        for a,c,rt,enabled in items:actors.destroy_actor(a)
        u.unregister_slate_post_tick_callback(state['handle'])
state['handle']=u.register_slate_post_tick_callback(tick)
