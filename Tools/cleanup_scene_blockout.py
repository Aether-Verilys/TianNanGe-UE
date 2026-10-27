"""Remove only invisible, superseded whitebox actors; back up scene and bridge assets first."""
import unreal as u,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SourceAssets/SceneCleanup_20261027'
BACKUP=ROOT/'Backups/SceneCleanupNanite_20261027'
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.')
assert not (OUT/'cleanup.json').exists(),'Cleanup already completed; inspect its report instead of deleting again.'
audit=json.loads((OUT/'audit-before.json').read_text())
all_actors=list(actors.get_all_level_actors());by_path={a.get_path_name():a for a in all_actors}
legacy_bridge={'TianNanGe_Blockout/Bridge','TianNanGe_Blockout/Bridge/ExtendedRailings','Lookdev/Bridge snow'}
delete=[]
for s in audit['actors']:
    if not s['components'] or not s['hidden_game'] or any(c['visible'] for c in s['components']):continue
    if s['folder'] in legacy_bridge or s['folder'].startswith('TianNanGe_Blockout/Mountains/'):
        a=by_path[s['path']]
        assert isinstance(a,u.StaticMeshActor)
        assert a.get_editor_property('hidden') and all(not c.get_editor_property('visible') for c in a.get_components_by_class(u.StaticMeshComponent))
        delete.append(s)
assert len(delete)==323,len(delete)
delete_paths={s['path'] for s in delete}
for s in delete:
    assert all(c.get_path_name() in delete_paths for c in by_path[s['path']].get_attached_actors()),s['path']
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
assert not BACKUP.exists(),'Preserve the existing backup; do not overwrite it.'
BACKUP.mkdir(parents=True)
map_file=ROOT/'Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap'
shutil.copy2(map_file,BACKUP/map_file.name)
bridge=[]
for p,m in audit['meshes'].items():
    if '/BridgeReference/Meshes/' not in p:continue
    asset=assets.load_asset(p);assert assets.save_loaded_asset(asset)
    stem=ROOT/'Content'/p.split('.')[0].removeprefix('/Game/')
    for ext in ('.uasset','.uexp','.ubulk','.uptnl'):
        source=stem.with_suffix(ext)
        if source.exists():
            dest=BACKUP/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    bridge.append(p)
(OUT/'backup.json').write_text(json.dumps(dict(path=str(BACKUP),map=str(map_file),bridge_meshes=bridge),indent=2),encoding='utf-8')
with u.ScopedEditorTransaction('Remove superseded bridge and mountain whiteboxes'):
    for s in delete:assert actors.destroy_actor(by_path[s['path']]),s['path']
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
registry=u.AssetRegistryHelpers.get_asset_registry()
options=u.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)
unused_meshes=[];shared_meshes=[]
used={c['mesh'].split('.')[0] for s in delete for c in s['components']}
for package in sorted(used):
    if not package.startswith('/Game/TianNanGe/'):continue
    refs=[str(r) for r in registry.get_referencers(package,options)]
    (shared_meshes if refs else unused_meshes).append(dict(package=package,referencers=refs))
# No force deletion: shared meshes belong to retained historical maps and live geometry.
deleted_assets=[]
for m in unused_meshes:
    package=m['package']
    assert not assets.find_package_referencers_for_asset(package,True),package
    stem=ROOT/'Content'/package.removeprefix('/Game/')
    for ext in ('.uasset','.uexp','.ubulk','.uptnl'):
        source=stem.with_suffix(ext)
        if source.exists():
            dest=BACKUP/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    assert assets.delete_asset(package),package
    deleted_assets.append(package)
report=dict(world=world.get_path_name(),backup=str(BACKUP),deleted_actor_count=len(delete),deleted_actors=delete,deleted_assets=deleted_assets,shared_assets_preserved=shared_meshes,scene_saved=True)
(OUT/'cleanup.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('SCENE_BLOCKOUT_CLEANED '+str(len(delete)))
