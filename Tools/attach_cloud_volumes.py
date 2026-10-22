"""Render the cloud banks with UE's native heterogeneous-volume components."""
import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
api=u.get_editor_subsystem(u.EditorActorSubsystem);actors=api.get_all_level_actors()
layout_path=root/'Saved/cloud-sea.json'
if not layout_path.exists():layout_path=root/'SourceAssets/CloudSea/base_layout.json'
layout=json.loads(layout_path.read_text())['actors']
report=[]
limit=globals().get('COMMAND',{}).get('limit',10)
for old in actors:
    if isinstance(old,u.StaticMeshActor) and old.get_actor_label().startswith('Cloud Sea - '):
        old.modify();old.static_mesh_component.set_visibility(False);old.static_mesh_component.set_hidden_in_game(True)
for index,item in enumerate(layout[:limit]):
    name=item['label'].replace('Cloud Sea - ','Cloud Volume - ')
    actor=next((a for a in actors if a.get_actor_label()==name),None)
    actor=actor or api.spawn_actor_from_class(u.HeterogeneousVolume,u.Vector(*item['center']))
    assert actor
    actor.modify();actor.set_actor_label(name);actor.set_folder_path('Lookdev/Cloud Sea')
    comp=actor.get_component_by_class(u.HeterogeneousVolumeComponent)
    comp.set_editor_property('pivot_at_centroid',True);comp.set_volume_resolution(u.IntVector(128,128,128))
    # Keep the visible cloud tops below the camera, exposing their relief.
    center=list(item['center']);center[2]-=30.
    actor.set_actor_location(u.Vector(*center),False,False)
    actor.set_actor_scale3d(u.Vector(*(v/64. for v in item['extent'])))
    comp.set_editor_property('step_factor',2.);comp.set_editor_property('shadow_step_factor',4.)
    comp.set_editor_property('lighting_downsample_factor',2.)
    comp.set_cast_shadow(True)
    mi=u.load_asset(item['instance'].split('.')[0]+'_Lit');assert mi
    u.MaterialEditingLibrary.set_material_instance_vector_parameter_value(mi,'CloudCenter',u.LinearColor(*center,1))
    u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(mi)
    comp.set_material(0,mi)
    report.append({'actor':actor.get_path_name(),'material':mi.get_path_name(),'center':center,'extent':item['extent']})
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(root/'Saved/cloud-native-volumes.json').write_text(json.dumps(report,indent=2))
