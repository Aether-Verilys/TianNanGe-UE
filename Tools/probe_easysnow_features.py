import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
m=u.load_asset('/Game/TianNanGe/EasySnowIntegration/Materials/M_PowderSnow_EasySnow')
d={'material_props':{},'static_switches':[], 'material_api':[x for x in dir(u.MaterialEditingLibrary) if 'switch' in x or 'parameter' in x]}
for p in ['enable_tessellation','displacement_scaling','max_world_position_offset_displacement','use_material_attributes']:
    try:d['material_props'][p]=str(m.get_editor_property(p))
    except Exception:pass
for key in ['get_static_switch_parameter_names','get_scalar_parameter_names']:
    if hasattr(u.MaterialEditingLibrary,key):d[key]=[str(x) for x in getattr(u.MaterialEditingLibrary,key)(m)]
mpc=u.load_asset('/Game/EasySnow/System/MP_WF_WorldData')
for typ in ['scalar_parameters','vector_parameters']:
    d[typ]=[{'name':str(v.get_editor_property('parameter_name')),'default':str(v.get_editor_property('default_value'))} for v in mpc.get_editor_property(typ)]
d['console_api']=[x for x in dir(u) if 'console' in x.lower()]
(root/'Saved/EasySnow/features.json').write_text(json.dumps(d,indent=2))
