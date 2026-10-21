"""Verify the surface-only profile against its live scene baseline."""
import unreal as u
import json
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[1]
before = json.loads((root/'Saved/EasySnow/surface-before.json').read_text())
after = json.loads((root/'Saved/EasySnow/surface-after.json').read_text())
profile = json.loads((root/'Saved/EasySnow/surface-snow.json').read_text())
assert before['environment'] == after['environment'], 'Lighting, fog or camera changed'
assert before['sky'] == after['sky'], 'Sky material parameters changed'
actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
by_path = {a.get_path_name():a for a in actors}
mel = u.MaterialEditingLibrary
bindings = {(b['actor'], b['slot']):b for b in profile['bindings']}
removed_during_user_edit = []
for path,previous in before['meshes'].items():
    if path not in after['meshes'] or path not in by_path:
        removed_during_user_edit.append(path)
        continue
    current = after['meshes'][path]
    assert current['mesh'] == previous['mesh']
    for slot,material in enumerate(previous['materials']):
        binding = bindings.get((path,slot))
        assert current['materials'][slot] == (binding['instance'] if binding else material)
        if binding: assert by_path[path].static_mesh_component.get_material(slot).get_path_name() == binding['instance']
for item in profile['materials']:
    m = u.load_asset(item['material'])
    assert not m.get_editor_property('enable_tessellation')
    assert not m.get_editor_property('use_material_attributes')
    assert mel.get_material_property_input_node(m,u.MaterialProperty.MP_WORLD_POSITION_OFFSET) is None
    assert mel.get_material_default_scalar_parameter_value(m,'Surface Snow Displacement Multiplier') == 0.
    assert isinstance(mel.get_material_property_input_node(m,u.MaterialProperty.MP_BASE_COLOR),u.MaterialExpressionMaterialFunctionCall)
    mi = u.load_asset(item['instance'])
    assert not mel.get_material_instance_static_switch_parameter_value(mi,'Override Blueprint Settings')
for path,old in before['weather'].items():
    new = after['weather'][path]
    for field,value in old.items():
        if field != 'snowAmount': assert new[field] == value, (path,field)
    a = by_path[path]
    assert a.get_editor_property('Collision') is False
    for c in a.get_components_by_class(u.NiagaraComponent):
        assert c.is_active()
        assert c.get_variable_bool('User.collision') in [False,None]
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
mpc = u.load_asset('/Game/EasySnow/System/MP_WF_WorldData')
settings = {k:u.MaterialLibrary.get_scalar_parameter_value(world,mpc,k) for k in ['Snow Amount','Snow Displacement Multiplier','Snow Glimmering Intensity','windBuildupOverride']}
assert abs(settings['Snow Amount']-.28)<.00001
assert all(settings[k] == 0 for k in settings if k!='Snow Amount')
for name,expected in [('TianNanGe_ReferenceLook','0f381b7b99e26b2143c3f583f87c7cc6d1dcb03eb7e61cb6296dffdbc718b9a4'),('TianNanGe_Main','6d662e9b85e484a5af007a93c357fe8867d5c644eb3b6e3765bb198f8fb1885e')]:
    assert hashlib.sha256((root/f'Content/TianNanGe/Maps/{name}.umap').read_bytes()).hexdigest()==expected
for tag in ['SurfaceSnow_Before','SurfaceSnow_After']:
    assert json.loads((root/f'Saved/EasySnow/{tag}-capture.json').read_text())['success']
(root/'Saved/EasySnow/surface-verified.json').write_text(json.dumps({'passed':True,'environment_preserved':True,'sky_preserved':True,'airborne_weather_preserved':True,'materials':len(profile['materials']),'actors':sum(b['actor'] in by_path for b in profile['bindings']),'particle_collision':False,'displacement':False,'settings':settings,'native_before_after_capture':True,'removed_during_concurrent_user_edit':removed_during_user_edit},indent=2))
