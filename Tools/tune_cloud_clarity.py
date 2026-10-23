"""Withdrawn experiment: followed by a D3D12/Niagara render-thread crash.

Kept for diagnosis only. Do not reapply the high-cost settings automatically.
The causal connection is unproven; short captures did not establish stability.
"""
raise RuntimeError('Cloud clarity experiment withdrawn after render-thread crash; retain recovered settings.')
import unreal as u, json, datetime, shutil
from pathlib import Path
r=Path(__file__).resolve().parents[1]
api=u.get_editor_subsystem(u.EditorActorSubsystem);assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
actors=api.get_all_level_actors()
layer=next(a for a in actors if a.get_actor_label()=='Cloud Sea Layer - TianNanGe')
c=layer.get_component_by_class(u.HeterogeneousVolumeComponent)
ctl=next((a for a in actors if a.get_class().get_name()=='BP_CloudSeaController_C'),None)
mat=c.get_material(0)
backup=r/'Backups'/('CloudClarity_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir()
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
for rel in ['Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap','Content/TianNanGe/CloudSea/Materials/MI_CloudSea_Layer.uasset','Config/DefaultEngine.ini']:
 shutil.copy2(r/rel,backup/Path(rel).name)
cvars={'DownsampleFactor':1,'Filter':0,'Jitter':0,'StochasticFiltering':0,'MaxStepCount':1024,'Shadows.Resolution':512,'Shadows.MaxSampleCount':8}
props={'step_factor':.5,'shadow_step_factor':1.,'lighting_downsample_factor':2.}
scalars={'SurfaceSoftness':24.,'WindSpeed':12.,'ErosionDepth':10.}
def read(k):
 return mat.get_scalar_parameter_value(k) if isinstance(mat,u.MaterialInstanceDynamic) else u.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(mat,k)
before={'cvars':{k:u.SystemLibrary.get_console_variable_float_value('r.HeterogeneousVolumes.'+k) for k in cvars},'component':{k:c.get_editor_property(k) for k in props},'scalars':{k:read(k) for k in scalars},'transforms':{a.get_path_name():a.get_actor_transform().export_text() for a in actors}}
(backup/'before.json').write_text(json.dumps(before,indent=2))
for k,v in cvars.items():u.SystemLibrary.execute_console_command(layer,'r.HeterogeneousVolumes.'+k+' '+str(v))
c.modify()
for k,v in props.items():c.set_editor_property(k,v)
if ctl:
 for k,v in scalars.items():ctl.set_editor_property(k,v)
 ctl.call_method('ApplyCloudParameters')
else:
 # A deleted controller can leave its transient MID assigned in the editor.
 # Preserve its complete settings in the persistent parent before saving.
 if isinstance(mat,u.MaterialInstanceDynamic):
  parent=mat.get_editor_property('parent')
  assert isinstance(parent,u.MaterialInstanceConstant)
  for k in u.MaterialEditingLibrary.get_scalar_parameter_names(parent):
   u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(parent,k,mat.get_scalar_parameter_value(k))
  for k in u.MaterialEditingLibrary.get_vector_parameter_names(parent):
   u.MaterialEditingLibrary.set_material_instance_vector_parameter_value(parent,k,mat.get_vector_parameter_value(k))
  mat=parent;c.set_material(0,mat)
 for k,v in scalars.items():
  if isinstance(mat,u.MaterialInstanceDynamic):mat.set_scalar_parameter_value(k,v)
  else:u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mat,k,v)
 if isinstance(mat,u.MaterialInstanceConstant):
  u.MaterialEditingLibrary.update_material_instance(mat);assert assets.save_loaded_asset(mat)
for a in actors:assert a.get_actor_transform().export_text()==before['transforms'][a.get_path_name()]
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(r/'Saved/cloud-clarity-applied.json').write_text(json.dumps({'backup':str(backup),'cvars':cvars,'component':props,'scalars':scalars,'transforms_preserved':True},indent=2))
