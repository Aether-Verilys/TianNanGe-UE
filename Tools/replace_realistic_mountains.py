"""Replace mountain visuals after all three imports succeed; preserve recoverable originals."""
import unreal as u, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SourceAssets/RealisticMountains/UserGenerated_20261027'
TAG='RealisticMountainReplacement_20261027'
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.')
all_actors=list(actors.get_all_level_actors())
assert not any(TAG in [str(t) for t in a.tags] for a in all_actors),'Replacement already exists; use the saved mapping instead of duplicating it.'
meshes=[u.load_asset(json.loads((OUT/('ue-import-%02d.json'%i)).read_text())['mesh']) for i in (1,2,3)]
assert all(isinstance(m,u.StaticMesh) for m in meshes)
def v(x):return [x.x,x.y,x.z]
def snapshot(a):
    c=a.static_mesh_component
    return dict(path=a.get_path_name(),label=a.get_actor_label(),folder=str(a.get_folder_path()),visible=c.get_editor_property('visible'),hidden_game=a.get_editor_property('hidden'),temporary_hidden=a.is_temporarily_hidden_in_editor(),mesh=c.static_mesh.get_path_name())
def transform(a):
    q=a.get_actor_rotation()
    return dict(location=v(a.get_actor_location()),rotation=[q.pitch,q.yaw,q.roll],scale=v(a.get_actor_scale3d()))
protected={a.get_path_name():transform(a) for a in all_actors if not str(a.get_folder_path()).startswith('TianNanGe_Blockout/Mountains')}
plans=[];hide=[]
for a in all_actors:
    if not isinstance(a,u.StaticMeshActor):continue
    c=a.static_mesh_component;m=c.static_mesh;folder=str(a.get_folder_path())
    if not m or not folder.startswith('TianNanGe_Blockout/Mountains/'):continue
    if m.get_name()=='SM_0011':
        group=folder.split('/')[2]
        idx=1 if group=='Mountain_Far' or a.get_actor_label()=='Visual2' else (2 if group in ('Mountain_Left','Mountain_TeaHouse','Mountain_WatchTower') else 0)
    elif folder.endswith(('NearBridgeLand','FarBridgeLand')):
        hide.append(a)
        if a.get_actor_label()!='Rock':continue
        group=folder.split('/')[-1];idx=0 if group=='NearBridgeLand' else 2
    elif folder.endswith('Mountain_FarRight/FittedFoundation') and a.get_actor_label()=='StoneCore':
        hide.append(a);continue
    else:continue
    if a not in hide:hide.append(a)
    origin,extent=a.get_actor_bounds(False)
    b=meshes[idx].get_bounds();yaw=a.get_actor_rotation().yaw
    cs=abs(math.cos(math.radians(yaw)));sn=abs(math.sin(math.radians(yaw)));det=cs*cs-sn*sn
    assert abs(det)>.1
    local_x=(cs*extent.x-sn*extent.y)/det;local_y=(cs*extent.y-sn*extent.x)/det
    scale=u.Vector(local_x/b.box_extent.x,local_y/b.box_extent.y,extent.z/b.box_extent.z)
    assert min(scale.x,scale.y,scale.z)>0
    plans.append(dict(original=a,group=group,index=idx,center=origin,extent=extent,scale=scale,yaw=yaw,mesh=meshes[idx]))
assert len(plans)==11,len(plans)
originals=[snapshot(a) for a in hide]
(OUT/'original-visibility.json').write_text(json.dumps(originals,indent=2),encoding='utf-8')
spawned=[];report=[]
try:
    with u.ScopedEditorTransaction('Replace cartoon mountains with user generated realistic mountains'):
        for n,p in enumerate(plans):
            a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0),u.Rotator(pitch=0,yaw=p['yaw'],roll=0))
            spawned.append(a);a.modify()
            a.set_actor_label('%s Realistic %02d%s'%(p['group'],p['index']+1,' Extra' if p['original'].get_actor_label()=='Visual2' else ''))
            a.set_folder_path('RealisticMountains/'+p['group'])
            a.set_editor_property('tags',[u.Name(TAG)])
            c=a.static_mesh_component;c.modify();c.set_static_mesh(p['mesh'])
            c.set_collision_enabled(p['original'].static_mesh_component.get_collision_enabled())
            a.set_actor_scale3d(p['scale'])
            current_origin,_=a.get_actor_bounds(False)
            a.set_actor_location(p['center']-current_origin,False,False)
            new_origin,new_extent=a.get_actor_bounds(False)
            error=max(abs(x-y) for x,y in zip(v(new_origin)+v(new_extent),v(p['center'])+v(p['extent'])))
            assert error<.1,(p['group'],error)
            report.append(dict(original=p['original'].get_path_name(),replacement=a.get_path_name(),label=a.get_actor_label(),mesh=p['mesh'].get_path_name(),bounds_center=v(new_origin),bounds_extent=v(new_extent),bounds_error_cm=error,**transform(a)))
        for a in hide:
            a.modify();a.static_mesh_component.modify()
            a.static_mesh_component.set_visibility(False,True)
            a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
        for a in all_actors:
            if a.get_path_name() in protected:assert transform(a)==protected[a.get_path_name()],a.get_path_name()
        assert assets.save_directory('/Game/TianNanGe/RealisticMountains',False,True)
        assert level.save_current_level()
except Exception:
    for a in spawned:actors.destroy_actor(a)
    by_path={a.get_path_name():a for a in all_actors}
    for s in originals:
        a=by_path[s['path']];a.static_mesh_component.set_visibility(s['visible'],True)
        a.set_actor_hidden_in_game(s['hidden_game']);a.set_is_temporarily_hidden_in_editor(s['temporary_hidden'])
    raise
(OUT/'replacement.json').write_text(json.dumps(dict(world=world.get_path_name(),replacements=report,originals_hidden=len(hide),protected_actor_transforms_unchanged=True,scene_saved=True),indent=2),encoding='utf-8')
u.log('REALISTIC_MOUNTAINS_REPLACED '+str(len(report)))
