"""Load the saved scene and export its transitive /Game package dependencies.

Run in UE's Python environment. Does not modify or save scene/assets.
Engine/plugin packages are supplied by UE and are recorded separately.
"""
import hashlib,json,runpy
from pathlib import Path
import unreal as u

root=Path(__file__).resolve().parents[1]
scene='/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow'
world=u.EditorLoadingAndSavingUtils.load_map(scene)
assert world and world.get_path_name().startswith(scene+'.')
registry=u.AssetRegistryHelpers.get_asset_registry()
registry.search_all_assets(True)
options=u.AssetRegistryDependencyOptions(
    include_soft_package_references=True,include_hard_package_references=True,
    include_searchable_names=False,include_soft_management_references=False,
    include_hard_management_references=False)
integration=root/'Content/TianNanGe/EasySnowIntegration'
roots=sorted({'/Game/'+p.relative_to(root/'Content').with_suffix('').as_posix()
              for p in integration.rglob('*') if p.suffix in ['.uasset','.umap']})
pending=list(roots);visited=set();external=set();files=[];missing=[]
while pending:
    package=pending.pop()
    if package in visited:continue
    visited.add(package)
    stem=root/'Content'/package.removeprefix('/Game/')
    asset=next((p for p in [stem.with_suffix('.uasset'),stem.with_suffix('.umap')] if p.is_file()),None)
    if asset is None:
        missing.append(package)
    else:
        for path in [asset,*[stem.with_suffix(s) for s in ['.ubulk','.uptnl','.uexp'] if stem.with_suffix(s).is_file()]]:
            files.append({'path':path.relative_to(root).as_posix(),'package':package,
                          'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    for dependency in registry.get_dependencies(package,options) or []:
        name=str(dependency)
        if name.startswith('/Game/'):pending.append(name)
        else:external.add(name)

actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
controls=[a for a in actors if a.get_class().get_name().startswith('BP_CloudSeaController')]
assert len(controls)==1
control=controls[0];volume=control.get_editor_property('TargetVolume')
assert volume and volume.is_visible()
material=volume.get_material(0)
assert isinstance(material,u.MaterialInstanceDynamic)
values={str(n):material.get_scalar_parameter_value(n) for n in u.MaterialEditingLibrary.get_scalar_parameter_names(material)}
assert all(abs(control.get_editor_property(n)-v)<1e-6 for n,v in values.items())
assert len(values)==16
assert not any(isinstance(a,u.SceneCapture2D) for a in actors)
runpy.run_path(str(root/'Tools/verify_cloud_sea.py'),run_name='__main__')
runpy.run_path(str(root/'Tools/verify_cloud_stability.py'),run_name='__main__')
report={'scene':scene,'package_roots':roots,'game_packages':len(visited),'files':sorted(files,key=lambda x:x['path']),
        'total_bytes':sum(f['bytes'] for f in files),'missing_packages':sorted(missing),
        'engine_and_plugin_packages':sorted(external),'actors':len(actors),
        'cloud_controller':control.get_actor_label(),'cloud_parameters':values,
        'verification':'Saved scene load and dependency audit using UE; no GPU rendering validation.'}
dest=root/'SourceAssets/SceneDependencies/TianNanGe_EasySnow.json'
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
assert not missing,missing
u.log('SCENE_DEPENDENCIES_VERIFIED '+json.dumps({'packages':len(visited),'files':len(files),'bytes':report['total_bytes']}))
