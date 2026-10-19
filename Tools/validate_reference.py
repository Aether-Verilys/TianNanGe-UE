"""Validate saved revision, scene coverage, Nanite, and material outputs."""
import unreal as u,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'Transfer_fdf5e67/scene.json').read_text())
assert u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/TianNanGe/Maps/TianNanGe_ReferenceLook')
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
source=[a for a in actors if isinstance(a,u.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_path_name().startswith('/Game/TianNanGe/Revision_fdf5e67/Meshes/')]
checks={'engine':u.SystemLibrary.get_engine_version(),'source_commit':'fdf5e672e4081c53729675a72b944f8cde8f5c28','expected_actors':len(DATA['nodes']),'actual_source_actors':len(source),'mesh_assets':len({a.static_mesh_component.static_mesh.get_path_name() for a in source}),'all_material_slots_valid':all(all(a.static_mesh_component.get_material(i) for i in range(a.static_mesh_component.get_num_materials())) for a in source),'nanite_enabled_meshes':sum(u.load_asset('/Game/TianNanGe/Revision_fdf5e67/Meshes/'+name).get_editor_property('nanite_settings').enabled for name in {n['mesh'] for n in DATA['nodes']}),'new_source_material_actor_counts':{},'skinned_world_heights_cm':{}}
for m in DATA['materials']:
    if 'Tripo/' not in m['source']:continue
    checks['new_source_material_actor_counts'][m['name']]=sum(any(a.static_mesh_component.get_material(i).get_name()==m['id'] for i in range(a.static_mesh_component.get_num_materials())) for a in source)
for n in DATA['nodes']:
    if not n['skinned']:continue
    actor=next(a for a in source if a.static_mesh_component.static_mesh.get_name()==n['mesh'])
    center,extent=actor.get_actor_bounds(False)
    checks['skinned_world_heights_cm'][n['name']]={'actual':extent.z*2,'source_pose':n['poseBoundsSize']['z']}
checks['material_outputs_valid']=all(u.MaterialEditingLibrary.get_material_property_input_node(a.static_mesh_component.get_material(i),u.MaterialProperty.MP_BASE_COLOR) for a in source for i in range(a.static_mesh_component.get_num_materials()))
if (ROOT/'Tools/Live/final-profile.json').exists():
    camera=next(a for a in actors if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
    rot=camera.get_actor_rotation()
    checks['saved_camera']={'pitch':rot.pitch,'yaw':rot.yaw,'roll':rot.roll,'horizontal_fov':camera.camera_component.field_of_view}
    character=next(a for a in source if a.get_actor_label()=='tripo_node_4dee5643')
    center,extent=character.get_actor_bounds(False)
    checks['character_feet_z_cm']=center.z-extent.z
    checks['character_lateral_cm']=character.get_actor_location().y
    checks['bridge_snow_detail_actors']=sum(a.get_actor_label().startswith('Lookdev Snow detail') for a in actors)
    checks['saved_lights']={}
    for a in actors:
        if isinstance(a,u.DirectionalLight):checks['saved_lights'][a.get_actor_label()]=a.get_component_by_class(u.DirectionalLightComponent).get_editor_property('intensity')
        elif isinstance(a,u.ExponentialHeightFog):checks['saved_fog_density']=a.get_component_by_class(u.ExponentialHeightFogComponent).get_editor_property('fog_density')
        elif isinstance(a,u.PostProcessVolume):checks['saved_fixed_ev']=-a.get_editor_property('settings').get_editor_property('auto_exposure_bias')
    checks['final_look_persisted']=abs(rot.pitch-4.2)<.001 and abs(rot.roll)<.001 and abs(camera.camera_component.field_of_view-58.7979375)<.001 and abs(checks['character_feet_z_cm']-7.3)<.01 and abs(checks['character_lateral_cm']-32)<.01 and checks['bridge_snow_detail_actors']==120 and abs(checks['saved_fog_density']-.18)<.001 and checks['saved_lights'].get('Lookdev Warm backlight')==35000 and checks['saved_lights'].get('Lookdev Cool soft fill')==10000 and checks['saved_fixed_ev']==12
checks['pass']=checks['actual_source_actors']==checks['expected_actors'] and checks['all_material_slots_valid'] and checks['material_outputs_valid'] and all(checks['new_source_material_actor_counts'].values()) and checks.get('final_look_persisted',True)
(ROOT/'validation-reference-result.json').write_text(json.dumps(checks,indent=2))
assert checks['pass'],checks
u.log('TIANNANGE_REFERENCE_VALIDATION_OK')
