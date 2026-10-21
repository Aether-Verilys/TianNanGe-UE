"""Prepare a local trial map in an offline UE process, avoiding live UWorld duplication."""
import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
base=root/'Content/TianNanGe/Maps/TianNanGe_ReferenceLook.umap'
world=u.EditorLoadingAndSavingUtils.load_map(str(base));assert world
target='/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow'
assert u.EditorLoadingAndSavingUtils.save_map(world,target)
(root/'Saved/EasySnow/prepared.json').write_text(json.dumps({'map':target,'saved':True}))
