import unreal as u,json
from pathlib import Path
data={'input_names_available':hasattr(u.MaterialEditingLibrary,'get_material_expression_input_names')}
for path in ['/Game/TianNanGe/Materials/M_006','/Game/TianNanGe/Lighting/M_Kloofendal_Sky']:
    mat=u.load_asset(path)
    expressions=u.MaterialEditingLibrary.get_material_expressions(mat) if hasattr(u.MaterialEditingLibrary,'get_material_expressions') else []
    data[path]=[(x.get_class().get_name(),list(u.MaterialEditingLibrary.get_material_expression_input_names(x))) for x in expressions]
(Path(__file__).resolve().parents[1] / 'Tools/probe-graph.json').write_text(json.dumps(data,indent=2))
