import unreal as u,json
from pathlib import Path
mel=u.MaterialEditingLibrary;m=u.load_asset('/Game/TianNanGe/EasySnowIntegration/Skies/M_Chaotic_WinterSky')
d={'root':str(mel.get_material_property_input_node(m,u.MaterialProperty.MP_EMISSIVE_COLOR)),'nodes':[]}
for e in mel.get_material_expressions(m):
    x={'id':e.get_name(),'class':e.get_class().get_name(),'inputs':{key:n.get_name() if n else None for key,n in zip(mel.get_material_expression_input_names(e),mel.get_inputs_for_material_expression(m,e))}}
    for k in ['parameter_name','default_value','texture','r','const_a','const_b','base','exponent']:
        try:x[k]=str(e.get_editor_property(k))
        except Exception:pass
    d['nodes'].append(x)
(Path(__file__).resolve().parents[1]/'Saved/ChaoticSkies/graph.json').write_text(json.dumps(d,indent=2))
