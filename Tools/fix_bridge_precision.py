import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'Transfer_BridgeReference/manifest.json').read_text())
s=u.get_editor_subsystem(u.StaticMeshEditorSubsystem);assets=u.get_editor_subsystem(u.EditorAssetSubsystem);report=[]
for info in data['meshes']:
    mesh=u.load_asset('/Game/TianNanGe/BridgeReference/Meshes/'+info['name'])
    settings=mesh.get_editor_property('nanite_settings');settings.set_editor_property('enabled',False)
    settings.set_editor_property('fallback_relative_error',0.0);settings.set_editor_property('fallback_percent_triangles',1.0);settings.set_editor_property('position_precision',-2147483648)
    s.set_nanite_settings(mesh,settings,True);assets.save_loaded_asset(mesh)
    report.append({'mesh':mesh.get_path_name(),'render_vertices':s.get_number_verts(mesh,0),'fallback_relative_error':mesh.get_editor_property('nanite_settings').get_editor_property('fallback_relative_error')})
(root/'Tools/Live/bridge-precision.json').write_text(json.dumps(report,indent=2))
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
