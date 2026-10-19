import unreal as u,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
report={}
for path in assets.list_assets('/Game/TianNanGe/Revision_fdf5e67',recursive=True):
    asset=assets.load_asset(path)
    if not isinstance(asset,u.Material):continue
    try:asset.set_editor_property('used_with_nanite',True)
    except Exception:pass
    assets.save_loaded_asset(asset)
    report[asset.get_name()]={'is_sky':asset.get_editor_property('is_sky'),'shading_model':str(asset.get_editor_property('shading_model')),'used_with_nanite':asset.get_editor_property('used_with_nanite')}
u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(ROOT/'Tools/Live/material-render-status.json').write_text(json.dumps(report,indent=2))
