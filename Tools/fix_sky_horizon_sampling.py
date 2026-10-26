"""Prevent vertical sky UV wrapping while retaining horizontal rotation/flow.

Only updates the sky texture's V addressing metadata. Requires the temporary
serialized rendering guard used for live asset edits; never moves a viewport.
"""
import datetime,hashlib,json,shutil
from pathlib import Path
import unreal as u

root=Path(__file__).resolve().parents[1]
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/TianNanGe_EasySnow.' in world.get_path_name()
assert u.SystemLibrary.get_console_variable_int_value('r.RHICmdBypass')==1,'Prepare the serialized asset update first.'
api=u.get_editor_subsystem(u.EditorActorSubsystem);assets=u.get_editor_subsystem(u.EditorAssetSubsystem);mel=u.MaterialEditingLibrary
actors=api.get_all_level_actors()
assert not any(isinstance(a,u.SceneCapture2D) for a in actors)
sky=next(a for a in actors if a.get_actor_label()=='Lookdev Chaotic winter sky 04')
mi=sky.static_mesh_component.get_material(0)
assert isinstance(mi,u.MaterialInstanceConstant),'Restore temporary sky comparison material first.'
texture=mel.get_material_instance_texture_parameter_value(mi,'SkyTexture');assert texture
source=root/'Content'/Path(texture.get_path_name().split('.')[0].removeprefix('/Game/')+'.uasset')
backup=root/'Backups'/('SkyHorizon_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True,exist_ok=False);shutil.copy2(source,backup/source.name)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
def snapshot():
 p,rot=level.get_level_viewport_camera_info(level.get_active_viewport_config_key())
 return {'transforms':{a.get_path_name():a.get_actor_transform().export_text() for a in actors},
  'view':[p.export_text(),rot.export_text()],'sky_material':sky.static_mesh_component.get_material(0).get_path_name(),
  'sky_scalars':{str(n):mel.get_material_instance_scalar_parameter_value(mi,n) for n in mel.get_scalar_parameter_names(mi)},
  'sky_vectors':{str(n):mel.get_material_instance_vector_parameter_value(mi,n).export_text() for n in mel.get_vector_parameter_names(mi)},
  'sky_textures':{str(n):mel.get_material_instance_texture_parameter_value(mi,n).get_path_name() for n in mel.get_texture_parameter_names(mi)},
  'cameras':{c.get_path_name():[c.field_of_view,c.post_process_settings.export_text()] for a in actors for c in a.get_components_by_class(u.CameraComponent)},
  'snow':{c.get_path_name():[c.is_visible(),c.is_active()] for a in actors for c in a.get_components_by_class(u.NiagaraComponent)}}
before=snapshot();old_y=texture.get_editor_property('address_y');old_x=texture.get_editor_property('address_x')
try:
 texture.modify();texture.set_editor_property('address_y',u.TextureAddress.TA_MIRROR)
 assert texture.get_editor_property('address_x')==old_x
 assert assets.save_loaded_asset(texture)
 assert snapshot()==before,'Scene or sky artist parameters changed during sampler update.'
except Exception:
 texture.set_editor_property('address_y',old_y)
 assets.save_loaded_asset(texture)
 raise
report={'texture':texture.get_path_name(),'old_address_y':str(old_y),'address_y':str(texture.get_editor_property('address_y')),
        'address_x':str(old_x),'backup':str(backup),'artist_parameters_preserved':True,'snapshot':before}
export=root/'Saved/ChaoticSkies/Seam/SkyTexture-after.tga'
task=u.AssetExportTask();task.object=texture;task.filename=str(export);task.exporter=u.TextureExporterTGA()
task.automated=True;task.prompt=False;task.replace_identical=True
assert u.Exporter.run_asset_export_task(task)
before_pixels=root/'Saved/ChaoticSkies/Seam/SkyTexture.tga'
if before_pixels.exists():
 report['source_pixels_preserved']=hashlib.sha256(before_pixels.read_bytes()).digest()==hashlib.sha256(export.read_bytes()).digest()
 assert report['source_pixels_preserved']
(root/'Saved/ChaoticSkies/horizon-sampling-fixed.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('SKY_HORIZON_SAMPLER_FIXED')
