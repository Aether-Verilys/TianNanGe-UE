"""Roll back only the cloud clarity experiment, preserving the saved scene."""
import unreal as u, json, runpy, time
from pathlib import Path
r=Path(__file__).resolve().parents[1]
runpy.run_path(str(r/'Tools/live_session.py'),run_name='__main__')
if (r/'Saved/cloud-crash-recovered.json').exists():
 u.log('Cloud recovery already completed; preserving current scene settings.')
else:
 api=u.get_editor_subsystem(u.EditorActorSubsystem)
 actors=api.get_all_level_actors()
 transforms={a.get_path_name():a.get_actor_transform().export_text() for a in actors}
 layer=next(a for a in actors if a.get_actor_label()=='Cloud Sea Layer - TianNanGe')
 c=layer.get_component_by_class(u.HeterogeneousVolumeComponent)
 before=json.loads((r/'Backups/CloudClarity_20261023_141228/before.json').read_text())
 c.modify()
 for k,v in dict(before['component'],step_factor=1.).items():c.set_editor_property(k,v)
 mi=c.get_material(0)
 assert isinstance(mi,u.MaterialInstanceConstant)
 scalars=dict(before['scalars'],ErosionDepth=0.)
 for k,v in scalars.items():u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi,k,v)
 u.MaterialEditingLibrary.update_material_instance(mi)
 assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(mi)
 for a in actors:assert a.get_actor_transform().export_text()==transforms[a.get_path_name()]
 assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
 # Sampling stabilization is independent of the withdrawn high-cost clarity test.
 for k,v in dict(before['cvars'],Jitter=0,StochasticFiltering=0,MaxStepCount=768).items():
  u.SystemLibrary.execute_console_command(layer,'r.HeterogeneousVolumes.'+k+' '+str(v))
 p=r/'Config/DefaultEngine.ini'
 s=p.read_text().replace('; Temporary recovery gate; removed after component settings have been restored.\nr.HeterogeneousVolumes=0\n','')
 p.write_text(s)
 u.SystemLibrary.execute_console_command(layer,'r.HeterogeneousVolumes 1')
 (r/'Saved/cloud-crash-recovered.json').write_text(json.dumps({'time':time.time(),'component':before['component'],'scalars':scalars,'transforms_preserved':True,'clouds_enabled':True},indent=2))
