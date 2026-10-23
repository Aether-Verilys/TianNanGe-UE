"""Add intuitive density/core controls without rebuilding the approved cloud shape.

Run Live/cloud_prepare_safe_update.py first, then restore normal rendering after
shader compilation. The resulting Blueprint is standalone and uses native nodes.
"""
import ctypes
import datetime
import json
import shutil
from pathlib import Path
import unreal as u

r=Path(__file__).resolve().parents[1]
assert u.SystemLibrary.get_console_variable_int_value('r.RHICmdBypass')==1
assert u.SystemLibrary.get_console_variable_int_value('r.RHICmd.ParallelTranslate.Enable')==0
api=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
mel=u.MaterialEditingLibrary
actors=api.get_all_level_actors()
assert not any(isinstance(a,u.SceneCapture2D) for a in actors)
control=next(a for a in actors if a.get_actor_label()=='Cloud Sea Controls - TianNanGe')
volume=control.get_editor_property('TargetVolume')
mid=volume.get_material(0)
values={str(k):control.get_editor_property(str(k)) for k in mel.get_scalar_parameter_names(mid)}
color=control.get_editor_property('CloudAlbedo')
transforms={a.get_path_name():a.get_actor_transform().export_text() for a in actors}
bp=u.load_asset('/Game/TianNanGe/CloudSea/Blueprints/BP_CloudSeaController')
mi=u.load_asset('/Game/TianNanGe/CloudSea/Materials/MI_CloudSea_Layer')
m=mi.get_editor_property('parent')
custom=mel.get_material_property_input_node(m,u.MaterialProperty.MP_SUBSURFACE_COLOR)
backup=r/'Backups'/('CloudOpacityControls_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir()
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
shutil.copy2(r/'Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap',backup/'TianNanGe_EasySnow.umap')
for obj in [m,mi,bp]:
 assert assets.save_loaded_asset(obj)
 src=(r/'Content'/obj.get_path_name().split('.')[0].removeprefix('/Game/')).with_suffix('.uasset')
 shutil.copy2(src,backup/src.name)
(backup/'previous-shader.ush').write_text(custom.get_editor_property('code'))
(backup/'before.json').write_text(json.dumps({'scalars':values,'color':color.export_text(),'actors':transforms},indent=2))
new={'DensityMultiplier':values.get('DensityMultiplier',1.5),
     'InteriorDensityBoost':values.get('InteriorDensityBoost',4.)}
existing={str(n.get_editor_property('parameter_name')):n for n in mel.get_inputs_for_material_expression(m,custom) if isinstance(n,u.MaterialExpressionScalarParameter)}
m.modify();mi.modify()
for index,(name,value) in enumerate(new.items()):
 node=existing.get(name)
 if not node:
  node=mel.create_material_expression(m,u.MaterialExpressionScalarParameter,-700,3200+index*150)
  node.set_editor_property('parameter_name',name)
  inp=u.CustomInput();inp.set_editor_property('input_name',name)
  custom.set_editor_property('inputs',list(custom.get_editor_property('inputs'))+[inp])
  assert mel.connect_material_expressions(node,'',custom,name)
 node.set_editor_property('default_value',value)
 node.set_editor_property('group','01 高度与密度')
 node.set_editor_property('slider_min',0. if index==0 else 1.)
 node.set_editor_property('slider_max',20. if index==0 else 8.)
 node.set_editor_property('desc','整体密度倍率：0关闭，1原密度，2两倍。' if index==0 else '内部厚实度：云顶以下平滑增密，减少近处透底。')
 mel.set_material_instance_scalar_parameter_value(mi,name,value)
existing['Extinction'].set_editor_property('group','90 高级范围')
existing['Extinction'].set_editor_property('slider_max',3.)
custom.set_editor_property('code',(r/'Tools/Shaders/CloudSeaLayer.ush').read_text())
mel.recompile_material(m);mel.update_material_instance(mi)
assert assets.save_loaded_asset(m) and assets.save_loaded_asset(mi)
u._cloud_opacity_builder=ctypes.CDLL(str(r/'Saved/CloudOpacityBuilder/HostProject/Plugins/CloudBlueprintBuilder/Binaries/Win64/UnrealEditor-CloudBlueprintBuilder.dll'))
assert u._cloud_opacity_builder.AddCloudOpacityControls() in [0,1]
control=next(a for a in api.get_all_level_actors() if a.get_actor_label()=='Cloud Sea Controls - TianNanGe')
control.modify()
for name,value in {**values,**new}.items():control.set_editor_property(name,value)
control.set_editor_property('CloudAlbedo',color)
control.call_method('ApplyCloudParameters')
mid=volume.get_material(0)
assert all(abs(mid.get_scalar_parameter_value(k)-v)<1e-6 for k,v in {**values,**new}.items())
cdo=u.get_default_object(bp.generated_class())
for name,value in new.items():cdo.set_editor_property(name,value)
assert assets.save_loaded_asset(bp)
assert all(a.get_actor_transform().export_text()==transforms[a.get_path_name()] for a in api.get_all_level_actors())
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
if getattr(u,'_cloud_opacity_view_test',None):mid.set_scalar_parameter_value('WindSpeed',0.)
api.set_selected_level_actors([control])
(r/'Saved/cloud-opacity-applied.json').write_text(json.dumps({'passed':True,'backup':str(backup),'preserved_scalars':values,'new_controls':new,'original_transforms_preserved':True,'stats':mel.get_statistics(m).export_text()},indent=2))
