import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'Transfer_BridgeReference/manifest.json').read_text())
s=u.get_editor_subsystem(u.StaticMeshEditorSubsystem);assets=u.get_editor_subsystem(u.EditorAssetSubsystem);report=[]
for info in data['meshes']:
    mesh=u.load_asset('/Game/TianNanGe/BridgeReference/Meshes/'+info['name'])
    settings=mesh.get_editor_property('nanite_settings');settings.set_editor_property('enabled',True)
    settings.set_editor_property('fallback_relative_error',0.0);settings.set_editor_property('fallback_percent_triangles',1.0);settings.set_editor_property('position_precision',8)
    settings.set_editor_property('keep_percent_triangles',1.0);settings.set_editor_property('trim_relative_error',0.0)
    settings.set_editor_property('fallback_target',u.NaniteFallbackTarget.PERCENT_TRIANGLES)
    if any(part in info['name'] for part in ('Snow_Rails','Snow_Caps','Icicles')):
        settings.set_editor_property('shape_preservation',u.NaniteShapePreservation.PRESERVE_AREA)
    s.set_nanite_settings(mesh,settings,True);assets.save_loaded_asset(mesh)
    report.append({'mesh':mesh.get_path_name(),'render_vertices':s.get_number_verts(mesh,0),'fallback_relative_error':mesh.get_editor_property('nanite_settings').get_editor_property('fallback_relative_error')})
(root/'Tools/Live/bridge-precision.json').write_text(json.dumps(report,indent=2))
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
