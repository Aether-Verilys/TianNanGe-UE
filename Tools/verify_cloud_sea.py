"""Verify imported noise, live native volumes, lighting controls and preserved scene state."""
import unreal as u,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];mel=u.MaterialEditingLibrary
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
before=json.loads((root/'Saved/cloud-weather-before.json').read_text())
after=json.loads((root/'Saved/cloud-weather-after.json').read_text())
assert before['preserved']==after['preserved'],'Camera or lights changed'
assert before['bridge']==after['bridge'],'Bridge bounds changed'
volumes=[a for a in actors if isinstance(a,u.HeterogeneousVolume) and a.get_actor_label().startswith('Cloud Volume - ')]
assert len(volumes)==10
for a in volumes:
    c=a.get_component_by_class(u.HeterogeneousVolumeComponent)
    assert c.visible and not c.hidden_in_game and c.cast_shadow
    assert c.get_material(0)
for a in actors:
    if isinstance(a,u.StaticMeshActor) and a.get_actor_label().startswith('Cloud Sea - '):assert not a.static_mesh_component.visible and a.static_mesh_component.hidden_in_game
m=u.load_asset('/Game/TianNanGe/CloudSea/Materials/M_CloudSea_LitVolume')
assert m.get_editor_property('material_domain')==u.MaterialDomain.MD_VOLUME
assert m.get_editor_property('used_with_heterogeneous_volumes')
zero=mel.get_material_property_input_node(m,u.MaterialProperty.MP_EMISSIVE_COLOR)
assert isinstance(zero,u.MaterialExpressionConstant) and zero.get_editor_property('r')==0.
textures=[]
registry=u.AssetRegistryHelpers.get_asset_registry()
for name,size in [('noiseShape',128),('noiseErosion',32)]:
    tex=u.load_asset('/Game/TianNanGe/CloudSea/Noise/VT_'+name)
    assert isinstance(tex,u.VolumeTexture) and not tex.get_editor_property('srgb')
    data=registry.get_asset_by_object_path(tex.get_path_name())
    assert data.get_tag_value('Dimensions')==f'{size}x{size}x{size}'
    textures.append({'name':name,'dimensions':[size]*3})
cvars={k:u.SystemLibrary.get_console_variable_float_value(k) for k in ['r.HeterogeneousVolumes.Shadows','r.HeterogeneousVolumes.IndirectLighting','r.HeterogeneousVolumes.IndirectLighting.Mode','r.HeterogeneousVolumes.LightType.Directional']}
assert all(v==1. for v in cvars.values())
for a in actors:
    if str(a.get_folder_path()) in ['EasySnow/Weather','EasySnow/Weather Layers']:
        assert not a.get_editor_property('Collision')
        if 'Ground' in a.get_actor_label():assert abs(a.get_editor_property('driftOpacity -')-.1)<.00001
        elif 'Distant' not in a.get_actor_label():assert abs(a.get_editor_property('NearParticleSizeMax -')-.28)<.00001
geometry=json.loads((root/'Saved/EasySnow/surface-geometry.json').read_text())
for item in geometry['materials']:
    mat=u.load_asset(item['material']);assert mat.get_editor_property('enable_tessellation')
    assert mat.get_editor_property('use_material_attributes')
    assert mat.get_editor_property('displacement_scaling').get_editor_property('magnitude')*item['maximum_actor_scale']<=.60001
for record in json.loads((root/'SourceAssets/CloudNoise/sources.json').read_text()):
    name='noiseShape' if record['volume_resolution'][0]==128 else 'noiseErosion'
    assert hashlib.sha256((root/'SourceAssets/CloudNoise'/(name+'.tga')).read_bytes()).hexdigest()==record['original_sha256']
assert json.loads((root/'Saved/EasySnow/CloudSea_Final_Low-capture.json').read_text())['success']
comparison=json.loads((root/'Saved/cloud-lighting-image-comparison.json').read_text())
assert comparison['left_cloud']['mean_absolute_change']>30 and comparison['hero_head_control']['mean_absolute_change']<1
report={'passed':True,'native_lit_cloud_volumes':len(volumes),'volume_textures':textures,'emissive':0,'lighting_cvars':cvars,'directional_light_and_camera_preserved':True,'snow_geometry_materials':len(geometry['materials']),'snow_collision':False,'near_drift_opacity':.1,'native_movie_capture':True,'lighting_image_comparison':comparison}
(root/'Saved/cloud-scene-final.json').write_text(json.dumps(report,indent=2))
