import unreal as u,time,json,traceback
from pathlib import Path
root=Path(__file__).resolve().parents[1];actors=u.get_editor_subsystem(u.EditorActorSubsystem)
all_actors=actors.get_all_level_actors();world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
position=u.Vector(1050,-1600,350);focus=u.Vector(1050,100,-50)
for old in all_actors:
    if isinstance(old,u.SceneCapture2D) and (old.get_actor_location()-position).length()<.01:actors.destroy_actor(old)
a=actors.spawn_actor_from_class(u.SceneCapture2D,position,u.MathLibrary.find_look_at_rotation(position,focus),transient=True)
a.set_actor_label('Transient Bridge Side QA')
c=a.get_component_by_class(u.SceneCaptureComponent2D)
target=u.RenderingLibrary.create_render_target2d(world,1600,774,u.TextureRenderTargetFormat.RTF_RGBA8)
for k,v in dict(texture_target=target,capture_source=u.SceneCaptureSource.SCS_FINAL_COLOR_LDR,fov_angle=72.,capture_every_frame=False,always_persist_rendering_state=True,primitive_render_mode=u.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST).items():c.set_editor_property(k,v)
visible=[v for v in all_actors if str(v.get_folder_path())=='Reference/Bridge' or str(v.get_folder_path())=='TianNanGe_Blockout/Bridge/FarPavilionStoneStairs' or (str(v.get_folder_path())=='TianNanGe_Blockout/Bridge/BridgeConnections' and v.get_actor_location().x>0) or v.get_actor_label()=='Lookdev Winter sky']
for v in visible:c.show_only_actor_components(v)
c.set_editor_property('post_process_settings',next(v for v in all_actors if isinstance(v,u.PostProcessVolume)).get_editor_property('settings'));c.set_editor_property('post_process_blend_weight',1.)
flags=[]
for name in ['Fog','Atmosphere']:
    f=u.EngineShowFlagsSetting();f.set_editor_property('show_flag_name',name);f.set_editor_property('enabled',False);flags.append(f)
c.set_editor_property('show_flag_settings',flags)
state={'t':time.time(),'stage':0,'handle':None}
def tick(dt):
    elapsed=time.time()-state['t']
    if elapsed>5 and state['stage']==0:state['stage']=1;c.capture_scene()
    if elapsed>10 and state['stage']==1:
        state['stage']=2
        try:u.RenderingLibrary.export_render_target(world,target,str(root/'Captures/ReferenceLook'),'Bridge_RearCurve_Side.png')
        except Exception:(root/'Tools/Live/side-error.txt').write_text(traceback.format_exc())
        finally:actors.destroy_actor(a);u.unregister_slate_post_tick_callback(state['handle'])
state['handle']=u.register_slate_post_tick_callback(tick)
