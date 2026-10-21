import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'Saved/ChaoticSkies';out.mkdir(exist_ok=True)
u.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous(['/Game/Chaotic_Skies_II'],True)
mel=u.MaterialEditingLibrary;report={'textures':[],'materials':[],'sky_actors':[]}
for i in range(1,7):
    t=u.load_asset('/Game/Chaotic_Skies_II/Textures/Skies/T_chaotic_sky_II_'+str(i).zfill(2));assert t
    d={'name':t.get_name(),'class':t.get_class().get_name(),'width':t.blueprint_get_size_x(),'height':t.blueprint_get_size_y(),'srgb':t.get_editor_property('srgb')}
    task=u.AssetExportTask();task.object=t;task.filename=str(out/(t.get_name()+'.png'));task.automated=True;task.prompt=False;task.replace_identical=True
    task.exporter=u.TextureExporterPNG();d['exported']=u.Exporter.run_asset_export_task(task)
    report['textures'].append(d)
for i in range(1,7):
    m=u.load_asset('/Game/Chaotic_Skies_II/Materials/Instances/MI_Flowmap_Inst_'+str(i).zfill(2));assert m
    report['materials'].append({'name':m.get_name(),'parent':str(m.get_editor_property('parent')),'scalar':{str(n):mel.get_material_instance_scalar_parameter_value(m,n) for n in mel.get_scalar_parameter_names(m)},'vector':{str(n):str(mel.get_material_instance_vector_parameter_value(m,n)) for n in mel.get_vector_parameter_names(m)},'texture':{str(n):str(mel.get_material_instance_texture_parameter_value(m,n)) for n in mel.get_texture_parameter_names(m)}})
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    if isinstance(a,u.StaticMeshActor) and ('sky' in a.get_actor_label().lower()):
        report['sky_actors'].append({'label':a.get_actor_label(),'name':a.get_name(),'position':str(a.get_actor_location()),'scale':str(a.get_actor_scale3d()),'materials':[str(m) for m in a.static_mesh_component.get_materials()]})
(out/'assets.json').write_text(json.dumps(report,indent=2))
