"""Record the current scene without changing actors, lights or camera."""
import unreal as u, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SourceAssets/RealisticMountains/UserGenerated_20261027'
OUT.mkdir(parents=True,exist_ok=True)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.'),world.get_path_name()
def v(x):return [x.x,x.y,x.z]
def r(x):return [x.pitch,x.yaw,x.roll]
records=[]
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    item=dict(path=a.get_path_name(),label=a.get_actor_label(),folder=str(a.get_folder_path()),class_name=a.get_class().get_name(),location=v(a.get_actor_location()),rotation=r(a.get_actor_rotation()),scale=v(a.get_actor_scale3d()))
    if isinstance(a,u.StaticMeshActor):
        c=a.static_mesh_component;m=c.static_mesh
        origin,extent=a.get_actor_bounds(False)
        item.update(mesh=m.get_path_name() if m else None,origin=v(origin),extent=v(extent),visible=c.get_editor_property('visible'),hidden_game=a.get_editor_property('hidden'),materials=[x.get_path_name() if x else None for x in c.get_materials()])
        if m:
            b=m.get_bounds();item.update(mesh_origin=v(b.origin),mesh_extent=v(b.box_extent))
    if isinstance(a,u.CameraActor):item['camera_fov']=a.camera_component.field_of_view
    records.append(item)
(OUT/'scene-before.json').write_text(json.dumps(dict(world=world.get_path_name(),actors=records),indent=2),encoding='utf-8')
u.log('MOUNTAIN_SCENE_INVENTORY_SAVED')
