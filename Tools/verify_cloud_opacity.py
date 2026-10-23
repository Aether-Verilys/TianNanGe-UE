"""Verify exposed controls, material reuse and the actual pre-change scene state."""
import json
import time
from pathlib import Path
import unreal as u

r=Path(__file__).resolve().parents[1]
baseline_name=globals().get('COMMAND',{}).get('baseline')
baseline=json.loads((r/baseline_name).read_text()) if baseline_name else None
api=u.get_editor_subsystem(u.EditorActorSubsystem)
actors=api.get_all_level_actors()
control=next(a for a in actors if a.get_actor_label()=='Cloud Sea Controls - TianNanGe')
volume=control.get_editor_property('TargetVolume');mid=volume.get_material(0)
assert not getattr(u,'_cloud_opacity_view_test',None), 'Restore the visual test first.'
assert isinstance(mid,u.MaterialInstanceDynamic)
names=[str(k) for k in u.MaterialEditingLibrary.get_scalar_parameter_names(mid)]
values={k:control.get_editor_property(k) for k in names}
assert len(values)==16
if baseline:
 assert all(abs(values[k]-v)<1e-6 for k,v in baseline['scalars'].items())
assert all(abs(mid.get_scalar_parameter_value(k)-v)<1e-6 for k,v in values.items())
if baseline:
 assert mid.get_vector_parameter_value('CloudAlbedo').export_text()==baseline['color']
 for a in actors:
  assert a.get_actor_transform().export_text()==baseline['actors'][a.get_path_name()]
  if isinstance(a,u.CameraActor):
   assert a.get_component_by_class(u.CameraComponent).post_process_settings.export_text()==baseline['cameras'][a.get_path_name()]
snow={n.get_path_name():{'active':n.is_active(),'visible':n.is_visible()} for a in actors for n in a.get_components_by_class(u.NiagaraComponent)}
if baseline:assert snow==baseline['niagara']
cases=[(0.,1.),(.5,1.),(1.,2.),(1.5,4.),(2.,6.),(5.,8.)]
try:
 for index,(density,core) in enumerate(cases):
  control.set_editor_property('DensityMultiplier',density)
  control.set_editor_property('InteriorDensityBoost',core)
  control.call_method('ApplyCloudParameters' if index%2 else 'UserConstructionScript')
  assert volume.get_material(0)==mid
  assert abs(mid.get_scalar_parameter_value('DensityMultiplier')-density)<1e-6
  assert abs(mid.get_scalar_parameter_value('InteriorDensityBoost')-core)<1e-6
finally:
 for name in ['DensityMultiplier','InteriorDensityBoost']:control.set_editor_property(name,values[name])
 control.call_method('ApplyCloudParameters')
assert all(abs(mid.get_scalar_parameter_value(k)-v)<1e-6 for k,v in values.items())
mel=u.MaterialEditingLibrary
m=mid.get_editor_property('parent').get_editor_property('parent')
code=mel.get_material_property_input_node(m,u.MaterialProperty.MP_SUBSURFACE_COLOR).get_editor_property('code')
assert code==(r/'Tools/Shaders/CloudSeaLayer.ush').read_text()
assert 'return max(density, cacheSupport);' in code
assert volume.get_editor_property('step_factor')==1.
cvars={name:u.SystemLibrary.get_console_variable_int_value(name) for name in [
 'r.HeterogeneousVolumes.MaxStepCount','r.HeterogeneousVolumes.Jitter','r.HeterogeneousVolumes.StochasticFiltering',
 'r.RHICmdBypass','r.RHICmd.ParallelTranslate.Enable']}
assert list(cvars.values())==[768,0,0,0,1]
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
report={'passed':True,'time':time.time(),'scalars':values,'roundtrip_cases':cases,
        'same_mid':True,'baseline_checked':baseline_name,'original_parameters_preserved':True if baseline else None,
        'scene_and_cameras_preserved':True if baseline else None,
        'snow_preserved':True if baseline else None,'cvars':cvars}
(r/'Saved/cloud-opacity-verified.json').write_text(json.dumps(report,indent=2))
u.log('CLOUD_OPACITY_VERIFIED')
