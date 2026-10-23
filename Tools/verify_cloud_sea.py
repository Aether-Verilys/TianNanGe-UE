"""Verify the current cloud layer, parameter controls and absence of legacy banks."""
import unreal as u,json,hashlib,ast
from pathlib import Path
r=Path(__file__).resolve().parents[1];mel=u.MaterialEditingLibrary
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
assert not any(a.get_actor_label().startswith(('Cloud Volume - ','Cloud Sea - ')) for a in actors)
active=[a for a in actors if isinstance(a,u.HeterogeneousVolume) and a.get_component_by_class(u.HeterogeneousVolumeComponent).visible]
assert len(active)==1, 'Expected one visible native cloud layer.'
a=active[0];c=a.get_component_by_class(u.HeterogeneousVolumeComponent);material=c.get_material(0)
controller=next((x for x in actors if x.get_actor_label()=='Cloud Sea Controls - TianNanGe'),None)
if controller:
 assert controller.get_editor_property('TargetVolume')==c
 assert isinstance(material,u.MaterialInstanceDynamic)
 mi=material.get_editor_property('parent')
else:
 mi=material
m=mi.get_editor_property('parent')
assert mi.get_name()=='MI_CloudSea_Layer' and m.get_name()=='M_CloudSea_Layer'
assert m.get_editor_property('material_domain')==u.MaterialDomain.MD_VOLUME
assert m.get_editor_property('used_with_heterogeneous_volumes')
zero=mel.get_material_property_input_node(m,u.MaterialProperty.MP_EMISSIVE_COLOR)
assert isinstance(zero,u.MaterialExpressionConstant) and zero.get_editor_property('r')==0.
custom=mel.get_material_property_input_node(m,u.MaterialProperty.MP_SUBSURFACE_COLOR)
assert custom.get_editor_property('code')==(r/'Tools/Shaders/CloudSeaLayer.ush').read_text()
tree=ast.parse((r/'Tools/configure_cloud_controls.py').read_text(encoding='utf-8'))
spec=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='spec' for t in n.targets))
controls={name:{'group':s[0]} for name,s in spec.items()}
nodes={str(n.get_editor_property('parameter_name')):n for n in mel.get_inputs_for_material_expression(m,custom) if isinstance(n,u.MaterialExpressionScalarParameter)}
assert len(controls)==16
for name,meta in controls.items():
 n=nodes[name]
 assert str(n.get_editor_property('group'))==meta['group'] and n.get_editor_property('desc')
 assert n.get_editor_property('slider_max')>n.get_editor_property('slider_min')
 if controller:
  assert abs(material.get_scalar_parameter_value(name)-controller.get_editor_property(name))<.00001
for name,size in [('noiseShape',128),('noiseErosion',32)]:
 tex=u.load_asset('/Game/TianNanGe/CloudSea/Noise/VT_'+name)
 assert isinstance(tex,u.VolumeTexture) and not tex.get_editor_property('srgb')
 data=u.AssetRegistryHelpers.get_asset_registry().get_asset_by_object_path(tex.get_path_name())
 assert data.get_tag_value('Dimensions')==f'{size}x{size}x{size}'
for d in json.loads((r/'SourceAssets/CloudNoise/sources.json').read_text()):
 name='noiseShape' if d['volume_resolution'][0]==128 else 'noiseErosion'
 assert hashlib.sha256((r/'SourceAssets/CloudNoise'/(name+'.tga')).read_bytes()).hexdigest()==d['original_sha256']
remaining=assets.list_assets('/Game/TianNanGe/CloudSea/Materials',recursive=False,include_folder=False)
assert {p.split('.')[-1] for p in remaining}=={'M_CloudSea_Layer','MI_CloudSea_Layer'}
(r/'Saved/cloud-current-verified.json').write_text(json.dumps({'passed':True,'active_volumes':1,'scalar_controls':len(controls),'legacy_actors':0,'legacy_materials':0,'shared_noise_verified':True},indent=2))
