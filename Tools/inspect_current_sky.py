import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];out={'world':u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name(),'actors':[]}
mel=u.MaterialEditingLibrary
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    if not isinstance(a,u.StaticMeshActor) or 'sky' not in a.get_actor_label().lower():continue
    mats=a.static_mesh_component.get_materials();d={'name':a.get_name(),'label':a.get_actor_label(),'rotation':str(a.get_actor_rotation()),'materials':[]}
    for mi in mats:
        if not mi:continue
        m=mi.get_editor_property('parent') if isinstance(mi,u.MaterialInstanceConstant) else mi
        entry={'instance':mi.get_path_name(),'parent':m.get_path_name(),'parameters':{str(n):mel.get_material_instance_scalar_parameter_value(mi,n) for n in mel.get_scalar_parameter_names(mi)} if isinstance(mi,u.MaterialInstanceConstant) else {},'uv_nodes':[]}
        for e in mel.get_material_expressions(m):
            if isinstance(e,u.MaterialExpressionTextureCoordinate):entry['uv_nodes'].append({'id':e.get_name(),'index':e.get_editor_property('coordinate_index'),'u_tiling':e.get_editor_property('u_tiling'),'v_tiling':e.get_editor_property('v_tiling')})
        d['materials'].append(entry)
    out['actors'].append(d)
(root/'Saved/ChaoticSkies/current-sky.json').write_text(json.dumps(out,indent=2))
