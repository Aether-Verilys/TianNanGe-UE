"""Read back the saved EasySnow scene and the actual Niagara/material settings."""
import unreal as u,json,hashlib,os
from pathlib import Path
root=Path(__file__).resolve().parents[1];mel=u.MaterialEditingLibrary
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
out={'pid':os.getpid(),'engine':u.SystemLibrary.get_engine_version(),'world':world.get_path_name(),'weather':[],'materials':[],'bridges':[],'camera':[]}
assert '/EasySnowIntegration/Maps/' in out['world']
out['tessellation_enabled']=u.SystemLibrary.get_console_variable_int_value('r.Nanite.Tessellation')
assert out['tessellation_enabled']==1
baseline=json.loads((root/'Tools/Baselines/bridge-actors-before.json').read_text())
out['directional_light_preserved']=[]
for d in baseline:
    if d['class_name']!='DirectionalLight':continue
    a=next(a for a in actors if isinstance(a,u.DirectionalLight) and a.get_actor_label()==d['label'])
    r=a.get_actor_rotation();actual=[r.pitch,r.yaw,r.roll]
    assert max(abs(x-y) for x,y in zip(actual,d['rotation']))<.00001
    out['directional_light_preserved'].append({'label':d['label'],'rotation':actual})
for a in actors:
    if str(a.get_folder_path()) in ['EasySnow/Weather','EasySnow/Weather Layers']:
        d={'label':a.get_actor_label(),'world_snow_controller':a.get_editor_property('Set World Snow Material Settings'),'components':[],'settings':{}}
        for key in ['Camera-Centric','spawnRate -','windDirection','windStrength -','driftsEnable -','DriftingSnowAmount -','driftOpacity -','Collision','snowAmount','Snow Glimmer Intensity']:
            d['settings'][key]=a.get_editor_property(key)
        for c in a.get_components_by_class(u.NiagaraComponent):
            v={'name':c.get_name(),'active':c.is_active(),'auto_activate':c.get_editor_property('auto_activate'),'tick_enabled':c.is_component_tick_enabled(),'asset':c.get_fx_system_asset().get_path_name(),'floats':{},'bools':{}}
            for name in ['spawnRate','windStrength','windDirection','driftsSpawnRate','driftsSizeMin','driftsSizeMax','spawnRadius','spawnRadiusHeight','NearParticleSizeMin','NearParticleSizeMax']:
                v['floats'][name]=c.get_variable_float('User.'+name)
            for name in ['driftsEnable','toggleDriftGravity','collision','Global Snow']:
                v['bools'][name]=c.get_variable_bool('User.'+name)
            assert v['active'] and v['auto_activate']
            d['components'].append(v)
        out['weather'].append(d)
    if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'):
        out['camera'].append({'label':a.get_actor_label(),'auto_activate':str(a.get_editor_property('auto_activate_for_player')),'position':str(a.get_actor_location()),'rotation':str(a.get_actor_rotation())})
    if isinstance(a,u.StaticMeshActor) and a.static_mesh_component.static_mesh and '/BridgeReference/' in a.static_mesh_component.static_mesh.get_path_name():
        enabled=a.static_mesh_component.static_mesh.get_editor_property('nanite_settings').get_editor_property('enabled')
        assert not enabled
        out['bridges'].append({'label':a.get_actor_label(),'nanite':enabled})
assert len(out['weather'])==3
assert sum(d['world_snow_controller'] for d in out['weather'])==1
assert len(out['bridges'])==7
dest='/Game/TianNanGe/EasySnowIntegration/Materials/'
for name in ['M_000']+['M_'+str(i).zfill(3) for i in range(6,15)]+['M_PowderSnow','M_ColdTimber_SnowTop','M_WeatheredBridgeTimber']:
    m=u.load_asset(dest+name+'_EasySnow');mi=u.load_asset(dest+'MI_'+name+'_EasySnow');assert m and mi
    d={'material':m.get_path_name(),'mask_enabled':mel.get_material_instance_static_switch_parameter_value(mi,'Custom Snow Masking'),'tessellation':m.get_editor_property('enable_tessellation'),'attributes':m.get_editor_property('use_material_attributes'),'displacement_magnitude':m.get_editor_property('displacement_scaling').get_editor_property('magnitude'),'shader_stats':str(mel.get_statistics(m))}
    assert d['mask_enabled']
    prop=u.MaterialProperty.MP_MATERIAL_ATTRIBUTES if d['attributes'] else u.MaterialProperty.MP_EMISSIVE_COLOR
    node=mel.get_material_property_input_node(m,prop)
    d['snow_output_connected']=isinstance(node,u.MaterialExpressionMaterialFunctionCall)
    assert d['snow_output_connected']
    out['materials'].append(d)
mask=next(a for a in actors if a.get_actor_label()=='EasySnow Mask - Hero Footing')
out['mask']={'position':str(mask.get_actor_location()),'extent':str(mask.get_component_by_class(u.BoxComponent).get_unscaled_box_extent())}
mpc=u.load_asset('/Game/EasySnow/System/MP_WF_WorldData')
out['mpc']={name:u.MaterialLibrary.get_scalar_parameter_value(world,mpc,name) for name in ['Snow Amount','Snow Glimmering Intensity','Snow Displacement Multiplier','windStrength','windDirection','windBuildupOverride']}
assert abs(out['mpc']['windBuildupOverride']-1.)<.0001
for filename,expected in [('TianNanGe_ReferenceLook.umap','0F381B7B99E26B2143C3F583F87C7CC6D1DCB03EB7E61CB6296DFFDBC718B9A4'),('TianNanGe_Main.umap','6D662E9B85E484A5AF007A93C357FE8867D5C644EB3B6E3765BB198F8FB1885E')]:
    digest=hashlib.sha256((root/'Content/TianNanGe/Maps'/filename).read_bytes()).hexdigest().upper()
    out[filename+'_unchanged']=digest==expected;assert digest==expected
(root/'Saved/EasySnow/verified.json').write_text(json.dumps(out,indent=2))
