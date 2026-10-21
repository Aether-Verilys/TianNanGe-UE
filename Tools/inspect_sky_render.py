import unreal as u,json,time
from pathlib import Path
root=Path(__file__).resolve().parents[1];actors=u.get_editor_subsystem(u.EditorActorSubsystem);world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
sky=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Lookdev Chaotic winter sky 04')
mat=u.load_asset('/Game/TianNanGe/EasySnowIntegration/Skies/M_Chaotic_WinterSky')
d={}
for k in ['blend_mode','shading_model','is_sky','apply_fogging','apply_cloud_fogging','disable_depth_test']:
    try:d[k]=str(mat.get_editor_property(k))
    except Exception:pass
t=u.load_asset('/Game/Chaotic_Skies_II/Textures/Skies/T_chaotic_sky_II_04');d['texture_size']=[t.blueprint_get_size_x(),t.blueprint_get_size_y()]
(root/'Saved/ChaoticSkies/render-properties.json').write_text(json.dumps(d,indent=2))
settings=next(a for a in actors.get_all_level_actors() if isinstance(a,u.PostProcessVolume)).get_editor_property('settings')
items=[]
for yaw in [0,90,180,270]:
    capture=actors.spawn_actor_from_class(u.SceneCapture2D,u.Vector(0,0,0),u.Rotator(pitch=20,yaw=yaw,roll=0),transient=True)
    c=capture.get_component_by_class(u.SceneCaptureComponent2D)
    rt=u.RenderingLibrary.create_render_target2d(world,640,400,u.TextureRenderTargetFormat.RTF_RGBA8)
    c.set_editor_property('texture_target',rt);c.set_editor_property('capture_source',u.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    c.set_editor_property('capture_every_frame',False);c.set_editor_property('fov_angle',100.)
    c.set_editor_property('post_process_settings',settings);c.set_editor_property('post_process_blend_weight',1.)
    c.set_editor_property('primitive_render_mode',u.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST);c.show_only_actor_components(sky)
    items.append((capture,c,rt,yaw))
state={'start':time.time(),'stage':0,'handle':None}
def tick(dt):
    elapsed=time.time()-state['start']
    if elapsed>3 and state['stage']==0:
        state['stage']=1
        for a,c,rt,yaw in items:c.capture_scene()
    elif elapsed>6 and state['stage']==1:
        state['stage']=2
        for a,c,rt,yaw in items:
            u.RenderingLibrary.export_render_target(world,rt,str(root/'Saved/ChaoticSkies'),'sky-yaw-'+str(yaw)+'.png');actors.destroy_actor(a)
        u.unregister_slate_post_tick_callback(state['handle'])
state['handle']=u.register_slate_post_tick_callback(tick)
