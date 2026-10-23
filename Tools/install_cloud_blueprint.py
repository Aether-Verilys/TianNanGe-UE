"""Initialize the generated native Blueprint with current scene values, then place it.

Run once after CloudBlueprintBuilder; refuses to overwrite a placed controller.
The saved Blueprint does not need this script or the builder to function.
"""
import ast, ctypes, json
from pathlib import Path
import unreal as u

r = Path(__file__).resolve().parents[1]
bel = u.BlueprintEditorLibrary
api = u.get_editor_subsystem(u.EditorActorSubsystem)
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
bp = u.load_asset('/Game/TianNanGe/CloudSea/Blueprints/BP_CloudSeaController')
assert bp
actors = api.get_all_level_actors()
assert not any(x.get_actor_label() == 'Cloud Sea Controls - TianNanGe' for x in actors), 'Controller already installed; preserve its settings.'
layer = next(x for x in actors if x.get_actor_label() == 'Cloud Sea Layer - TianNanGe')
component = layer.get_component_by_class(u.HeterogeneousVolumeComponent)
mi = u.load_asset('/Game/TianNanGe/CloudSea/Materials/MI_CloudSea_Layer')
assert component.get_material(0) == mi, 'Unexpected material; inspect before replacing.'
tree = ast.parse((r/'Tools/configure_cloud_controls.py').read_text(encoding='utf-8'))
spec = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'spec' for t in n.targets))
values = {name: u.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(mi, name) for name in spec}
color = u.MaterialEditingLibrary.get_material_instance_vector_parameter_value(mi, 'CloudAlbedo')
builder = u._cloud_builder
builder.SetCloudControlMeta.argtypes = [ctypes.c_wchar_p]*5
for name, (group, lo, hi, tip, _) in spec.items():
    builder.SetCloudControlMeta(name, 'Cloud Sea|' + group, tip, str(lo), str(hi))
bel.set_blueprint_variable_category(bp, 'CloudAlbedo', 'Cloud Sea|06 颜色')
assert bel.compile_blueprint(bp)
cdo = u.get_default_object(bp.generated_class())
for name, value in values.items():
    cdo.set_editor_property(name, value)
cdo.set_editor_property('CloudAlbedo', color)
assert assets.save_loaded_asset(bp)
controller = api.spawn_actor_from_class(bp.generated_class(), layer.get_actor_location())
controller.set_actor_label('Cloud Sea Controls - TianNanGe')
controller.set_folder_path('Lookdev/Cloud Sea')
controller.set_editor_property('TargetVolume', component)
controller.call_method('ApplyCloudParameters')
dynamic = component.get_material(0)
assert isinstance(dynamic, u.MaterialInstanceDynamic)
for name, value in values.items():
    assert abs(dynamic.get_scalar_parameter_value(name) - value) < 1e-6, name
# Exercise the public callable function and restore the exact scene value.
old = values['Extinction']
try:
    controller.set_editor_property('Extinction', old + 0.01)
    controller.call_method('ApplyCloudParameters')
    assert abs(component.get_material(0).get_scalar_parameter_value('Extinction') - (old + .01)) < 1e-6
finally:
    controller.set_editor_property('Extinction', old)
    controller.call_method('ApplyCloudParameters')
before = json.loads((r/'Saved/cloud-blueprint-before.json').read_text())
for actor in actors:
    assert actor.get_actor_transform().export_text() == before['transforms'][actor.get_path_name()], actor.get_actor_label()
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
api.set_selected_level_actors([controller])
(r/'Saved/cloud-blueprint-installed.json').write_text(json.dumps({'passed': True, 'blueprint': bp.get_path_name(), 'controller': controller.get_path_name(), 'target': component.get_path_name(), 'scalars': values, 'color': color.export_text(), 'density_roundtrip_passed': True, 'original_transforms_preserved': True}, indent=2), encoding='utf-8')
