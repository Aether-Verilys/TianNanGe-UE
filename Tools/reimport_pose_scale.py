import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
original=json.loads((root/'migration-result.json').read_text())
exec(compile((root/'Tools/import_scene.py').read_text().split('\ntry:build()')[0],'import_definitions','exec'),globals())
report=original
u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/TianNanGe/Maps/TianNanGe_Main')
for node in DATA['nodes']:
    if node['skinned']:import_mesh(node['mesh'],force=True)
u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
save_report()
u.log('TIANNANGE_POSE_SCALE_FIXED')
