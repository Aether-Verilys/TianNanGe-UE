"""Expose grouped cloud instance controls while preserving the current appearance."""
import unreal as u,json,datetime,shutil
from pathlib import Path
r=Path(__file__).resolve().parents[1];mel=u.MaterialEditingLibrary
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
m=u.load_asset('/Game/TianNanGe/CloudSea/Materials/M_CloudSea_Layer')
mi=u.load_asset('/Game/TianNanGe/CloudSea/Materials/MI_CloudSea_Layer')
assert m and mi
# name: group, slider min/max, tooltip, default for newly exposed controls
spec={
'SeaLevel':('01 高度与密度',-500,300,'云海平均高度，单位 cm；整体升降优先调整此项。',25),
'Extinction':('90 高级范围',0,3,'基础消光系数。保留原始参数兼容性；日常请调整体密度倍率和内部厚实度。',.065),
'DensityMultiplier':('01 高度与密度',0,20,'整体密度倍率：0关闭，1为原密度，2为两倍；不改变云形起伏。',1.5),
'InteriorDensityBoost':('01 高度与密度',1,8,'内部厚实度：1为原密度，4为四倍；云顶以下平滑增强，减少近处看穿。',4),
'SurfaceSoftness':('01 高度与密度',5,150,'云顶过渡半宽 cm；越小边缘越紧实，越大越柔和。',35),
'WaveHeight':('02 云顶形态',0,150,'大尺度起伏幅度 cm；当前平缓云海建议从 20–60 调整。',40),
'WavePeriod':('02 云顶形态',300,5000,'大尺度起伏的水平周期 cm；越大越舒展。',1800),
'BillowPeriod':('02 云顶形态',100,2000,'中尺度卷动的水平周期 cm。',550),
'BillowStrength':('02 云顶形态',0,1,'中尺度起伏相对大尺度起伏的强度；0 关闭中尺度起伏。',.6),
'ErosionDepth':('03 细节',0,100,'细节侵蚀深度 cm；越大越破碎。',45),
'DetailPeriod':('03 细节',30,600,'侵蚀纹理周期 cm；越小细节越细密。',170),
'WindSpeed':('04 流动',0,40,'噪声流动速度；0 停止流动。',4),
'WindRotationDegrees':('04 流动',-180,180,'风向相对原方向的旋转角，单位度；0 保持原风向。',0),
'BridgeClearanceStrength':('05 桥面避让',0,1,'桥面附近减密强度；1 为原效果，0 关闭避让。',1),
'BridgeClearanceWidth':('05 桥面避让',.25,2,'避让宽度相对原值的倍率；1 保持原范围。',1),
'EdgeFade':('90 高级范围',100,2000,'体积水平边缘淡出宽度 cm；通常无需调整。',900)}
old_names={str(k) for k in mel.get_scalar_parameter_names(m)}
before={k:mel.get_material_instance_scalar_parameter_value(mi,k) for k in old_names}
backup=r/'Backups'/('CloudControls_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True)
for obj in [m,mi]:
    assets.save_loaded_asset(obj)
    shutil.copy2((r/'Content'/obj.get_path_name().split('.')[0].removeprefix('/Game/')).with_suffix('.uasset'),backup/(obj.get_name()+'.uasset'))
(backup/'parameters-before.json').write_text(json.dumps(before,indent=2))
custom=mel.get_material_property_input_node(m,u.MaterialProperty.MP_SUBSURFACE_COLOR)
existing={str(n.get_editor_property('parameter_name')):n for n in mel.get_inputs_for_material_expression(m,custom) if isinstance(n,u.MaterialExpressionScalarParameter)}
m.modify();mi.modify()
for index,(name,(group,lo,hi,desc,default)) in enumerate(spec.items()):
    node=existing.get(name)
    if not node:
        node=mel.create_material_expression(m,u.MaterialExpressionScalarParameter,-700,1600+index*100)
        node.set_editor_property('parameter_name',name);node.set_editor_property('default_value',default)
        inp=u.CustomInput();inp.set_editor_property('input_name',name)
        custom.set_editor_property('inputs',list(custom.get_editor_property('inputs'))+[inp])
        assert mel.connect_material_expressions(node,'',custom,name)
    for k,v in {'group':group,'slider_min':float(lo),'slider_max':float(hi),'desc':desc,'sort_priority':index}.items():node.set_editor_property(k,v)
    mel.set_material_instance_scalar_parameter_value(mi,name,before.get(name,default))
custom.set_editor_property('code',(r/'Tools/Shaders/CloudSeaLayer.ush').read_text())
for n in mel.get_inputs_for_material_expression(m,custom):
    if isinstance(n,u.MaterialExpressionVectorParameter):
        n.set_editor_property('group','90 高级范围')
        n.set_editor_property('desc','体积世界范围，需与 Actor 范围同步；仅调云的外观时无需修改。')
color=mel.get_material_property_input_node(m,u.MaterialProperty.MP_BASE_COLOR)
color.set_editor_property('group','06 颜色');color.set_editor_property('desc','云的散射颜色，仍接受场景真实光照。')
mel.recompile_material(m);mel.update_material_instance(mi)
assert assets.save_loaded_asset(m) and assets.save_loaded_asset(mi)
assert all(mel.get_material_instance_scalar_parameter_value(mi,k)==v for k,v in before.items())
report={'passed':True,'backup':str(backup),'preserved_existing_parameters':before,'controls':{k:{'group':v[0],'range':[v[1],v[2]],'description':v[3],'value':mel.get_material_instance_scalar_parameter_value(mi,k)} for k,v in spec.items()}}
(r/'Saved/cloud-controls.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
if globals().get('COMMAND',{}).get('open',True):u.get_editor_subsystem(u.AssetEditorSubsystem).open_editor_for_assets([mi])
