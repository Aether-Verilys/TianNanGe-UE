"""Refine native integration without changing density, noise or light settings."""
import unreal as u, json, time
from pathlib import Path
r=Path(__file__).resolve().parents[1]
api=u.get_editor_subsystem(u.EditorActorSubsystem)
actors=api.get_all_level_actors()
a=next(a for a in actors if a.get_actor_label()=='Cloud Sea Layer - TianNanGe')
c=a.get_component_by_class(u.HeterogeneousVolumeComponent)
before=json.loads((r/'Saved/cloud-banding-before.json').read_text())
assert all(next(x for x in actors if x.get_path_name()==p).get_actor_transform().export_text()==t for p,t in before['actors'].items())
mid=c.get_material(0)
assert isinstance(mid,u.MaterialInstanceDynamic)
assert all(abs(mid.get_scalar_parameter_value(k)-v)<1e-6 for k,v in before['scalars'].items())
c.modify();c.set_editor_property('step_factor',1.)
u.SystemLibrary.execute_console_command(a,'r.HeterogeneousVolumes.MaxStepCount 768')
for name in ['Jitter','StochasticFiltering']:
 assert u.SystemLibrary.get_console_variable_int_value('r.HeterogeneousVolumes.'+name)==0
assert c.get_editor_property('shadow_step_factor')==4.
assert c.get_editor_property('lighting_downsample_factor')==4.
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(r/'Saved/cloud-banding-fix-applied.json').write_text(json.dumps({'time':time.time(),'step_factor':1.,'max_steps':768,'shape_parameters_preserved':True,'original_transforms_preserved':True,'shadow_and_cache_budget_preserved':True},indent=2))
