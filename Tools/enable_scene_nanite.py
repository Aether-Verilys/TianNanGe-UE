"""Enable Nanite on remaining render geometry, with fine bridge precision and full fallbacks."""
import unreal as u,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SourceAssets/SceneCleanup_20261027'
assert (OUT/'cleanup.json').exists(),'Back up and clean obsolete actors first.'
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
api=u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
state_path=OUT/'nanite-progress.json'
state=json.loads(state_path.read_text()) if state_path.exists() else dict(meshes={},exceptions=[],component_overrides=[])
command=globals().get('COMMAND',{})
limit=int(command.get('limit',1));processed=0
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(u.StaticMeshComponent):
        m=c.get_editor_property('static_mesh')
        if not m:continue
        path=m.get_path_name()
        if path in state['meshes']:continue
        if path.startswith('/Engine/EditorMeshes/'):
            exception=dict(mesh=path,reason='Editor camera visualization; not scene render geometry.')
            if exception not in state['exceptions']:state['exceptions'].append(exception)
            continue
        if any(material and material.get_base_material().get_editor_property('blend_mode') not in (u.BlendMode.BLEND_OPAQUE,u.BlendMode.BLEND_MASKED) for material in c.get_materials()):
            exception=dict(mesh=path,reason='Translucent sky material; retain current sky rendering.')
            if exception not in state['exceptions']:state['exceptions'].append(exception)
            continue
        assert path.startswith('/Game/'),path
        settings=m.get_editor_property('nanite_settings')
        was_enabled=settings.enabled
        if not was_enabled:
            if processed>=limit:continue
            settings.set_editor_property('enabled',True)
            settings.set_editor_property('keep_percent_triangles',1.0)
            settings.set_editor_property('trim_relative_error',0.0)
            settings.set_editor_property('fallback_percent_triangles',1.0)
            settings.set_editor_property('fallback_relative_error',0.0)
            settings.set_editor_property('fallback_target',u.NaniteFallbackTarget.PERCENT_TRIANGLES)
            if '/BridgeReference/' in path:
                # UE specifies step=2^(-precision) cm; 8 is 1/256 cm, NOT -8.
                settings.set_editor_property('position_precision',8)
                if any(n in m.get_name() for n in ('Snow_Rails','Snow_Caps','Icicles')):
                    settings.set_editor_property('shape_preservation',u.NaniteShapePreservation.PRESERVE_AREA)
            api.set_nanite_settings(m,settings,True)
            assert assets.save_loaded_asset(m)
            for material in c.get_materials():
                if material:
                    base=material.get_base_material()
                    if base.get_path_name().startswith('/Game/'):
                        assert assets.save_loaded_asset(base)
            processed+=1
        state['meshes'][path]=dict(mesh=path,previously_enabled=was_enabled,nanite_enabled=m.get_editor_property('nanite_settings').enabled,settings=str(m.get_editor_property('nanite_settings')),fallback_vertices=api.get_number_verts(m,0))
        state_path.write_text(json.dumps(state,indent=2),encoding='utf-8')
# Remove component-level fallback overrides only for the accepted render meshes.
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(u.StaticMeshComponent):
        m=c.get_editor_property('static_mesh')
        if not m or m.get_path_name() not in state['meshes']:continue
        for prop in ('disallow_nanite',):
            if c.get_editor_property(prop):
                c.modify();c.set_editor_property(prop,False)
                state['component_overrides'].append(dict(component=c.get_path_name(),property=prop,previous=True))
state_path.write_text(json.dumps(state,indent=2),encoding='utf-8')
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('SCENE_NANITE_BATCH '+str(processed))
