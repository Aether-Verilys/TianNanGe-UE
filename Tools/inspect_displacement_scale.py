import unreal as u,json
from pathlib import Path
out={'cvars':{n:u.SystemLibrary.get_console_variable_int_value(n) for n in ['r.Nanite.AllowTessellation','r.Nanite.Tessellation']},'meshes':[],'materials':[]}
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    if not isinstance(a,u.StaticMeshActor):continue
    c=a.static_mesh_component
    if any(m and '_EasySnow' in m.get_name() for m in c.get_materials()):
        out['meshes'].append({'label':a.get_actor_label(),'scale':str(a.get_actor_scale3d()),'mesh':c.static_mesh.get_path_name(),'nanite':c.static_mesh.get_editor_property('nanite_settings').get_editor_property('enabled'),'materials':[m.get_name() if m else None for m in c.get_materials()]})
for i in range(6,15):
    m=u.load_asset('/Game/TianNanGe/EasySnowIntegration/Materials/M_'+str(i).zfill(3)+'_EasySnow')
    out['materials'].append({'name':m.get_name(),'attrs':m.get_editor_property('use_material_attributes'),'tessellation':m.get_editor_property('enable_tessellation'),'scaling':str(m.get_editor_property('displacement_scaling')),'stats':str(u.MaterialEditingLibrary.get_statistics(m))})
(Path(__file__).resolve().parents[1]/'Saved/EasySnow/displacement-scale.json').write_text(json.dumps(out,indent=2))
