import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];mel=u.MaterialEditingLibrary
report=json.loads((root/'Saved/ChaoticSkies/rotation-parameter.json').read_text())
mi=u.load_asset(report['instance']);assert mi
mel.set_material_instance_scalar_parameter_value(mi,'SkyRotationDegrees',0.);mel.update_material_instance(mi)
assert mel.get_material_instance_scalar_parameter_value(mi,'SkyRotationDegrees')==0.
for key,val in report['unchanged_parameters']['scalars'].items():assert mel.get_material_instance_scalar_parameter_value(mi,key)==val
for key in report['unchanged_parameters']['textures']:
    texture=mel.get_material_instance_texture_parameter_value(mi,key)
    assert texture.get_path_name()==report['unchanged_parameters']['textures'][key]
    assert texture.get_editor_property('address_x')==u.TextureAddress.TA_WRAP
for name,expected in report['transforms_preserved'].items():
    a=next(a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if a.get_name()==name)
    p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
    assert [p.x,p.y,p.z,r.pitch,r.yaw,r.roll,s.x,s.y,s.z]==expected
assert any(str(v.get_editor_property('parameter_info').get_editor_property('name'))=='SkyRotationDegrees' for v in mi.get_editor_property('scalar_parameter_values'))
assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(mi)
report.update(value=0.,visual_check_degrees=[0,90],texture_u_address_mode='Wrap',instance_override_enabled=True)
(root/'Saved/ChaoticSkies/rotation-parameter.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
u.EditorAssetLibrary.sync_browser_to_objects([mi.get_path_name()])
assert u.get_editor_subsystem(u.AssetEditorSubsystem).open_editor_for_assets([mi])
