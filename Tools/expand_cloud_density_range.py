"""Change slider metadata only; preserve every live controller value."""
import ctypes
import datetime
import json
import shutil
import time
from pathlib import Path
import unreal as u

r=Path(__file__).resolve().parents[1]
assert u.SystemLibrary.get_console_variable_int_value('r.RHICmdBypass')==1
api=u.get_editor_subsystem(u.EditorActorSubsystem);assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
control=next(a for a in api.get_all_level_actors() if a.get_actor_label()=='Cloud Sea Controls - TianNanGe')
volume=control.get_editor_property('TargetVolume');mid=volume.get_material(0)
mel=u.MaterialEditingLibrary
values={str(k):control.get_editor_property(str(k)) for k in mel.get_scalar_parameter_names(mid)}
color=control.get_editor_property('CloudAlbedo').export_text()
bp=u.load_asset('/Game/TianNanGe/CloudSea/Blueprints/BP_CloudSeaController')
m=u.load_asset('/Game/TianNanGe/CloudSea/Materials/M_CloudSea_Layer')
backup=r/'Backups'/('CloudDensityRange_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir()
for obj in [bp,m]:
 assert assets.save_loaded_asset(obj)
 src=(r/'Content'/obj.get_path_name().split('.')[0].removeprefix('/Game/')).with_suffix('.uasset')
 shutil.copy2(src,backup/src.name)
builder=u._cloud_opacity_builder
builder.SetCloudControlMeta.argtypes=[ctypes.c_wchar_p]*5
builder.SetCloudControlMeta('DensityMultiplier','Cloud Sea|01 高度与密度',
 '0关闭云，1为原有整体密度，2为两倍。滑条范围0至20；提高整体浓度，不改变云形起伏。','0','20')
assert u.BlueprintEditorLibrary.compile_blueprint(bp)
custom=mel.get_material_property_input_node(m,u.MaterialProperty.MP_SUBSURFACE_COLOR)
node=next(n for n in mel.get_inputs_for_material_expression(m,custom) if isinstance(n,u.MaterialExpressionScalarParameter) and str(n.get_editor_property('parameter_name'))=='DensityMultiplier')
m.modify();node.set_editor_property('slider_max',20.)
assert assets.save_loaded_asset(m) and assets.save_loaded_asset(bp)
control=next(a for a in api.get_all_level_actors() if a.get_actor_label()=='Cloud Sea Controls - TianNanGe')
assert all(abs(control.get_editor_property(k)-v)<1e-6 for k,v in values.items())
assert control.get_editor_property('CloudAlbedo').export_text()==color
assert all(abs(volume.get_material(0).get_scalar_parameter_value(k)-v)<1e-6 for k,v in values.items())
assert node.get_editor_property('slider_max')==20.
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
api.set_selected_level_actors([control])
(r/'Saved/cloud-density-range-expanded.json').write_text(json.dumps({'time':time.time(),'passed':True,
 'slider_min':0,'slider_max':20,'current_density_preserved':values['DensityMultiplier'],
 'all_values_preserved':values,'backup':str(backup)},indent=2))
