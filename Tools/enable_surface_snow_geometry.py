"""Enable scale-compensated Nanite snow relief on buildings and rocks only."""
import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
assets=u.get_editor_subsystem(u.EditorAssetSubsystem);mel=u.MaterialEditingLibrary
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/' in world.get_path_name()
dest='/Game/TianNanGe/EasySnowIntegration/SurfaceSnow/DisplacedMaterials'
groups={};bindings=[]
for a in actors:
    if not isinstance(a,u.StaticMeshActor):continue
    c=a.static_mesh_component
    for slot,mi in enumerate(c.get_materials()):
        if not mi or not isinstance(mi,u.MaterialInstanceConstant):continue
        parent=mi.get_editor_property('parent')
        if '/SurfaceSnow/' not in parent.get_path_name() or not parent.get_name().startswith(tuple(f'M_{i:03}_' for i in range(6,16))):continue
        assert c.static_mesh.get_editor_property('nanite_settings').get_editor_property('enabled')
        source_name=parent.get_name().replace('_Geometry','')
        group=groups.setdefault(source_name,{'parent':parent,'instance':mi,'max_scale':1.,'actors':[]})
        scale=a.get_actor_scale3d();group['max_scale']=max(group['max_scale'],abs(scale.x),abs(scale.y),abs(scale.z))
        group['actors'].append((a,slot,mi))
report={'materials':[],'bindings':[],'maximum_world_displacement_bound_cm':.6,'bridge_meshes_unchanged':True,'particle_collision':False}
for name,g in groups.items():
    material_path=dest+'/'+name+'_Geometry'
    m=assets.load_asset(material_path) if assets.does_asset_exist(material_path) else assets.duplicate_asset(g['parent'].get_path_name().split('.')[0],material_path)
    assert m
    fn=next(e for e in mel.get_material_expressions(m) if isinstance(e,u.MaterialExpressionMaterialFunctionCall) and e.get_editor_property('material_function') and 'WorldSnow' in e.get_editor_property('material_function').get_name())
    attrs=next((e for e in mel.get_material_expressions(m) if isinstance(e,u.MaterialExpressionMakeMaterialAttributes)),None)
    attrs=attrs or mel.create_material_expression(m,u.MaterialExpressionMakeMaterialAttributes,200,-650)
    incoming=dict(zip(mel.get_material_expression_input_names(fn),mel.get_inputs_for_material_expression(m,fn)))
    for pin,attr in [('Base Color','BaseColor'),('Roughness','Roughness'),('Normal','Normal'),('Ambient Occlusion','AmbientOcclusion')]:
        node=incoming.get(pin)
        if node:
            output=mel.get_input_node_output_name_for_material_expression(fn,node)
            if isinstance(output,tuple):output=next(x for x in output if isinstance(x,str))
            assert mel.connect_material_expressions(node,output or '',attrs,attr)
    for prop,pin in [(u.MaterialProperty.MP_METALLIC,'Metallic'),(u.MaterialProperty.MP_SPECULAR,'Specular')]:
        node=mel.get_material_property_input_node(m,prop)
        if node:assert mel.connect_material_expressions(node,mel.get_material_property_input_node_output_name(m,prop),attrs,pin)
    assert mel.connect_material_expressions(attrs,'',fn,'Material Attributes')
    m.set_editor_property('use_material_attributes',True)
    assert mel.connect_material_property(fn,'Material Attributes (MA)',u.MaterialProperty.MP_MATERIAL_ATTRIBUTES)
    for node in mel.get_material_expressions(m):
        if isinstance(node,u.MaterialExpressionScalarParameter) and str(node.get_editor_property('parameter_name'))=='Surface Snow Displacement Multiplier':node.set_editor_property('default_value',1.)
    m.set_editor_property('enable_tessellation',True)
    scaling=m.get_editor_property('displacement_scaling')
    scaling.set_editor_property('magnitude',.6/g['max_scale']);scaling.set_editor_property('center',0.)
    m.set_editor_property('displacement_scaling',scaling)
    mel.recompile_material(m);assert assets.save_loaded_asset(m)
    mipath=dest+'/MI_'+name+'_Geometry'
    mi=assets.load_asset(mipath) if assets.does_asset_exist(mipath) else assets.duplicate_asset(g['instance'].get_path_name().split('.')[0],mipath)
    assert mi
    mel.set_material_instance_parent(mi,m)
    mel.set_material_instance_scalar_parameter_value(mi,'Surface Snow Displacement Multiplier',1.)
    assert mel.get_material_instance_scalar_parameter_value(mi,'Surface Snow Displacement Multiplier')==1.
    mel.update_material_instance(mi);assert assets.save_loaded_asset(mi)
    for a,slot,old in g['actors']:
        a.modify();a.static_mesh_component.set_material(slot,mi)
        report['bindings'].append({'actor':a.get_path_name(),'slot':slot,'previous':old.get_path_name(),'instance':mi.get_path_name()})
    report['materials'].append({'material':m.get_path_name(),'instance':mi.get_path_name(),'maximum_actor_scale':g['max_scale'],'local_displacement_magnitude':.6/g['max_scale'],'maximum_world_displacement_bound_cm':.6})
main=next(a for a in actors if str(a.get_folder_path())=='EasySnow/Weather')
main.modify();main.set_editor_property('World Snow Displacement Multiplier',.5);main.call_method('UserConstructionScript')
for a in actors:
    if str(a.get_folder_path()) in ['EasySnow/Weather','EasySnow/Weather Layers']:
        assert not a.get_editor_property('Collision')
        for c in a.get_components_by_class(u.NiagaraComponent):c.activate(True)
u.SystemLibrary.execute_console_command(world,'r.Nanite.Tessellation 1')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(root/'Saved/EasySnow/surface-geometry.json').write_text(json.dumps(report,indent=2))
