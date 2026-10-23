"""Replace individual cloud banks with a continuous rolling native volume layer."""
import datetime, json, shutil
from pathlib import Path
import unreal as u

root = Path(__file__).resolve().parents[1]
api = u.get_editor_subsystem(u.EditorActorSubsystem)
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
mel = u.MaterialEditingLibrary
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/' in world.get_path_name()
actors = api.get_all_level_actors()
backup = root / 'Backups' / ('CloudSeaLayer_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True, exist_ok=False)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
shutil.copy2(root / 'Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap', backup / 'TianNanGe_EasySnow.umap')
dest = '/Game/TianNanGe/CloudSea/Materials'
path = dest + '/M_CloudSea_Layer'
mat = assets.load_asset(path) if assets.does_asset_exist(path) else u.AssetToolsHelpers.get_asset_tools().create_asset('M_CloudSea_Layer', dest, u.Material, u.MaterialFactoryNew())
assert mat
mel.delete_all_material_expressions(mat)
mat.set_editor_property('blend_mode', u.BlendMode.BLEND_ADDITIVE)
mat.set_editor_property('material_domain', u.MaterialDomain.MD_VOLUME)
mat.set_editor_property('used_with_heterogeneous_volumes', True)
nodes = {}
for name, cls in [('WorldPos', u.MaterialExpressionWorldPosition), ('TimeSeconds', u.MaterialExpressionTime)]:
    nodes[name] = mel.create_material_expression(mat, cls, -900, len(nodes)*100)
defaults = {'SeaLevel': 25., 'WaveHeight': 40., 'WavePeriod': 1800., 'BillowPeriod': 550.,
            'SurfaceSoftness': 35., 'ErosionDepth': 45., 'DetailPeriod': 170.,
            'EdgeFade': 900., 'Extinction': .065, 'WindSpeed': 4., 'WindRotationDegrees':0.,
            'BillowStrength':.6, 'BridgeClearanceWidth':1., 'BridgeClearanceStrength':1.,
            'DensityMultiplier':1.5, 'InteriorDensityBoost':4.}
defaults.update(globals().get('COMMAND', {}).get('scalars', {}))
center, extent = (1800., 0., -400.), (4000., 4200., 750.)
for name, value in defaults.items():
    n = mel.create_material_expression(mat, u.MaterialExpressionScalarParameter, -700, len(nodes)*90)
    n.set_editor_property('parameter_name', name); n.set_editor_property('default_value', value)
    n.set_editor_property('group', '云海层'); nodes[name] = n
for name, value in [('CloudCenter', center), ('CloudExtent', extent)]:
    n = mel.create_material_expression(mat, u.MaterialExpressionVectorParameter, -500, len(nodes)*90)
    n.set_editor_property('parameter_name', name); n.set_editor_property('default_value', u.LinearColor(*value, 1.))
    n.set_editor_property('group', '云海范围'); nodes[name] = n
for name, tex in [('ShapeNoise', 'VT_noiseShape'), ('ErosionNoise', 'VT_noiseErosion')]:
    n = mel.create_material_expression(mat, u.MaterialExpressionTextureObjectParameter, -300, len(nodes)*90)
    n.set_editor_property('parameter_name', name)
    n.set_editor_property('texture', u.load_asset('/Game/TianNanGe/CloudSea/Noise/' + tex))
    n.set_editor_property('sampler_type', u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR); nodes[name] = n
custom = mel.create_material_expression(mat, u.MaterialExpressionCustom, 0, 0)
custom.set_editor_property('code', (root / 'Tools/Shaders/CloudSeaLayer.ush').read_text())
custom.set_editor_property('output_type', u.CustomMaterialOutputType.CMOT_FLOAT1)
inputs = []
for name in nodes:
    inp = u.CustomInput(); inp.set_editor_property('input_name', name); inputs.append(inp)
custom.set_editor_property('inputs', inputs)
for name, node in nodes.items():
    assert mel.connect_material_expressions(node, 'RGB' if name in ['CloudCenter', 'CloudExtent'] else '', custom, name)
assert mel.connect_material_property(custom, '', u.MaterialProperty.MP_SUBSURFACE_COLOR)
albedo = mel.create_material_expression(mat, u.MaterialExpressionVectorParameter, 150, 200)
albedo.set_editor_property('parameter_name', 'CloudAlbedo'); albedo.set_editor_property('default_value', u.LinearColor(.82, .88, .94, 1.))
albedo.set_editor_property('group', '云海光照')
assert mel.connect_material_property(albedo, 'RGB', u.MaterialProperty.MP_BASE_COLOR)
zero = mel.create_material_expression(mat, u.MaterialExpressionConstant, 150, 400); zero.set_editor_property('r', 0.)
assert mel.connect_material_property(zero, '', u.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat); assert assets.save_loaded_asset(mat)
mi_path = dest + '/MI_CloudSea_Layer'
mi = assets.load_asset(mi_path) if assets.does_asset_exist(mi_path) else u.AssetToolsHelpers.get_asset_tools().create_asset('MI_CloudSea_Layer', dest, u.MaterialInstanceConstant, u.MaterialInstanceConstantFactoryNew())
mel.set_material_instance_parent(mi, mat)
for k, v in defaults.items(): mel.set_material_instance_scalar_parameter_value(mi, k, v)
mel.update_material_instance(mi); assert assets.save_loaded_asset(mi)
label = 'Cloud Sea Layer - TianNanGe'
layer = next((a for a in actors if a.get_actor_label() == label), None)
layer = layer or api.spawn_actor_from_class(u.HeterogeneousVolume, u.Vector(*center))
assert layer
layer.modify(); layer.set_actor_label(label); layer.set_folder_path('Lookdev/Cloud Sea')
comp = layer.get_component_by_class(u.HeterogeneousVolumeComponent)
comp.set_volume_resolution(u.IntVector(256, 256, 128)); comp.set_editor_property('pivot_at_centroid', True)
layer.set_actor_location(u.Vector(*center), False, False)
layer.set_actor_scale3d(u.Vector(extent[0]/128., extent[1]/128., extent[2]/64.))
for k, v in {'step_factor':1., 'shadow_step_factor':4., 'shadow_bias_factor':.5, 'lighting_downsample_factor':4.}.items(): comp.set_editor_property(k, v)
comp.set_cast_shadow(True); comp.set_material(0, mi); comp.set_visibility(True); comp.set_hidden_in_game(False)
hidden = []
for a in actors:
    if isinstance(a, u.HeterogeneousVolume) and a.get_actor_label().startswith('Cloud Volume - '):
        c = a.get_component_by_class(u.HeterogeneousVolumeComponent); c.modify()
        c.set_visibility(False); c.set_hidden_in_game(True); hidden.append(a.get_actor_label())
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(root/'Saved/cloud-sea-layer.json').write_text(json.dumps({'actor':layer.get_path_name(), 'material':mi.get_path_name(), 'center':center, 'extent':extent, 'scalars':defaults, 'old_cloud_banks_hidden':hidden, 'backup':str(backup), 'material_stats':mel.get_statistics(mat).export_text()}, indent=2))
import runpy
runpy.run_path(str(root/'Tools/configure_cloud_controls.py'),init_globals={'COMMAND':{'open':False}},run_name='__main__')
