"""Art direct the local EasySnow trial: wind, near/far snowfall, ground drift, masks and glints."""
import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];dest='/Game/TianNanGe/EasySnowIntegration'
actors=u.get_editor_subsystem(u.EditorActorSubsystem);assets=u.get_editor_subsystem(u.EditorAssetSubsystem);mel=u.MaterialEditingLibrary
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();assert world.get_path_name().startswith(dest+'/Maps/')
report={'features':{},'material_instances':[],'lighting':{}}
all_actors=actors.get_all_level_actors()
main=next(a for a in all_actors if str(a.get_folder_path())=='EasySnow/Weather')
base_values={
 'Preset':None,'Camera-Centric':True,'spawnRate -':2200.,'snowLifetime -':6.,'spawnRadius':1700.,'spawnRadiusHeight':1200.,
 'windDirection':125.,'windStrength -':2.4,'windUpdraftStrength -':.3,'turbulenceIntensity -':.45,'turbulenceFrequency -':.55,
 'snowChaos -':.8,'NearParticleSizeMin -':.18,'NearParticleSizeMax -':.55,'distantParticleSize -':1.4,'distantParticleAlpha':1.4,
 'HighDetailMaxDistance':300.,'MidDetailMaxDistance':1000.,'cameraFadeDistance':100.,'Collision':True,
 'driftsEnable -':False,'Set World Snow Material Settings':True,'windBuildupOverride':1.,'snowAmount':.16,
 'Snow Glimmer Intensity':.015,'World Snow Displacement Multiplier':.5,'breakupIntensity':.6,'breakupTextureTiling':1.25
}
def configure(a,values):
    a.modify()
    for k,v in values.items():a.set_editor_property(k,v)
    a.call_method('UserConstructionScript')
    for c in a.get_components_by_class(u.NiagaraComponent):c.activate(True)
    return {k:str(v) for k,v in values.items()}
report['features']['main_wind_snow']=configure(main,base_values)
cls=main.get_class()
def extra(label,position):
    found=next((a for a in actors.get_all_level_actors() if a.get_actor_label()==label),None)
    a=found or actors.spawn_actor_from_class(cls,u.Vector(*position));a.set_actor_label(label);a.set_folder_path('EasySnow/Weather Layers');return a
drift=extra('EasySnow - Bridge Ground Spindrift',(100,40,60))
drift_values={**base_values,'Camera-Centric':False,'spawnRate -':0.,'Set World Snow Material Settings':False,
 'spawnRadius':1000.,'spawnRadiusHeight':150.,'snowLifetime -':5.,'driftsEnable -':True,'DriftingSnowAmount -':6.,
 'driftOpacity -':.09,'driftsSizeMin -':400.,'driftsSizeMax -':950.,'driftsCameraFadeDistance':140.,
 'Geometry Fading Distance':100.,'toggleDriftGravity -':False,'windUpdraftStrength -':.04,'driftsTextureSpeed':1.0,
 'driftColor':u.LinearColor(.66,.78,.9,1),'driftsEmissive':u.LinearColor(0,0,0,1)}
report['features']['ground_spindrift']=configure(drift,drift_values)
far=extra('EasySnow - Courtyard Distant Flurries',(1500,350,450))
far_values={**base_values,'Camera-Centric':False,'spawnRate -':2400.,'Set World Snow Material Settings':False,
 'spawnRadius':2200.,'spawnRadiusHeight':1300.,'HighDetailMaxDistance':100.,'MidDetailMaxDistance':300.,
 'distantParticleSize -':1.8,'distantParticleAlpha':1.8,'NearParticleSizeMin -':.2,'NearParticleSizeMax -':.6,
 'windStrength -':2.4,'windUpdraftStrength -':.25,'driftsEnable -':False}
report['features']['distant_flurries']=configure(far,far_values)

# Enable a world-space exclusion volume through the package's own material switches.
mask_cls=u.load_class(None,'/Game/EasySnow/Blueprints/BP_EasySnowMask.BP_EasySnowMask_C')
mask=next((a for a in actors.get_all_level_actors() if a.get_actor_label()=='EasySnow Mask - Hero Footing'),None)
mask=mask or actors.spawn_actor_from_class(mask_cls,u.Vector(0,32,85));mask.set_actor_label('EasySnow Mask - Hero Footing');mask.set_folder_path('EasySnow/Masks')
box=mask.get_component_by_class(u.BoxComponent);box.set_box_extent(u.Vector(75,60,105),False)
mask.set_editor_property('customSnowMaskEdgeFalloff',35.);mask.set_editor_property('customSnowMaskBreakupTiling',1.4);mask.set_editor_property('customSnowMaskBreakupContrast',1.5);mask.call_method('UserConstructionScript')
material_map={}
for a in actors.get_all_level_actors():
    if not isinstance(a,u.StaticMeshActor):continue
    for slot,m in enumerate(a.static_mesh_component.get_materials()):
        if not m or not m.get_path_name().startswith(dest+'/Materials/'):continue
        if isinstance(m,u.MaterialInstanceConstant):continue
        if m.get_path_name() not in material_map:
            fn=next((e for e in mel.get_material_expressions(m) if isinstance(e,u.MaterialExpressionMaterialFunctionCall) and e.get_editor_property('material_function') and 'MF_WF_WorldSnow' in e.get_editor_property('material_function').get_name()),None)
            if not fn:continue
            old=mel.get_material_property_input_node(m,u.MaterialProperty.MP_EMISSIVE_COLOR)
            if old is None:assert mel.connect_material_property(fn,'Emissive',u.MaterialProperty.MP_EMISSIVE_COLOR)
            mel.recompile_material(m);assets.save_loaded_asset(m)
            name='MI_'+m.get_name();path=dest+'/Materials/'+name
            mi=assets.load_asset(path) if assets.does_asset_exist(path) else u.AssetToolsHelpers.get_asset_tools().create_asset(name,dest+'/Materials',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
            mel.set_material_instance_parent(mi,m)
            for key,val in [('Custom Snow Masking',True),('Override Blueprint Settings',False),('Use Vertex Paint?',False)]:
                mel.set_material_instance_static_switch_parameter_value(mi,key,val)
                assert mel.get_material_instance_static_switch_parameter_value(mi,key)==val,(mi.get_name(),key)
            mel.update_material_instance(mi);assets.save_loaded_asset(mi);material_map[m.get_path_name()]=mi
            report['material_instances'].append(mi.get_path_name())
        a.modify();a.static_mesh_component.set_material(slot,material_map[m.get_path_name()])

# Lighting adjustments are confined to this copied trial map.
for a in actors.get_all_level_actors():
    if isinstance(a,u.DirectionalLight):
        a.modify();c=a.get_component_by_class(u.DirectionalLightComponent)
        c.set_intensity(65000.);c.set_light_color(u.LinearColor(1.,.84,.66,1));c.set_editor_property('light_source_angle',2.2)
        # Preserve the user-authored directional light orientation.
        report['lighting']['directional_lux']=65000
    elif isinstance(a,u.SkyLight):
        a.modify();a.get_component_by_class(u.SkyLightComponent).set_intensity(4000.);report['lighting']['skylight_intensity']=4000
    elif isinstance(a,u.PostProcessVolume):
        a.modify();s=a.get_editor_property('settings');s.set_editor_property('auto_exposure_bias',-12.4);a.set_editor_property('settings',s);report['lighting']['manual_bias']=-12.4
report['tessellation_cvars']={n:u.SystemLibrary.get_console_variable_int_value(n) for n in ['r.Nanite.AllowTessellation','r.Nanite.Tessellation']}
report['material_libraries']=[x for x in dir(u) if 'Material' in x and 'Library' in x]
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(root/'Saved/EasySnow/features-enabled.json').write_text(json.dumps(report,indent=2))
