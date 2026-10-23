"""Repair the existing Blueprint in place; retain user values and graph controls."""
import ctypes
import datetime
import json
import shutil
from pathlib import Path
import unreal as u

r=Path(__file__).resolve().parents[1]
assert u.SystemLibrary.get_console_variable_int_value('r.RHICmdBypass')==1, 'Serialize the editor update first.'
api=u.get_editor_subsystem(u.EditorActorSubsystem)
actors=api.get_all_level_actors()
bp=u.load_asset('/Game/TianNanGe/CloudSea/Blueprints/BP_CloudSeaController')
controller=next(a for a in actors if a.get_class()==bp.generated_class())
volume=controller.get_editor_property('TargetVolume')
material=volume.get_material(0)
values={str(k):material.get_scalar_parameter_value(k) for k in u.MaterialEditingLibrary.get_scalar_parameter_names(material)}
assert all(abs(controller.get_editor_property(k)-v)<1e-6 for k,v in values.items()), 'Finish temporary parameter tests first.'
transforms={a.get_path_name():a.get_actor_transform().export_text() for a in actors}
backup=r/'Backups'/('CloudControllerReuse_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir()
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
assert assets.save_loaded_asset(bp)
shutil.copy2(r/'Content/TianNanGe/CloudSea/Blueprints/BP_CloudSeaController.uasset',backup/'BP_CloudSeaController.uasset')
u._cloud_builder=ctypes.CDLL(str(r/'Saved/CloudControllerRepair/Binaries/Win64/UnrealEditor-CloudBlueprintBuilder.dll'))
assert u._cloud_builder.RepairCloudControllerMaterialReuse()==0
actors=api.get_all_level_actors()
controller=next(a for a in actors if a.get_class()==bp.generated_class())
controller.call_method('ApplyCloudParameters')
mid=volume.get_material(0)
assert all(abs(mid.get_scalar_parameter_value(k)-v)<1e-6 for k,v in values.items())
# Exercise both paths that are used by the editor and external Blueprints.
old=values['Extinction']
try:
 for i in range(12):
  value=old+(0.0001 if i%2 else 0.)
  controller.set_editor_property('Extinction',value)
  controller.call_method('UserConstructionScript' if i%2 else 'ApplyCloudParameters')
  assert volume.get_material(0)==mid, 'Applying a value must reuse the same MID.'
  assert abs(mid.get_scalar_parameter_value('Extinction')-value)<1e-6
finally:
 controller.set_editor_property('Extinction',old)
 controller.call_method('ApplyCloudParameters')
assert all(a.get_actor_transform().export_text()==transforms[a.get_path_name()] for a in actors)
assert assets.save_loaded_asset(bp)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
api.set_selected_level_actors([controller])
(r/'Saved/cloud-controller-reuse-verified.json').write_text(json.dumps({'passed':True,'backup':str(backup),'apply_and_construction_calls':12,'same_mid_reused':True,'scalars_preserved':values,'transforms_preserved':True},indent=2))
