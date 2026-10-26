"""Replace the background with a locally supplied Chaotic Skies II sky, keeping lighting/weather intact."""
import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];assets=u.get_editor_subsystem(u.EditorAssetSubsystem);mel=u.MaterialEditingLibrary
actors=u.get_editor_subsystem(u.EditorActorSubsystem);all_actors=actors.get_all_level_actors()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/' in world.get_path_name()
command=globals().get('COMMAND',{});brightness=command.get('brightness',5000.);yaw=command.get('yaw',-75.)
def preserved():
    out=[]
    for a in all_actors:
        if isinstance(a,(u.DirectionalLight,u.SkyLight,u.PostProcessVolume)):
            r=a.get_actor_rotation();d={'name':a.get_name(),'rotation':[r.pitch,r.yaw,r.roll]}
            if isinstance(a,u.DirectionalLight):
                c=a.get_component_by_class(u.DirectionalLightComponent);col=c.light_color
                d.update(intensity=c.intensity,color=[col.r,col.g,col.b,col.a],angle=c.get_editor_property('light_source_angle'))
            elif isinstance(a,u.SkyLight):
                c=a.get_component_by_class(u.SkyLightComponent);d.update(intensity=c.intensity,cubemap=str(c.get_editor_property('cubemap').get_path_name()),source_angle=c.get_editor_property('source_cubemap_angle'),real_time_capture=c.get_editor_property('real_time_capture'))
            else:d['exposure_bias']=a.get_editor_property('settings').get_editor_property('auto_exposure_bias')
            out.append(d)
        elif str(a.get_folder_path()) in ['EasySnow/Weather','EasySnow/Weather Layers']:
            out.append({'name':a.get_name(),'settings':{k:a.get_editor_property(k) for k in ['spawnRate -','Collision','windStrength -','snowAmount','NearParticleSizeMin -','NearParticleSizeMax -','DriftingSnowAmount -','driftOpacity -']}})
    return out
before=preserved();dest='/Game/TianNanGe/EasySnowIntegration/Skies'
parent_path=dest+'/M_Chaotic_WinterSky'
parent=assets.load_asset(parent_path) if assets.does_asset_exist(parent_path) else assets.duplicate_asset('/Game/Chaotic_Skies_II/Materials/Main_Materials/M_Flowmap_Main',parent_path)
assert parent
parent.set_editor_property('is_sky',False);parent.set_editor_property('two_sided',True)
# Preserve the user's dense volumetric haze on geometry. A depth-tested,
# unlit translucent background draws behind it without fogging the painting.
parent.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT)
parent.set_editor_property('use_translucency_vertex_fog',False)
parent.set_editor_property('apply_cloud_fogging',False)
parent.set_editor_property('translucency_pass',u.MaterialTranslucencyPass.MTP_BEFORE_DOF)
opacity=next((e for e in mel.get_material_expressions(parent) if isinstance(e,u.MaterialExpressionConstant) and e.get_editor_property('desc')=='Sky background opacity'),None)
opacity=opacity or mel.create_material_expression(parent,u.MaterialExpressionConstant,500,500)
opacity.set_editor_property('r',1.);opacity.set_editor_property('desc','Sky background opacity')
assert mel.connect_material_property(opacity,'',u.MaterialProperty.MP_OPACITY)
mel.recompile_material(parent);assets.save_loaded_asset(parent)
mi_path=dest+'/MI_Chaotic_WinterSky_04'
mi=assets.load_asset(mi_path) if assets.does_asset_exist(mi_path) else u.AssetToolsHelpers.get_asset_tools().create_asset('MI_Chaotic_WinterSky_04',dest,u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
mel.set_material_instance_parent(mi,parent)
source=u.load_asset('/Game/Chaotic_Skies_II/Materials/Instances/MI_Flowmap_Inst_04')
for key in mel.get_texture_parameter_names(source):
    texture=mel.get_material_instance_texture_parameter_value(source,key)
    assert texture
    mel.set_material_instance_texture_parameter_value(mi,key,texture)
    assert mel.get_material_instance_texture_parameter_value(mi,key)==texture
    if str(key)=='SkyTexture':
        # The sphere folds V at its equator. Keep U wrapping for rotation, but
        # reflect vertical flow offsets instead of sampling the opposite pole.
        texture.set_editor_property('address_y',u.TextureAddress.TA_MIRROR)
        assert assets.save_loaded_asset(texture)
for key,val in {'Brightness':brightness,'Contrast':.95,'Speed':.004,'NoiseStrength':.04}.items():
    mel.set_material_instance_scalar_parameter_value(mi,key,val)
    assert abs(mel.get_material_instance_scalar_parameter_value(mi,key)-val)<.0001
mel.set_material_instance_vector_parameter_value(mi,'Tint',u.LinearColor(.76,.88,1.,1))
mel.update_material_instance(mi);assets.save_loaded_asset(mi)
sky=next(a for a in all_actors if a.get_actor_label() in ['Lookdev Winter sky','Lookdev Chaotic winter sky 04'])
c=sky.static_mesh_component;mesh=u.load_asset('/Game/Chaotic_Skies_II/Meshes/SM_Skybox_Mesh');assert mesh
old={'mesh':c.static_mesh.get_path_name(),'materials':[m.get_path_name() for m in c.get_materials()],'scale':str(sky.get_actor_scale3d()),'rotation':str(sky.get_actor_rotation())}
sky.modify();c.set_static_mesh(mesh);c.set_material(0,mi);sky.set_actor_label('Lookdev Chaotic winter sky 04')
sky.set_is_temporarily_hidden_in_editor(False);sky.set_actor_hidden_in_game(False)
c.set_visibility(True);c.set_hidden_in_game(False)
assert not sky.is_hidden_ed(),'Sky remains hidden in an editor layer'
camera=next(a for a in all_actors if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
scene_radius=0.
for a in all_actors:
    if isinstance(a,u.StaticMeshActor) and a!=sky and a.static_mesh_component.get_editor_property('visible'):
        origin,extent=a.get_actor_bounds(False)
        scene_radius=max(scene_radius,(origin-camera.get_actor_location()).length()+extent.length())
cutoff=max(100000.,scene_radius*1.25);sky_radius=cutoff*2.
scale=sky_radius/mesh.get_bounds().box_extent.x;sky.set_actor_scale3d(u.Vector(scale,scale,scale));sky.set_actor_rotation(u.Rotator(pitch=0.,yaw=yaw,roll=0.),False)
c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
c.set_editor_property('translucency_sort_priority',-100)
for key in ['cast_shadow','affect_distance_field_lighting','affect_dynamic_indirect_lighting']:c.set_editor_property(key,False)
fog_changes=[]
for a in all_actors:
    if isinstance(a,u.ExponentialHeightFog):
        fc=a.get_component_by_class(u.ExponentialHeightFogComponent)
        old_cutoff=fc.get_editor_property('fog_cutoff_distance');a.modify();fc.set_fog_cutoff_distance(0.)
        fog_changes.append({'actor':a.get_name(),'previous_cutoff_cm':old_cutoff,'restored_cutoff_cm':0.,'density_unchanged':fc.get_editor_property('fog_density')})
after=preserved();assert before==after,'Sky replacement changed lighting or snow'
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
report={'sky':sky.get_path_name(),'mesh':mesh.get_path_name(),'material':mi.get_path_name(),'texture':mel.get_material_instance_texture_parameter_value(mi,'SkyTexture').get_path_name(),'brightness':brightness,'yaw':yaw,'old_sky':old,'lighting_and_weather_preserved':True,'preserved_state':before,'fog_cutoff':fog_changes,'sky_radius_cm':sky_radius,'visible_scene_radius_cm':scene_radius}
(root/'Saved/ChaoticSkies/installed.json').write_text(json.dumps(report,indent=2))
