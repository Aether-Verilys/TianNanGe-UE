"""Import attributed open cloud noise atlases as genuine UE VolumeTexture assets."""
import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
dest='/Game/TianNanGe/CloudSea/Noise';report=[]
for stem,size in [('noiseShape',128),('noiseErosion',32)]:
    path=dest+'/T_'+stem+'_Atlas'
    tex=assets.load_asset(path)
    if not tex:
        task=u.AssetImportTask();task.set_editor_property('filename',str(root/'SourceAssets/CloudNoise'/(stem+'_atlas.png')))
        task.set_editor_property('destination_path',dest);task.set_editor_property('destination_name','T_'+stem+'_Atlas')
        task.set_editor_property('automated',True);task.set_editor_property('save',True)
        u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task]);tex=assets.load_asset(path)
    assert tex
    tex.set_editor_property('srgb',False);tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
    tex.set_editor_property('mip_gen_settings',u.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    assets.save_loaded_asset(tex)
    vp=dest+'/VT_'+stem
    volume=assets.load_asset(vp)
    if not volume:
        factory=u.VolumeTextureFactory()
        volume=u.AssetToolsHelpers.get_asset_tools().create_asset('VT_'+stem,dest,u.VolumeTexture,factory)
    assert volume
    volume.set_editor_property('Source2DTexture',tex)
    volume.set_editor_property('Source2DTileSizeX',size);volume.set_editor_property('Source2DTileSizeY',size)
    volume.set_editor_property('srgb',False);volume.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
    volume.set_editor_property('address_mode',u.TextureAddress.TA_WRAP)
    volume.set_editor_property('mip_gen_settings',u.TextureMipGenSettings.TMGS_SIMPLE_AVERAGE)
    assert assets.save_loaded_asset(volume)
    data=u.AssetRegistryHelpers.get_asset_registry().get_asset_by_object_path(volume.get_path_name())
    dimensions=data.get_tag_value('Dimensions')
    report.append({'texture':volume.get_path_name(),'dimensions':str(dimensions),'expected':[size]*3,'tile_size':[volume.get_editor_property('Source2DTileSizeX'),volume.get_editor_property('Source2DTileSizeY')],'srgb':volume.get_editor_property('srgb')})
(root/'Saved/cloud-noise-import.json').write_text(json.dumps(report,indent=2))
