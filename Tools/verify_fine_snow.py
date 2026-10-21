import unreal as u,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/' in world.get_path_name()
out={'weather':[],'surface_snow_materials_in_use':[],'lighting_preserved':True}
baseline=json.loads((root/'Saved/EasySnow/contact-before.json').read_text())['lighting']
for d in baseline:
    a=next(a for a in actors if a.get_name()==d['name']);r=a.get_actor_rotation()
    assert max(abs(x-y) for x,y in zip([r.pitch,r.yaw,r.roll],d['rotation']))<1e-8
    if isinstance(a,u.DirectionalLight):
        c=a.get_component_by_class(u.DirectionalLightComponent)
        assert c.intensity==d['intensity'] and str(c.light_color).split('{')[-1]==d['color'].split('{')[-1]
        assert c.get_editor_property('light_source_angle')==d['angle']
    elif isinstance(a,u.SkyLight):assert a.get_component_by_class(u.SkyLightComponent).intensity==d['intensity']
    else:assert a.get_editor_property('settings').get_editor_property('auto_exposure_bias')==d['exposure_bias']
for a in actors:
    if isinstance(a,u.StaticMeshActor):
        for m in a.static_mesh_component.get_materials():
            if m and any(p in m.get_path_name() for p in ['/EasySnowIntegration/Materials/','/EasySnowIntegration/SurfaceSnow/Materials/']):out['surface_snow_materials_in_use'].append(m.get_path_name())
    if str(a.get_folder_path()) not in ['EasySnow/Weather','EasySnow/Weather Layers']:continue
    assert a.get_editor_property('Collision') is False
    d={'label':a.get_actor_label(),'collision':False,'components':[]}
    for c in a.get_components_by_class(u.NiagaraComponent):
        assert c.is_active() and c.get_editor_property('auto_activate')
        assert c.get_variable_bool('User.collision') in [None,False]
        values={key:c.get_variable_float('User.'+key) for key in ['spawnRate','NearParticleSizeMin','NearParticleSizeMax','windStrength','driftsSpawnRate']}
        d['components'].append(values)
    out['weather'].append(d)
assert len(out['weather'])==3 and not out['surface_snow_materials_in_use']
mpc=u.load_asset('/Game/EasySnow/System/MP_WF_WorldData')
out['surface_settings']={key:u.MaterialLibrary.get_scalar_parameter_value(world,mpc,key) for key in ['Snow Amount','Snow Displacement Multiplier','Snow Glimmering Intensity','windBuildupOverride']}
assert all(abs(x)<.0001 for x in out['surface_settings'].values())
out['original_maps_unchanged']={}
for name,expected in [('TianNanGe_ReferenceLook','0f381b7b99e26b2143c3f583f87c7cc6d1dcb03eb7e61cb6296dffdbc718b9a4'),('TianNanGe_Main','6d662e9b85e484a5af007a93c357fe8867d5c644eb3b6e3765bb198f8fb1885e')]:
    actual=hashlib.sha256((root/('Content/TianNanGe/Maps/'+name+'.umap')).read_bytes()).hexdigest()
    assert actual==expected;out['original_maps_unchanged'][name]=True
out['passed']=True
(root/'Saved/EasySnow/fine-verified.json').write_text(json.dumps(out,indent=2))
