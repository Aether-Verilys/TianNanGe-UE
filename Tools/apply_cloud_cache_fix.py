"""Apply bounded cache support with serialized live editing and no SceneCapture churn.

First run Live/cloud_prepare_safe_update.py, let the editor render several
frames, then run this script. Restore the previous threading mode after shader
compilation. This guard is an editing precaution, not a proven crash root cause.
"""
import unreal as u, json, datetime, shutil
from pathlib import Path
r=Path(__file__).resolve().parents[1]
assert u.SystemLibrary.get_console_variable_int_value('r.RHICmdBypass')==1, 'Prepare the serialized live update first.'
assert u.SystemLibrary.get_console_variable_int_value('r.RHICmd.ParallelTranslate.Enable')==0
mel=u.MaterialEditingLibrary;assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
m=u.load_asset('/Game/TianNanGe/CloudSea/Materials/M_CloudSea_Layer')
mi=u.load_asset('/Game/TianNanGe/CloudSea/Materials/MI_CloudSea_Layer')
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
assert not any(isinstance(a,u.SceneCapture2D) for a in actors), 'Do not mix live shader updates with temporary SceneCapture tests.'
before={a.get_path_name():a.get_actor_transform().export_text() for a in actors}
values={str(k):mel.get_material_instance_scalar_parameter_value(mi,k) for k in mel.get_scalar_parameter_names(mi)}
backup=r/'Backups'/('CloudCacheMaterial_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir()
assets.save_loaded_asset(m)
shutil.copy2(r/'Content/TianNanGe/CloudSea/Materials/M_CloudSea_Layer.uasset',backup/'M_CloudSea_Layer.uasset')
custom=mel.get_material_property_input_node(m,u.MaterialProperty.MP_SUBSURFACE_COLOR)
(backup/'previous-shader.ush').write_text(custom.get_editor_property('code'))
m.modify();custom.set_editor_property('code',(r/'Tools/Shaders/CloudSeaLayer.ush').read_text())
mel.recompile_material(m);assert assets.save_loaded_asset(m)
assert all(mel.get_material_instance_scalar_parameter_value(mi,k)==v for k,v in values.items())
assert all(a.get_actor_transform().export_text()==before[a.get_path_name()] for a in actors)
zero=mel.get_material_property_input_node(m,u.MaterialProperty.MP_EMISSIVE_COLOR)
assert isinstance(zero,u.MaterialExpressionConstant) and zero.get_editor_property('r')==0.
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
for key in ['r.HeterogeneousVolumes.Jitter','r.HeterogeneousVolumes.StochasticFiltering']:
 u.SystemLibrary.execute_console_command(world,key+' 0')
 assert u.SystemLibrary.get_console_variable_int_value(key)==0
(r/'Saved/cloud-cache-fix-applied.json').write_text(json.dumps({'backup':str(backup),'parameters_preserved':values,'actor_transforms_preserved':True,'emission_zero':True,'shader_stats':mel.get_statistics(m).export_text()},indent=2))
