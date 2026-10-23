"""Read-only verification of the cloud flicker fix in the current editor.

Run through Tools/dispatch.py. The optional before snapshot is local evidence,
not an assertion that user-authored cloud settings must equal factory defaults.
"""
import unreal as u
import hashlib
import json
import time
from pathlib import Path

root = Path(__file__).resolve().parents[1]
actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
mel = u.MaterialEditingLibrary
layers = [a for a in actors if isinstance(a, u.HeterogeneousVolume)
          and a.get_component_by_class(u.HeterogeneousVolumeComponent).is_visible()]
assert len(layers) == 1, 'Expected one visible native cloud layer.'
volume = layers[0].get_component_by_class(u.HeterogeneousVolumeComponent)
material = volume.get_material(0)
mi = material.get_editor_property('parent') if isinstance(material, u.MaterialInstanceDynamic) else material
parent = mi.get_editor_property('parent')
custom = mel.get_material_property_input_node(parent, u.MaterialProperty.MP_SUBSURFACE_COLOR)
shader = (root / 'Tools/Shaders/CloudSeaLayer.ush').read_text()
assert custom.get_editor_property('code') == shader
assert 'return max(density, cacheSupport);' in shader
zero = mel.get_material_property_input_node(parent, u.MaterialProperty.MP_EMISSIVE_COLOR)
assert isinstance(zero, u.MaterialExpressionConstant) and zero.get_editor_property('r') == 0
expected = {
    'r.HeterogeneousVolumes.Jitter': 0,
    'r.HeterogeneousVolumes.StochasticFiltering': 0,
    'r.HeterogeneousVolumes.DownsampleFactor': 2,
    'r.HeterogeneousVolumes.MaxStepCount': 768,
    'r.HeterogeneousVolumes.Shadows': 1,
    'r.HeterogeneousVolumes.IndirectLighting.Mode': 1,
    'r.HeterogeneousVolumes.VolumetricFog': 0,
    'r.HeterogeneousVolumes.HeightFog': 1,
    'r.VolumetricFog': 1,
}
actual = {k: u.SystemLibrary.get_console_variable_int_value(k) for k in expected}
assert actual == expected, (actual, expected)
component = {k: volume.get_editor_property(k) for k in
             ['step_factor', 'shadow_step_factor', 'lighting_downsample_factor']}
assert component == {'step_factor': 1., 'shadow_step_factor': 4., 'lighting_downsample_factor': 4.}
captures = [a.get_path_name() for a in actors if isinstance(a, u.SceneCapture2D)]
assert not captures, captures
read_scalar = material.get_scalar_parameter_value if isinstance(material, u.MaterialInstanceDynamic) else lambda k: mel.get_material_instance_scalar_parameter_value(mi, k)
scalars = {str(k): read_scalar(k) for k in mel.get_scalar_parameter_names(mi)}
niagara = {n.get_path_name(): {'active': n.is_active(), 'visible': n.is_visible()}
           for a in actors for n in a.get_components_by_class(u.NiagaraComponent)}
transforms = {a.get_path_name(): a.get_actor_transform().export_text() for a in actors}
report = {'time': time.time(), 'passed': True, 'material': material.get_path_name(),
          'shader_sha256': hashlib.sha256(shader.encode()).hexdigest(),
          'emission_zero': True, 'cvars': actual, 'component': component,
          'scalars': scalars, 'niagara': niagara, 'scene_captures': captures}
controllers = [a for a in actors if a.get_actor_label() == 'Cloud Sea Controls - TianNanGe']
assert len(controllers) == 1
assert controllers[0].get_editor_property('TargetVolume') == volume
assert all(abs(controllers[0].get_editor_property(k) - v) < 1e-6 for k, v in scalars.items())
report['controller'] = controllers[0].get_path_name()
report['controller_parameters_match'] = True
baseline_name = globals().get('COMMAND', {}).get('baseline')
baseline_path = root / baseline_name if baseline_name else None
if baseline_path is not None and baseline_path.exists():
    baseline = json.loads(baseline_path.read_text())
    # Restoring the requested controller intentionally adds one actor.
    report['transforms_preserved'] = all(transforms.get(k) == v for k, v in baseline['actors'].items())
    report['scalars_preserved'] = all(scalars.get(k) == v for k, v in baseline['scalars'].items())
    baseline_snow = baseline['niagara']
    if isinstance(baseline_snow, list):
        baseline_snow = {n['path']: {'active': n['active'], 'visible': n['visible']} for n in baseline_snow}
    report['snow_preserved'] = niagara == baseline_snow
    assert report['transforms_preserved'] and report['scalars_preserved'] and report['snow_preserved'], report
(root / 'Saved/cloud-stability-verified.json').write_text(json.dumps(report, indent=2))
u.log('CLOUD_STABILITY_VERIFIED')
