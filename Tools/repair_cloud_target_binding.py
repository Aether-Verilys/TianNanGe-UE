"""Reconnect the existing controller to the sole live cloud; preserve its appearance."""
import datetime, json, shutil, time
from pathlib import Path
import unreal as u
r=Path(__file__).resolve().parents[1]
api=u.get_editor_subsystem(u.EditorActorSubsystem);actors=api.get_all_level_actors()
controls=[a for a in actors if a.get_class().get_name().startswith('BP_CloudSeaController')]
volumes=[a.get_component_by_class(u.HeterogeneousVolumeComponent) for a in actors if isinstance(a,u.HeterogeneousVolume) and a.get_component_by_class(u.HeterogeneousVolumeComponent).is_visible()]
assert len(controls)==len(volumes)==1
control=controls[0];volume=volumes[0];mid=volume.get_material(0)
assert isinstance(mid,u.MaterialInstanceDynamic)
assert control.get_editor_property('TargetVolume') in [None,volume]
values={str(k):mid.get_scalar_parameter_value(k) for k in u.MaterialEditingLibrary.get_scalar_parameter_names(mid)}
color=mid.get_vector_parameter_value('CloudAlbedo')
transforms={a.get_path_name():a.get_actor_transform().export_text() for a in actors}
backup=r/'Backups'/('CloudTargetRebind_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir()
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert level.save_current_level()
shutil.copy2(r/'Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap',backup/'TianNanGe_EasySnow.umap')
control.modify()
for k,v in values.items():control.set_editor_property(k,v)
control.set_editor_property('CloudAlbedo',color)
control.set_editor_property('TargetVolume',volume)
control.call_method('ApplyCloudParameters')
assert volume.get_material(0)==mid
assert all(abs(mid.get_scalar_parameter_value(k)-v)<1e-6 for k,v in values.items())
assert all(a.get_actor_transform().export_text()==transforms[a.get_path_name()] for a in actors)
assert level.save_current_level()
(r/'Saved/cloud-target-rebound.json').write_text(json.dumps({'passed':True,'time':time.time(),'backup':str(backup),
 'target':volume.get_path_name(),'scalars_preserved':values,'same_mid':True,'transforms_preserved':True},indent=2))
