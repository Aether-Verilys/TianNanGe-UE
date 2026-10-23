"""Restore the existing controller, copying the live cloud values before binding it."""
import datetime
import json
import shutil
from pathlib import Path
import unreal as u

root = Path(__file__).resolve().parents[1]
api = u.get_editor_subsystem(u.EditorActorSubsystem)
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
mel = u.MaterialEditingLibrary
actors = api.get_all_level_actors()
bp = u.load_asset('/Game/TianNanGe/CloudSea/Blueprints/BP_CloudSeaController')
assert bp and bp.generated_class(), 'Existing controller asset is required; do not overwrite it.'
assert not any(a.get_class() == bp.generated_class() for a in actors), 'A controller already exists; inspect it instead of duplicating it.'
assert u.get_default_object(bp.generated_class()).get_editor_property('TargetVolume') is None
layer = next(a for a in actors if a.get_actor_label() == 'Cloud Sea Layer - TianNanGe')
volume = layer.get_component_by_class(u.HeterogeneousVolumeComponent)
current = volume.get_material(0)
mi = current.get_editor_property('parent') if isinstance(current, u.MaterialInstanceDynamic) else current
assert mi.get_name() == 'MI_CloudSea_Layer'
scalar = current.get_scalar_parameter_value if isinstance(current, u.MaterialInstanceDynamic) else lambda k: mel.get_material_instance_scalar_parameter_value(mi, k)
vector = current.get_vector_parameter_value if isinstance(current, u.MaterialInstanceDynamic) else lambda k: mel.get_material_instance_vector_parameter_value(mi, k)
values = {str(k): scalar(k) for k in mel.get_scalar_parameter_names(mi)}
color = vector('CloudAlbedo')
transforms = {a.get_path_name(): a.get_actor_transform().export_text() for a in actors}
backup = root / 'Backups' / ('CloudControllerRestore_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
shutil.copy2(root / 'Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap', backup / 'TianNanGe_EasySnow.umap')
controller = api.spawn_actor_from_class(bp.generated_class(), layer.get_actor_location())
assert controller
try:
    controller.set_actor_label('Cloud Sea Controls - TianNanGe')
    controller.set_folder_path('Lookdev/Cloud Sea')
    # Target is deliberately unbound until all user values have been copied.
    for name, value in values.items():
        controller.set_editor_property(name, value)
    controller.set_editor_property('CloudAlbedo', color)
    controller.set_editor_property('TargetVolume', volume)
    controller.call_method('ApplyCloudParameters')
    dynamic = volume.get_material(0)
    assert isinstance(dynamic, u.MaterialInstanceDynamic)
    assert all(abs(dynamic.get_scalar_parameter_value(k) - v) < 1e-6 for k, v in values.items())
    assert dynamic.get_vector_parameter_value('CloudAlbedo') == color
    assert all(a.get_actor_transform().export_text() == transforms[a.get_path_name()] for a in actors)
    assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
except Exception:
    volume.set_material(0, current)
    api.destroy_actor(controller)
    raise
api.set_selected_level_actors([controller])
(root / 'Saved/cloud-controller-restored.json').write_text(json.dumps({
    'blueprint': bp.get_path_name(), 'controller': controller.get_path_name(),
    'backup': str(backup), 'scalars': values, 'color': color.export_text(),
    'existing_transforms_preserved': True, 'live_values_preserved': True,
}, indent=2))
