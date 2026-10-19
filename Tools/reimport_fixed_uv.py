import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
original=json.loads((root/'migration-result.json').read_text())
code=(root/'Tools/import_scene.py').read_text().split('\ntry:build()')[0]
exec(compile(code,'import_scene_definitions','exec'),globals())
report=original
u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/TianNanGe/Maps/TianNanGe_Main')
for mesh_id in json.loads((root/'Tools/uv-repair.json').read_text()):import_mesh(mesh_id,force=True)
for actor in actors.get_all_level_actors():
    if isinstance(actor,u.DirectionalLight):prop(actor.get_component_by_class(u.DirectionalLightComponent),'atmosphere_sun_light',actor.get_actor_label()=='Sun')
u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
save_report()
u.log('TIANNANGE_UV_REIMPORT_OK')
