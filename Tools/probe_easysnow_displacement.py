import unreal as u,json
from pathlib import Path
m=u.load_asset('/Game/TianNanGe/EasySnowIntegration/Materials/M_006_EasySnow')
d={'properties':str(list(u.MaterialProperty)),'material_methods':[x for x in dir(m) if 'displace' in x or 'tess' in x], 'fields':{}}
d['enum_api']=dir(u.MaterialProperty)
try:d['cast']=str(u.MaterialProperty.cast(34))
except Exception as e:d['cast']=str(e)
try:
    data=m.get_editor_property('editor_only_data');d['editor_data']=str(data)
    d['input']=str(data.get_editor_property('displacement'))
except Exception as e:d['editor_data']=str(e)
for p in ['displacement','displacement_scaling','enable_tessellation']:
    try:d['fields'][p]=str(m.get_editor_property(p))
    except Exception as e:d['fields'][p]=str(e)
(Path(__file__).resolve().parents[1]/'Saved/EasySnow/displacement-api.json').write_text(json.dumps(d,indent=2))
