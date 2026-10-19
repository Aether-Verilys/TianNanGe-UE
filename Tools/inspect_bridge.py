import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=[]
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    f=str(a.get_folder_path()); label=a.get_actor_label()
    if 'Bridge' not in f and not isinstance(a,(u.CameraActor,u.DirectionalLight,u.SkyLight,u.PostProcessVolume,u.ExponentialHeightFog)):continue
    p=a.get_actor_location();r=a.get_actor_rotation();s=a.get_actor_scale3d()
    d=dict(label=label,folder=f,path=a.get_path_name(),position=[p.x,p.y,p.z],rotation=[r.pitch,r.yaw,r.roll],scale=[s.x,s.y,s.z],hidden=a.is_hidden_ed(),class_name=a.get_class().get_name())
    if isinstance(a,u.StaticMeshActor):
        c=a.static_mesh_component
        d.update(mesh=c.static_mesh.get_path_name() if c.static_mesh else None,materials=[m.get_path_name() if m else None for m in c.get_materials()])
    if isinstance(a,u.CameraActor):d.update(fov=a.camera_component.field_of_view,aspect=a.camera_component.aspect_ratio)
    if isinstance(a,u.DirectionalLight):
        c=a.get_component_by_class(u.DirectionalLightComponent);d.update(intensity=c.intensity,color=str(c.light_color))
    if isinstance(a,u.SkyLight):d['intensity']=a.get_component_by_class(u.SkyLightComponent).intensity
    out.append(d)
(root/'Tools/Live/bridge-before.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
