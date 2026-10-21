"""Enable sub-centimetre native Nanite snow displacement on the building materials only."""
import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];assets=u.get_editor_subsystem(u.EditorAssetSubsystem);mel=u.MaterialEditingLibrary
dest='/Game/TianNanGe/EasySnowIntegration';report=[]
material_scales={}
for actor in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    if not isinstance(actor,u.StaticMeshActor):continue
    s=actor.get_actor_scale3d();maximum=max(abs(s.x),abs(s.y),abs(s.z),1.)
    for mi in actor.static_mesh_component.get_materials():
        if isinstance(mi,u.MaterialInstanceConstant):
            parent=mi.get_editor_property('parent')
            if parent:material_scales[parent.get_path_name()]=max(maximum,material_scales.get(parent.get_path_name(),1.))
for i in range(6,15):
    m=u.load_asset(dest+'/Materials/M_'+str(i).zfill(3)+'_EasySnow');assert m
    fn=next(e for e in mel.get_material_expressions(m) if isinstance(e,u.MaterialExpressionMaterialFunctionCall) and e.get_editor_property('material_function') and 'WorldSnow' in e.get_editor_property('material_function').get_name())
    scale=next((e for e in mel.get_material_expressions(m) if isinstance(e,u.MaterialExpressionConstant) and e.get_editor_property('desc')=='EasySnow displacement strength'),None)
    scale=scale or mel.create_material_expression(m,u.MaterialExpressionConstant,-200,1100)
    scale.set_editor_property('desc','EasySnow displacement strength');scale.set_editor_property('r',.65)
    assert mel.connect_material_expressions(scale,'',fn,'Snow Displacement Multiplier')
    # UE hides MP_Displacement from Python. The package's complete Material
    # Attributes output carries it natively, preserving the source channels.
    names=mel.get_material_expression_input_names(fn)
    incoming=dict(zip(names,mel.get_inputs_for_material_expression(m,fn)))
    attrs=next((e for e in mel.get_material_expressions(m) if isinstance(e,u.MaterialExpressionMakeMaterialAttributes)),None)
    attrs=attrs or mel.create_material_expression(m,u.MaterialExpressionMakeMaterialAttributes,200,-500)
    for source_pin,attr_pin in [('Base Color','BaseColor'),('Roughness','Roughness'),('Normal','Normal'),('Ambient Occlusion','AmbientOcclusion')]:
        node=incoming.get(source_pin)
        if node:
            pin=mel.get_input_node_output_name_for_material_expression(fn,node)
            if isinstance(pin,tuple):pin=next(v for v in pin if isinstance(v,str))
            assert mel.connect_material_expressions(node,pin or '',attrs,attr_pin)
    for prop,attr_pin in [(u.MaterialProperty.MP_METALLIC,'Metallic'),(u.MaterialProperty.MP_SPECULAR,'Specular')]:
        node=mel.get_material_property_input_node(m,prop)
        if node:assert mel.connect_material_expressions(node,mel.get_material_property_input_node_output_name(m,prop),attrs,attr_pin)
    assert mel.connect_material_expressions(attrs,'',fn,'Material Attributes')
    m.set_editor_property('use_material_attributes',True)
    assert mel.connect_material_property(fn,'Material Attributes (MA)',u.MaterialProperty.MP_MATERIAL_ATTRIBUTES)
    m.set_editor_property('enable_tessellation',True)
    # Nanite Magnitude is measured before component scaling. Unity imports here
    # range from 10x to 3139x; cap the largest instance at 0.8 cm in world space.
    object_magnitude=.8/material_scales.get(m.get_path_name(),1.)
    scaling=m.get_editor_property('displacement_scaling');scaling.set_editor_property('magnitude',object_magnitude);scaling.set_editor_property('center',0.0);m.set_editor_property('displacement_scaling',scaling)
    mel.recompile_material(m);assets.save_loaded_asset(m)
    report.append({'material':m.get_path_name(),'object_magnitude':object_magnitude,'maximum_component_scale':material_scales.get(m.get_path_name(),1.),'maximum_world_magnitude_cm':.8,'source':'EasySnow Material Attributes displacement','bridge_nanite_enabled':False})
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    if str(a.get_folder_path()) not in ['EasySnow/Weather','EasySnow/Weather Layers']:continue
    ground='Ground' in a.get_actor_label()
    a.modify();a.set_editor_property('snowEmissive',u.LinearColor(550,650,750,1) if not ground else u.LinearColor(0,0,0,1))
    a.set_editor_property('subsurfaceIntensity',.4);a.set_editor_property('subsurfaceColor',u.LinearColor(.5,.65,.85,1));a.call_method('UserConstructionScript')
    for c in a.get_components_by_class(u.NiagaraComponent):c.activate(True)
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    if isinstance(a,u.PostProcessVolume):
        a.modify();s=a.get_editor_property('settings');s.set_editor_property('motion_blur_amount',.12);a.set_editor_property('settings',s)
assets.save_directory(dest,True,True)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(root/'Saved/EasySnow/displacement.json').write_text(json.dumps(report,indent=2))
