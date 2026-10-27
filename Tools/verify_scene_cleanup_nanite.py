"""Verify cleanup, all remaining render geometry and bridge fallback vertex preservation."""
import unreal as u,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SourceAssets/SceneCleanup_20261027'
before=json.loads((OUT/'audit-before.json').read_text())
cleanup=json.loads((OUT/'cleanup.json').read_text())
progress=json.loads((OUT/'nanite-progress.json').read_text())
removed={s['path'] for s in cleanup['deleted_actors']}
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
all_actors=list(actors.get_all_level_actors());by_path={a.get_path_name():a for a in all_actors}
assert not (removed & set(by_path))
def v(x):return [x.x,x.y,x.z]
def close(x,y):return max(abs(a-b) for a,b in zip(x,y))<.0001
for s in before['actors']:
    if s['path'] in removed:continue
    assert s['path'] in by_path,s['path']
    a=by_path[s['path']];rot=a.get_actor_rotation()
    assert close(v(a.get_actor_location()),s['location']),s['path']
    assert close(v(a.get_actor_scale3d()),s['scale']),s['path']
    assert close([rot.pitch,rot.yaw,rot.roll],s['rotation']),s['path']
    assert a.get_editor_property('hidden')==s['hidden_game']
    for old_c in s['components']:
        c=u.find_object(None,old_c['path'])
        assert c and c.get_editor_property('static_mesh').get_path_name()==old_c['mesh'],old_c['path']
        assert c.get_editor_property('visible')==old_c['visible']
        assert [m.get_path_name() if m else None for m in c.get_materials()]==[m['asset'] for m in old_c['materials']]
mesh_api=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
geometry={};exceptions=[];components=0
for a in all_actors:
    for c in a.get_components_by_class(u.StaticMeshComponent):
        m=c.get_editor_property('static_mesh')
        if not m:continue
        path=m.get_path_name()
        if path.startswith('/Engine/EditorMeshes/'):
            exceptions.append(dict(actor=a.get_actor_label(),mesh=path,reason='Editor helper geometry'));continue
        if any(mat and mat.get_base_material().get_editor_property('blend_mode') not in (u.BlendMode.BLEND_OPAQUE,u.BlendMode.BLEND_MASKED) for mat in c.get_materials()):
            assert path=='/Game/Chaotic_Skies_II/Meshes/SM_Skybox_Mesh.SM_Skybox_Mesh',path
            exceptions.append(dict(actor=a.get_actor_label(),mesh=path,reason='Translucent sky material'));continue
        settings=m.get_editor_property('nanite_settings')
        assert settings.enabled,path
        assert not c.get_editor_property('disallow_nanite'),c.get_path_name()
        components+=1
        info=dict(nanite_enabled=True)
        if '/BridgeReference/' in path:
            verts=mesh_api.get_number_verts(m,0)
            assert verts==before['meshes'][path]['vertices'],(path,verts,before['meshes'][path]['vertices'])
            assert settings.position_precision==8
            assert settings.keep_percent_triangles==1 and settings.trim_relative_error==0
            assert settings.fallback_percent_triangles==1 and settings.fallback_relative_error==0
            info.update(fallback_vertices=verts,source_fallback_vertex_count_preserved=True,position_precision=settings.position_precision,shape_preservation=str(settings.shape_preservation))
        geometry[path]=info
assert len(geometry)==34,len(geometry)
assert len(all_actors)==len(before['actors'])-len(removed),(len(all_actors),len(before['actors']))
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
report=dict(passed=True,deleted_actors=len(removed),remaining_actors=len(all_actors),nanite_meshes=len(geometry),nanite_components=components,mesh_details=geometry,exceptions=exceptions,surviving_actor_transforms_visibility_materials_preserved=True,backup=cleanup['backup'])
(OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('SCENE_CLEANUP_NANITE_VERIFIED')
