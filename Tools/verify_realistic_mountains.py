"""Verify saved replacement references and unchanged original actor transforms."""
import unreal as u,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SourceAssets/RealisticMountains/UserGenerated_20261027'
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
all_actors=list(actors.get_all_level_actors());by_path={a.get_path_name():a for a in all_actors}
before=json.loads((OUT/'scene-before.json').read_text())
replacement=json.loads((OUT/'replacement.json').read_text())
originals=json.loads((OUT/'original-visibility.json').read_text())
def v(x):return [x.x,x.y,x.z]
def close(a,b):return max(abs(x-y) for x,y in zip(a,b))<.0001
for s in before['actors']:
    a=by_path[s['path']];r=a.get_actor_rotation()
    assert close(v(a.get_actor_location()),s['location']),s['path']
    assert close(v(a.get_actor_scale3d()),s['scale']),s['path']
    assert close([r.pitch,r.yaw,r.roll],s['rotation']),s['path']
    if 'camera_fov' in s:assert abs(a.camera_component.field_of_view-s['camera_fov'])<.0001
for s in originals:
    a=by_path[s['path']]
    assert not a.static_mesh_component.get_editor_property('visible')
    assert a.get_editor_property('hidden')
    assert a.static_mesh_component.static_mesh.get_path_name()==s['mesh']
for s in replacement['replacements']:
    a=by_path[s['replacement']];c=a.static_mesh_component
    assert c.get_editor_property('visible') and not a.get_editor_property('hidden')
    assert c.static_mesh.get_path_name()==s['mesh']
    assert c.static_mesh.get_editor_property('nanite_settings').enabled
    assert all(x.material_interface for x in c.static_mesh.static_materials)
textures=[]
for i in (1,2,3):
    imported=json.loads((OUT/('ue-import-%02d.json'%i)).read_text())
    for p in imported['objects']:
        a=u.load_asset(p)
        if isinstance(a,u.Texture2D):textures.append(dict(asset=p,width=a.blueprint_get_size_x(),height=a.blueprint_get_size_y(),srgb=a.get_editor_property('srgb'),compression=str(a.get_editor_property('compression_settings'))))
result=dict(replacement_count=len(replacement['replacements']),hidden_original_count=len(originals),all_original_actor_transforms_unchanged=True,camera_fov_unchanged=True,nanite_enabled=True,materials_present=True,textures=textures)
(OUT/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
u.log('REALISTIC_MOUNTAINS_VALIDATED')
