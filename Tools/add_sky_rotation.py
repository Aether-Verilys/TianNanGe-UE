"""Expose horizontal sky texture rotation in degrees, retaining the current appearance at zero."""
import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];mel=u.MaterialEditingLibrary
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
mi=u.load_asset('/Game/TianNanGe/EasySnowIntegration/Skies/MI_Chaotic_WinterSky_04');assert mi
m=mi.get_editor_property('parent');assert m
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
def pose(a):
    r=a.get_actor_rotation();p=a.get_actor_location();s=a.get_actor_scale3d()
    return [p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]
poses={a.get_name():pose(a) for a in actors if isinstance(a,u.DirectionalLight) or a.get_actor_label()=='Lookdev Chaotic winter sky 04'}
def instance_settings():
    return {'scalars':{str(n):mel.get_material_instance_scalar_parameter_value(mi,n) for n in mel.get_scalar_parameter_names(mi) if str(n)!='SkyRotationDegrees'},'vectors':{str(n):list(mel.get_material_instance_vector_parameter_value(mi,n).to_tuple()) for n in mel.get_vector_parameter_names(mi)},'textures':{str(n):mel.get_material_instance_texture_parameter_value(mi,n).get_path_name() for n in mel.get_texture_parameter_names(mi)}}
before=instance_settings()
existing=next((e for e in mel.get_material_expressions(m) if isinstance(e,u.MaterialExpressionScalarParameter) and str(e.get_editor_property('parameter_name'))=='SkyRotationDegrees'),None)
if not existing:
    expressions=list(mel.get_material_expressions(m))
    coords=[e for e in expressions if isinstance(e,u.MaterialExpressionTextureCoordinate)]
    assert coords,'Sky material has no texture coordinates'
    # Snapshot links before inserting nodes, so re-routing cannot wire a node to itself.
    consumers=[]
    for e in expressions:
        for pin,source in zip(mel.get_material_expression_input_names(e),mel.get_inputs_for_material_expression(m,e)):
            if source in coords:consumers.append((e,pin,source))
    angle=mel.create_material_expression(m,u.MaterialExpressionScalarParameter,-1800,-500)
    angle.set_editor_property('parameter_name','SkyRotationDegrees');angle.set_editor_property('default_value',0.)
    angle.set_editor_property('group','天空角度');angle.set_editor_property('sort_priority',0)
    angle.set_editor_property('slider_min',0.);angle.set_editor_property('slider_max',360.)
    angle.set_editor_property('desc','天空贴图水平旋转，单位为度。0 保持当前角度，360 为一整圈；不改变灯光或天空球 Transform。')
    divide=mel.create_material_expression(m,u.MaterialExpressionDivide,-1550,-500);divide.set_editor_property('const_b',360.)
    assert mel.connect_material_expressions(angle,'',divide,'A')
    zero=mel.create_material_expression(m,u.MaterialExpressionConstant,-1550,-350);zero.set_editor_property('r',0.)
    offset=mel.create_material_expression(m,u.MaterialExpressionAppendVector,-1300,-500)
    assert mel.connect_material_expressions(divide,'',offset,'A')
    assert mel.connect_material_expressions(zero,'',offset,'B')
    rotated={}
    for index,coord in enumerate(coords):
        add=mel.create_material_expression(m,u.MaterialExpressionAdd,-1050,-300+index*220)
        add.set_editor_property('desc','Sky rotation UV: '+coord.get_name())
        assert mel.connect_material_expressions(coord,'',add,'A')
        assert mel.connect_material_expressions(offset,'',add,'B')
        rotated[coord.get_name()]=add
    for consumer,pin,coord in consumers:
        assert mel.connect_material_expressions(rotated[coord.get_name()],'',consumer,pin)
    mel.recompile_material(m)
    mel.set_material_instance_scalar_parameter_value(mi,'SkyRotationDegrees',0.)
    report={'created':True,'links_rotated':[{'consumer':e.get_name(),'pin':pin,'original_uv':uv.get_name()} for e,pin,uv in consumers]}
else:report={'created':False,'note':'Parameter already exists; existing value retained'}
mel.update_material_instance(mi)
assert before==instance_settings(),'Existing sky appearance parameters changed'
assert all(pose(next(a for a in actors if a.get_name()==name))==value for name,value in poses.items()),'Sky/light transform changed'
assert 'SkyRotationDegrees' in [str(n) for n in mel.get_scalar_parameter_names(mi)]
assert assets.save_loaded_asset(m);assert assets.save_loaded_asset(mi)
report.update(material=m.get_path_name(),instance=mi.get_path_name(),parameter='SkyRotationDegrees',value=mel.get_material_instance_scalar_parameter_value(mi,'SkyRotationDegrees'),unchanged_parameters=before,transforms_preserved=poses,shader_stats=str(mel.get_statistics(m)))
(root/'Saved/ChaoticSkies/rotation-parameter.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
