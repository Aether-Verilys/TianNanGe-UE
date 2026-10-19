"""Reload saved packages in a fresh UE process and check migration invariants."""
import unreal as u,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'Transfer/scene.json').read_text())
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert level.load_level('/Game/TianNanGe/Maps/TianNanGe_Main'),'Saved map failed to reload'
all_actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
meshes=[a for a in all_actors if isinstance(a,u.StaticMeshActor) and a.get_actor_label()!='Kloofendal HDRI Background']
camera=next(a for a in all_actors if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
checks={'engine':u.SystemLibrary.get_engine_version(),'expected_mesh_actors':len(data['nodes']),'actual_mesh_actors':len(meshes),'all_have_mesh':all(a.static_mesh_component.static_mesh is not None for a in meshes),'all_have_materials':all(all(a.static_mesh_component.get_material(i) is not None for i in range(a.static_mesh_component.get_num_materials())) for a in meshes),'camera_position_error_cm':(camera.get_actor_location()-u.Vector(**data['camera']['position'])).length(),'camera_horizontal_fov':camera.camera_component.field_of_view,'map_reloaded':True}
material_paths=['/Game/TianNanGe/Materials/'+m['id'] for m in data['materials']]+['/Game/TianNanGe/Lighting/M_Kloofendal_Sky']
checks['material_graphs_connected']=True
checks['skinned_height_relative_error']={}
for node in data['nodes']:
    if not node['skinned']:continue
    actor=next(a for a in meshes if a.static_mesh_component.static_mesh.get_name()==node['mesh'])
    origin,extent=actor.get_actor_bounds(False)
    expected_height=node['poseBoundsSize']['z']
    checks['skinned_height_relative_error'][node['name']]=abs(extent.z*2-expected_height)/expected_height
for path in material_paths:
    mat=u.load_asset(path)
    prop=u.MaterialProperty.MP_EMISSIVE_COLOR if path.endswith('M_Kloofendal_Sky') else u.MaterialProperty.MP_BASE_COLOR
    output_node=u.MaterialEditingLibrary.get_material_property_input_node(mat,prop)
    if not output_node:checks['material_graphs_connected']=False
    pending=[output_node] if output_node else []
    visited=set()
    while pending:
        node=pending.pop()
        if node.get_path_name() in visited:continue
        visited.add(node.get_path_name())
        inputs=[v for v in u.MaterialEditingLibrary.get_inputs_for_material_expression(mat,node) if v]
        if isinstance(node,(u.MaterialExpressionOneMinus,u.MaterialExpressionCustom,u.MaterialExpressionTextureSampleParameterCube)):
            if not inputs:checks['material_graphs_connected']=False
        pending.extend(inputs)
checks['pass']=checks['expected_mesh_actors']==checks['actual_mesh_actors'] and checks['all_have_mesh'] and checks['all_have_materials'] and checks['material_graphs_connected'] and checks['camera_position_error_cm']<.01 and all(v<.05 for v in checks['skinned_height_relative_error'].values())
(root/'validation-result.json').write_text(json.dumps(checks,indent=2))
assert checks['pass'],str(checks)
u.log('TIANNANGE_VALIDATION_OK '+str(checks))
