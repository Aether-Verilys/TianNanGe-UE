"""Replace the approximate translucent marcher with true, lit volume density."""
import unreal as u,json,shutil,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
assets=u.get_editor_subsystem(u.EditorAssetSubsystem);mel=u.MaterialEditingLibrary
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/' in world.get_path_name()
shape=u.load_asset('/Game/TianNanGe/CloudSea/Noise/VT_noiseShape');erosion=u.load_asset('/Game/TianNanGe/CloudSea/Noise/VT_noiseErosion')
assert shape and erosion
dest='/Game/TianNanGe/CloudSea/Materials';path=dest+'/M_CloudSea_LitVolume'
m=assets.load_asset(path) if assets.does_asset_exist(path) else u.AssetToolsHelpers.get_asset_tools().create_asset('M_CloudSea_LitVolume',dest,u.Material,u.MaterialFactoryNew())
assert m
mel.delete_all_material_expressions(m)
m.set_editor_property('blend_mode',u.BlendMode.BLEND_ADDITIVE)
m.set_editor_property('material_domain',u.MaterialDomain.MD_VOLUME)
m.set_editor_property('used_with_heterogeneous_volumes',True)
nodes={}
for name,cls in [('WorldPos',u.MaterialExpressionWorldPosition),('TimeSeconds',u.MaterialExpressionTime)]:nodes[name]=mel.create_material_expression(m,cls,-900,len(nodes)*150)
for name,value in {'BridgeY':0.,'Seed':0.,'WindSpeed':4.,'ShapePeriod':2600.,'DetailPeriod':320.,'Coverage':.20,'ErosionStrength':.15,'Extinction':.045}.items():
    n=mel.create_material_expression(m,u.MaterialExpressionScalarParameter,-700,len(nodes)*120);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',value);n.set_editor_property('group','云海密度');nodes[name]=n
for name,value in {'CloudCenter':(0,0,-150),'CloudExtent':(650,500,200)}.items():
    n=mel.create_material_expression(m,u.MaterialExpressionVectorParameter,-500,len(nodes)*120);n.set_editor_property('parameter_name',name);n.set_editor_property('default_value',u.LinearColor(*value,1));n.set_editor_property('group','云海范围');nodes[name]=n
for name,texture in [('ShapeNoise',shape),('ErosionNoise',erosion)]:
    n=mel.create_material_expression(m,u.MaterialExpressionTextureObjectParameter,-300,len(nodes)*120);n.set_editor_property('parameter_name',name);n.set_editor_property('texture',texture);n.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);nodes[name]=n
custom=mel.create_material_expression(m,u.MaterialExpressionCustom,0,0)
custom.set_editor_property('code',(root/'Tools/Shaders/CloudSeaDensity.ush').read_text());custom.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT1)
inputs=[]
for name in nodes:
    inp=u.CustomInput();inp.set_editor_property('input_name',name);inputs.append(inp)
custom.set_editor_property('inputs',inputs)
for name,node in nodes.items():assert mel.connect_material_expressions(node,'RGB' if name in ['CloudCenter','CloudExtent'] else '',custom,name)
assert mel.connect_material_property(custom,'',u.MaterialProperty.MP_SUBSURFACE_COLOR)
albedo=mel.create_material_expression(m,u.MaterialExpressionVectorParameter,100,250)
albedo.set_editor_property('parameter_name','CloudAlbedo');albedo.set_editor_property('default_value',u.LinearColor(.82,.88,.94,1));albedo.set_editor_property('group','云海光照')
assert mel.connect_material_property(albedo,'RGB',u.MaterialProperty.MP_BASE_COLOR)
zero=mel.create_material_expression(m,u.MaterialExpressionConstant,100,450);zero.set_editor_property('r',0.)
assert mel.connect_material_property(zero,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(m);assert assets.save_loaded_asset(m)
report={'material':m.get_path_name(),'native_volume_lighting':True,'emissive':0.,'assets':[shape.get_path_name(),erosion.get_path_name()],'actors':[],'lights':[]}
for a in actors:
    if a.get_actor_label().startswith('Cloud Sea - '):
        old=a.static_mesh_component.get_material(0)
        name=old.get_name().removesuffix('_Lit')+'_Lit';mipath=dest+'/'+name
        mi=assets.load_asset(mipath) if assets.does_asset_exist(mipath) else u.AssetToolsHelpers.get_asset_tools().create_asset(name,dest,u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi,m)
        for key in ['CloudCenter','CloudExtent']:mel.set_material_instance_vector_parameter_value(mi,key,mel.get_material_instance_vector_parameter_value(old,key))
        for key in ['BridgeY','Seed']:mel.set_material_instance_scalar_parameter_value(mi,key,mel.get_material_instance_scalar_parameter_value(old,key))
        mel.update_material_instance(mi);assert assets.save_loaded_asset(mi)
        a.modify();a.static_mesh_component.set_editor_property('disallow_nanite',True)
        a.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE)
        a.static_mesh_component.set_material(0,mi)
        report['actors'].append({'actor':a.get_path_name(),'material':mi.get_path_name()})
    elif isinstance(a,u.DirectionalLight):
        c=a.get_component_by_class(u.DirectionalLightComponent)
        report['lights'].append({'actor':a.get_path_name(),'rotation':a.get_actor_rotation().export_text(),'intensity':c.intensity,'volumetric_scattering_intensity':c.get_editor_property('volumetric_scattering_intensity'),'cast_volumetric_shadow':c.get_editor_property('cast_volumetric_shadow')})
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(root/'Saved/cloud-sea-lit.json').write_text(json.dumps(report,indent=2))
