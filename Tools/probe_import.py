import unreal as u,json,traceback
from pathlib import Path
root=(Path(__file__).resolve().parents[1] / 'Tools')
(root/'probe.obj').write_text('o probe\nv 0 0 0\nv 100 0 0\nv 0 100 0\nvt 0 0\nvt 1 0\nvt 0 1\nvn 0 0 1\nf 1/1/1 2/2/1 3/3/1\n')
r={}
for name,obj,props in [('mesh',u.FbxImportUI().static_mesh_import_data,['combine_meshes','convert_scene','convert_scene_unit','force_front_x_axis','generate_lightmap_u_vs']),('pp',u.PostProcessSettings(),['override_auto_exposure_apply_physical_camera_exposure','auto_exposure_apply_physical_camera_exposure','override_camera_iso','camera_iso','override_camera_shutter_speed','camera_shutter_speed','override_depth_of_field_fstop','depth_of_field_fstop'])]:
    r[name]={}
    for prop in props:
        try:r[name][prop]=str(obj.get_editor_property(prop))
        except Exception as e:r[name][prop]=str(e)
try:
    task=u.AssetImportTask();task.filename=str(root/'probe.obj');task.destination_path='/Game/MigrationProbe';task.destination_name='SM_Probe';task.automated=True;task.save=True
    options=u.FbxImportUI();options.import_materials=False;options.import_textures=False;options.automated_import_should_detect_type=False;options.mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH
    options.static_mesh_import_data.convert_scene=False;options.static_mesh_import_data.convert_scene_unit=False;task.options=options
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);r['import_paths']=list(task.imported_object_paths)
    for p in task.imported_object_paths:
        a=u.load_asset(p)
        if isinstance(a,u.StaticMesh):r['bounds']=str(a.get_bounds())
except Exception:r['error']=traceback.format_exc()
(root/'probe-import.json').write_text(json.dumps(r,indent=2))
