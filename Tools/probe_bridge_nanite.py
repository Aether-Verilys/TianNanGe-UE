import unreal as u,json
from pathlib import Path
s=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
out={}
for name in ['SM_Bridge_Snow_Caps','SM_Bridge_Snow_Rails','SM_Bridge_Icicles']:
    m=u.load_asset('/Game/TianNanGe/BridgeReference/Meshes/'+name)
    d={'nanite':str(m.get_editor_property('nanite_settings')),'materials':str(m.static_materials),'lods':s.get_lod_count(m)}
    for method in ['get_number_verts','get_number_triangles']:
        if hasattr(s,method):d[method]=getattr(s,method)(m,0)
    out[name]=d
out['api']=[x for x in dir(s) if 'nanite' in x or 'triangle' in x or 'vert' in x]
((Path(__file__).resolve().parents[1] / 'Tools/Live')/'bridge-nanite.json').write_text(json.dumps(out,indent=2))
