"""Back up and remove only the unused legacy ellipsoid-cloud setup."""
import unreal as u,json,shutil,datetime
from pathlib import Path
r=Path(__file__).resolve().parents[1]
assets=u.get_editor_subsystem(u.EditorAssetSubsystem);api=u.get_editor_subsystem(u.EditorActorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/TianNanGe_EasySnow.' in world.get_path_name()
actors=api.get_all_level_actors()
layer=next(a for a in actors if a.get_actor_label()=='Cloud Sea Layer - TianNanGe')
active_material=layer.get_component_by_class(u.HeterogeneousVolumeComponent).get_material(0)
assert active_material.get_name()=='MI_CloudSea_Layer'
keep={'M_CloudSea_Layer','MI_CloudSea_Layer'}
old=assets.list_assets('/Game/TianNanGe/CloudSea/Materials',recursive=False,include_folder=False)
old=[p for p in old if p.split('.')[-1] not in keep]
assert all(p.split('.')[-1] in ['M_CloudSea_LitVolume','M_CloudSea_Raymarch'] or p.split('.')[-1].startswith(('MI_CloudSea_L_','MI_CloudSea_R_')) for p in old)
packages={p.split('.')[0] for p in old}
map_package=world.get_path_name().split('.')[0]
for p in old:
    refs=set(str(x) for x in assets.find_package_referencers_for_asset(p,False))
    assert refs <= packages|{map_package},(p,refs-packages-{map_package})
backup=r/'Backups'/('LegacyCloudCleanup_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
map_file=r/'Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap'
shutil.copy2(map_file,backup/map_file.name)
for p in old:
    obj=assets.load_asset(p);assert assets.save_loaded_asset(obj)
    src=(r/'Content'/p.split('.')[0].removeprefix('/Game/')).with_suffix('.uasset')
    shutil.copy2(src,backup/src.name)
preserved={a.get_path_name():a.get_actor_transform().export_text() for a in actors if not a.get_actor_label().startswith(('Cloud Volume - ','Cloud Sea - '))}
deleted_actors=[]
for a in actors:
    if a.get_actor_label().startswith(('Cloud Volume - ','Cloud Sea - ')):
        assert isinstance(a,(u.HeterogeneousVolume,u.StaticMeshActor))
        deleted_actors.append(a.get_actor_label());assert api.destroy_actor(a)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
# Delete children first; their parent materials become unreferenced afterwards.
deleted=[]
for p in sorted(old,key=lambda p:0 if p.split('.')[-1].startswith('MI_') else 1):
    refs=set(str(x) for x in assets.find_package_referencers_for_asset(p,True))
    assert not (refs-packages),(p,refs)
    assert assets.delete_asset(p),p
    deleted.append(p)
assert assets.does_asset_exist('/Game/TianNanGe/CloudSea/Materials/MI_CloudSea_Layer')
for name in ['VT_noiseShape','VT_noiseErosion']:
    assert assets.does_asset_exist('/Game/TianNanGe/CloudSea/Noise/'+name)
remaining=api.get_all_level_actors()
assert all(a.get_actor_transform().export_text()==preserved[a.get_path_name()] for a in remaining)
assert not any(a.get_actor_label().startswith(('Cloud Volume - ','Cloud Sea - ')) for a in remaining)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(r/'Saved/cloud-cleanup.json').write_text(json.dumps({'passed':True,'backup':str(backup),'deleted_actors':deleted_actors,'deleted_assets':deleted,'active_layer_and_shared_noise_preserved':True,'other_transforms_preserved':True},indent=2))
