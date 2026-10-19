import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/TianNanGe/Maps/TianNanGe_Main')
data=json.loads((root/'Transfer/scene.json').read_text())
r=[]
for node in data['nodes']:
    if not node['skinned']:continue
    actor=next(a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if isinstance(a,u.StaticMeshActor) and a.static_mesh_component.static_mesh.get_name()==node['mesh'])
    origin,extent=actor.get_actor_bounds(False)
    r.append({'name':node['name'],'ue_origin':str(origin),'ue_extent':str(extent),'ue_mesh_bounds':str(actor.static_mesh_component.static_mesh.get_bounds()),'ue_scale':str(actor.get_actor_scale3d()),'source_bounds':node['sourceBoundsSize']})
(root/'Tools/ue-bounds.json').write_text(json.dumps(r,indent=2))
