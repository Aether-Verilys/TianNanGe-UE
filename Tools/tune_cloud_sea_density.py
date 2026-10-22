"""Apply the expanded cloud-bank profile without changing scene lights or cameras."""
import datetime, json, shutil
from pathlib import Path
import unreal as u

root = Path(__file__).resolve().parents[1]
profile = json.loads((root / 'SourceAssets/CloudSea/dense_profile.json').read_text(encoding='utf-8'))
api = u.get_editor_subsystem(u.EditorActorSubsystem)
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
mel = u.MaterialEditingLibrary
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().split('.')[0] == profile['map']
actors = {a.get_actor_label(): a for a in api.get_all_level_actors() if isinstance(a, u.HeterogeneousVolume)}
assert all(item['label'] in actors for item in profile['clouds'])

# Preserve the current saved scene and material edits before applying the profile.
backup = root / 'Backups' / ('CloudDensity_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True, exist_ok=False)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
packages = [profile['map']]
before = []
for item in profile['clouds']:
    a = actors[item['label']]
    comp = a.get_component_by_class(u.HeterogeneousVolumeComponent)
    mi = comp.get_material(0)
    assert mi
    assert assets.save_loaded_asset(mi)
    packages.append(mi.get_path_name().split('.')[0])
    before.append({'label': item['label'], 'location': list(a.get_actor_location().to_tuple()),
                   'scale': list(a.get_actor_scale3d().to_tuple()), 'material': mi.get_path_name(),
                   'vectors': {k: list(mel.get_material_instance_vector_parameter_value(mi, k).to_tuple()) for k in ['CloudCenter', 'CloudExtent']},
                   'scalars': {k: mel.get_material_instance_scalar_parameter_value(mi, k) for k in profile['scalars']}})
for package in packages:
    rel = Path('Content') / package.removeprefix('/Game/')
    suffix = '.umap' if package == profile['map'] else '.uasset'
    src = (root / rel).with_suffix(suffix)
    assert src.exists(), str(src)
    dst = (backup / rel).with_suffix(suffix)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
(backup / 'before.json').write_text(json.dumps(before, indent=2))

report = {'backup': str(backup), 'profile': profile, 'verified': []}
with u.ScopedEditorTransaction('Expand and densify bridge cloud banks'):
    for item in profile['clouds']:
        a = actors[item['label']]
        c = a.get_component_by_class(u.HeterogeneousVolumeComponent)
        mi = c.get_material(0)
        a.modify(); c.modify(); mi.modify()
        center, extent = item['center'], item['extent']
        a.set_actor_location(u.Vector(*center), False, False)
        a.set_actor_scale3d(u.Vector(*(v / 64. for v in extent)))
        for key, values in [('CloudCenter', center), ('CloudExtent', extent)]:
            mel.set_material_instance_vector_parameter_value(mi, key, u.LinearColor(*values, 1.))
            actual = mel.get_material_instance_vector_parameter_value(mi, key).to_tuple()
            assert all(abs(actual[i] - values[i]) < .002 for i in range(3))
        for key, value in profile['scalars'].items():
            mel.set_material_instance_scalar_parameter_value(mi, key, value)
            assert abs(mel.get_material_instance_scalar_parameter_value(mi, key) - value) < .00001
        mel.update_material_instance(mi)
        assert assets.save_loaded_asset(mi)
        report['verified'].append(a.get_actor_label())
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(root / 'Saved/cloud-density-applied.json').write_text(json.dumps(report, indent=2))
