import unreal as u,json
from pathlib import Path
paths=u.get_editor_subsystem(u.EditorAssetSubsystem).list_assets('/Game/TianNanGe/Materials')+u.get_editor_subsystem(u.EditorAssetSubsystem).list_assets('/Game/TianNanGe/Lighting')
r={}
for path in paths:
    mat=u.load_asset(path)
    if not isinstance(mat,u.Material):continue
    r[path]={'base':str(u.MaterialEditingLibrary.get_material_property_input_node(mat,u.MaterialProperty.MP_BASE_COLOR)),'emissive':str(u.MaterialEditingLibrary.get_material_property_input_node(mat,u.MaterialProperty.MP_EMISSIVE_COLOR)),'nodes':[]}
    for n in u.MaterialEditingLibrary.get_material_expressions(mat):
        if isinstance(n,(u.MaterialExpressionOneMinus,u.MaterialExpressionCustom,u.MaterialExpressionTextureSampleParameterCube)):
            r[path]['nodes'].append({'type':n.get_class().get_name(),'inputs':[str(v) for v in u.MaterialEditingLibrary.get_inputs_for_material_expression(mat,n)]})
(Path(__file__).resolve().parents[1] / 'Tools/graph-audit.json').write_text(json.dumps(r,indent=2))
