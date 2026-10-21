"""Add EasySnow shading to environment surfaces without collision or displacement."""
import unreal as u
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
dest = '/Game/TianNanGe/EasySnowIntegration/SurfaceSnow/Materials'
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
mel = u.MaterialEditingLibrary
assert '/EasySnowIntegration/Maps/' in u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name()
function = u.load_asset('/Game/EasySnow/Materials/Functions/MF_WF_WorldSnow')
sources = [f'/Game/TianNanGe/Revision_fdf5e67/Materials/M_{i:03}' for i in range(6,16)] + [
    '/Game/TianNanGe/Revision_fdf5e67/Lookdev/M_ColdTimber_SnowTop',
    '/Game/TianNanGe/BridgeReference/Materials/M_WeatheredBridgeTimber']
report = {'materials': [], 'bindings': [], 'profile': 'surface_shading_only', 'displacement': False, 'collision': False}
mapping = {}

def scalar(m, name, value, x, y):
    n = mel.create_material_expression(m, u.MaterialExpressionScalarParameter, x, y)
    n.set_editor_property('parameter_name', name)
    n.set_editor_property('default_value', value)
    n.set_editor_property('group', '表面积雪')
    return n

for source_path in sources:
    source = u.load_asset(source_path)
    assert source and isinstance(source,u.Material), source_path
    path = dest + '/' + source.get_name() + '_SurfaceSnow'
    fresh = not assets.does_asset_exist(path)
    m = assets.load_asset(path) if not fresh else assets.duplicate_asset(source_path, path)
    assert m
    if fresh:
        fn = mel.create_material_expression(m,u.MaterialExpressionMaterialFunctionCall,700,0)
        fn.set_material_function(function)
        for prop, pin in [(u.MaterialProperty.MP_BASE_COLOR,'Base Color'),(u.MaterialProperty.MP_ROUGHNESS,'Roughness'),(u.MaterialProperty.MP_NORMAL,'Normal'),(u.MaterialProperty.MP_AMBIENT_OCCLUSION,'Ambient Occlusion')]:
            n = mel.get_material_property_input_node(m,prop)
            if n: assert mel.connect_material_expressions(n,mel.get_material_property_input_node_output_name(m,prop),fn,pin)
            assert mel.connect_material_property(fn,pin,prop)
        for index,(pin,value) in enumerate([('Snow Roughness',.9),('Snow Tiling',1.),('Blend Snow/Source Normals',.12),('Snow Displacement Multiplier',0.)]):
            node = scalar(m,'Surface '+pin,value,100,450+index*140)
            assert mel.connect_material_expressions(node,'',fn,pin)
        for index,(pin,color) in enumerate([('Snow Base Color',(.73,.81,.88)),('Snow Normal Intensity',(.25,.25,1.))]):
            node = mel.create_material_expression(m,u.MaterialExpressionVectorParameter,100,1100+index*160)
            node.set_editor_property('parameter_name','Surface '+pin)
            node.set_editor_property('default_value',u.LinearColor(*color,1))
            node.set_editor_property('group','表面积雪')
            assert mel.connect_material_expressions(node,'',fn,pin)
        m.set_editor_property('enable_tessellation',False)
        # Use individual shading outputs only; neither MA displacement nor WPO is connected.
        m.set_editor_property('use_material_attributes',False)
        mel.recompile_material(m)
        assert assets.save_loaded_asset(m)
    mi_path = dest + '/MI_' + m.get_name()
    mi = assets.load_asset(mi_path) if assets.does_asset_exist(mi_path) else u.AssetToolsHelpers.get_asset_tools().create_asset('MI_'+m.get_name(),dest,u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi,m)
    for key,val in [('Override Blueprint Settings',False),('Custom Snow Masking',True),('Use Vertex Paint?',False)]:
        mel.set_material_instance_static_switch_parameter_value(mi,key,val)
        assert mel.get_material_instance_static_switch_parameter_value(mi,key)==val
    mel.update_material_instance(mi)
    assert assets.save_loaded_asset(mi)
    mapping[source.get_path_name()] = mi
    report['materials'].append({'source':source.get_path_name(),'material':m.get_path_name(),'instance':mi.get_path_name()})

for a in actors:
    if not isinstance(a,u.StaticMeshActor): continue
    for slot,old in enumerate(a.static_mesh_component.get_materials()):
        if old and old.get_path_name() in mapping:
            mi = mapping[old.get_path_name()]
            a.modify()
            a.static_mesh_component.set_material(slot,mi)
            report['bindings'].append({'actor':a.get_path_name(),'label':a.get_actor_label(),'slot':slot,'source':old.get_path_name(),'instance':mi.get_path_name()})

main = next(a for a in actors if str(a.get_folder_path())=='EasySnow/Weather')
settings = {'snowAmount':.28,'Transition Sharpness':3.5,'breakupIntensity':.55,'breakupTextureTiling':1.5,'windBuildupOverride':0.,'World Snow Displacement Multiplier':0.,'Snow Glimmer Intensity':0.}
main.modify()
for key,value in settings.items(): main.set_editor_property(key,value)
main.call_method('UserConstructionScript')
for a in actors:
    if str(a.get_folder_path()) in ['EasySnow/Weather','EasySnow/Weather Layers']:
        assert a.get_editor_property('Collision') is False
        for c in a.get_components_by_class(u.NiagaraComponent): c.activate(True)
report['settings'] = settings
report['actors_changed'] = len({x['actor'] for x in report['bindings']})
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
report_path = root/'Saved/EasySnow/surface-snow.json'
if report['bindings'] or not report_path.exists(): report_path.write_text(json.dumps(report,indent=2))
u.log('SURFACE_SNOW_ENABLED')
