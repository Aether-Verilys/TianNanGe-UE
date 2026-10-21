import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];mesh=u.load_asset('/Game/Chaotic_Skies_II/Meshes/SM_Skybox_Mesh');assert mesh
mel=u.MaterialEditingLibrary;d={'bounds':str(mesh.get_bounds()),'slots':[],'top':{}}
for s in mesh.get_editor_property('static_materials'):
    d['slots'].append({'name':str(s.get_editor_property('material_slot_name')),'material':str(s.get_editor_property('material_interface'))})
m=u.load_asset('/Game/Chaotic_Skies_II/Materials/Instances/MI_Flowmap_top_Inst_04')
d['top']={'parent':str(m.get_editor_property('parent')),'scalar':{str(n):mel.get_material_instance_scalar_parameter_value(m,n) for n in mel.get_scalar_parameter_names(m)},'texture':{str(n):str(mel.get_material_instance_texture_parameter_value(m,n)) for n in mel.get_texture_parameter_names(m)}}
(root/'Saved/ChaoticSkies/mesh.json').write_text(json.dumps(d,indent=2))
