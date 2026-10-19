"""Transient two-shot comparison. Restores intensity and never saves the map."""
import unreal as u,time,json,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Captures/DirectLightDiagnosis';OUT.mkdir(exist_ok=True)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
light=next(a for a in actors.get_all_level_actors() if isinstance(a,u.DirectionalLight) and a.get_actor_label()=='DirectionalLight')
lc=light.get_component_by_class(u.DirectionalLightComponent)
original=float(lc.get_editor_property('intensity'));test=35000.0
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
settings=next(a for a in actors.get_all_level_actors() if isinstance(a,u.PostProcessVolume)).get_editor_property('settings')
captures=[]
for index in range(2):
    a=actors.spawn_actor_from_class(u.SceneCapture2D,camera.get_actor_location(),camera.get_actor_rotation(),transient=True)
    c=a.get_component_by_class(u.SceneCaptureComponent2D)
    rt=u.RenderingLibrary.create_render_target2d(world,1280,620,u.TextureRenderTargetFormat.RTF_RGBA8)
    for key,value in dict(texture_target=rt,capture_source=u.SceneCaptureSource.SCS_FINAL_COLOR_LDR,fov_angle=camera.camera_component.field_of_view,capture_every_frame=False,always_persist_rendering_state=True,post_process_settings=settings,post_process_blend_weight=1.0).items():c.set_editor_property(key,value)
    captures.append((a,c,rt))
state={'start':time.time(),'stage':0,'handle':None,'changed':False}
report={'baseline_lux':original,'test_lux':test,'saved_map':False,'light_rotation':str(light.get_actor_rotation()),'camera':str(camera.get_actor_location())}
def finish():
    if state['changed']:
        current=float(lc.get_editor_property('intensity'))
        if current==test:
            lc.set_intensity(original);report['restored_original_intensity']=True
        else:report['restored_original_intensity']=False;report['concurrent_user_value_preserved']=current
    for a,c,rt in captures:actors.destroy_actor(a)
    report['final_lux']=float(lc.get_editor_property('intensity'))
    (OUT/'response-test.json').write_text(json.dumps(report,indent=2))
    u.unregister_slate_post_tick_callback(state['handle'])
def tick(dt):
    elapsed=time.time()-state['start']
    try:
        if state['stage']==0 and elapsed>2:
            report['baseline_lux']=float(lc.get_editor_property('intensity'));state['stage']=1;captures[0][1].capture_scene()
        elif state['stage']==1 and elapsed>4:
            u.RenderingLibrary.export_render_target(world,captures[0][2],str(OUT),'Current_10lux.png')
            if float(lc.get_editor_property('intensity'))!=original:
                report['aborted']='Light changed during baseline; preserved user edit';finish();return
            lc.set_intensity(test);state['changed']=True;state['stage']=2
        elif state['stage']==2 and elapsed>6:
            state['stage']=3;captures[1][1].capture_scene()
        elif state['stage']==3 and elapsed>8:
            u.RenderingLibrary.export_render_target(world,captures[1][2],str(OUT),'Test_35000lux.png');finish()
    except Exception:report['error']=traceback.format_exc();finish()
state['handle']=u.register_slate_post_tick_callback(tick)
