"""Read-only live scene/component inventory and project mesh reference audit."""
import unreal as u, json, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SourceAssets/SceneCleanup_20261027';OUT.mkdir(parents=True,exist_ok=True)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.')
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
registry=u.AssetRegistryHelpers.get_asset_registry()
options=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
mesh_api=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
def vec(v):return [v.x,v.y,v.z]
def get(obj,k):
    try:return str(obj.get_editor_property(k))
    except Exception as e:return 'unavailable: '+str(e)
mesh_info={};rows=[];skeletal=[]
for a in actors.get_all_level_actors():
    r=a.get_actor_rotation()
    row=dict(path=a.get_path_name(),label=a.get_actor_label(),folder=str(a.get_folder_path()),class_name=a.get_class().get_name(),location=vec(a.get_actor_location()),rotation=[r.pitch,r.yaw,r.roll],scale=vec(a.get_actor_scale3d()),hidden_game=a.get_editor_property('hidden'),hidden_editor=a.is_temporarily_hidden_in_editor(),components=[])
    for c in a.get_components_by_class(u.StaticMeshComponent):
        m=c.get_editor_property('static_mesh')
        if not m:continue
        mats=[]
        for material in c.get_materials():
            base=material.get_base_material() if material else None
            mats.append(dict(asset=material.get_path_name() if material else None,base=base.get_path_name() if base else None,blend=get(base,'blend_mode') if base else None,domain=get(base,'material_domain') if base else None))
        row['components'].append(dict(path=c.get_path_name(),mesh=m.get_path_name(),visible=c.get_editor_property('visible'),hidden_game=c.get_editor_property('hidden_in_game'),materials=mats,component_class=c.get_class().get_name()))
        if m.get_path_name() not in mesh_info:
            settings=m.get_editor_property('nanite_settings')
            mesh_info[m.get_path_name()]=dict(mesh=m.get_path_name(),nanite_enabled=settings.enabled,nanite_settings=str(settings),referencers=[str(x) for x in registry.get_referencers(m.get_path_name().split('.')[0],options)],triangles=m.get_num_triangles(0) if hasattr(m,'get_num_triangles') else None,vertices=mesh_api.get_number_verts(m,0))
    for c in a.get_components_by_class(u.SkeletalMeshComponent):
        skeletal.append(dict(actor=a.get_path_name(),component=c.get_path_name(),mesh=str(c.get_editor_property('skeletal_mesh_asset'))))
    rows.append(row)
project_meshes=[]
for data in registry.get_assets_by_path('/Game/TianNanGe',recursive=True):
    if str(data.asset_class_path.asset_name)!='StaticMesh':continue
    package=str(data.package_name)
    project_meshes.append(dict(package=package,asset_name=str(data.asset_name),referencers=[str(x) for x in registry.get_referencers(package,options)]))
(OUT/'audit-before.json').write_text(json.dumps(dict(world=world.get_path_name(),actors=rows,meshes=mesh_info,project_meshes=project_meshes,skeletal=skeletal),indent=2),encoding='utf-8')
u.log('SCENE_CLEANUP_NANITE_AUDIT_COMPLETE')
