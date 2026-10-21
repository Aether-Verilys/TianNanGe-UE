import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
out={'world':world.get_path_name(),'lighting':[],'meshes':[],'weather':[]}
assert '/EasySnowIntegration/Maps/' in out['world']
for a in actors:
    if isinstance(a,(u.DirectionalLight,u.SkyLight,u.PostProcessVolume)):
        r=a.get_actor_rotation();d={'name':a.get_name(),'label':a.get_actor_label(),'rotation':[r.pitch,r.yaw,r.roll]}
        if isinstance(a,u.DirectionalLight):
            c=a.get_component_by_class(u.DirectionalLightComponent);d.update(intensity=c.intensity,color=str(c.light_color),angle=c.get_editor_property('light_source_angle'))
        elif isinstance(a,u.SkyLight):d['intensity']=a.get_component_by_class(u.SkyLightComponent).intensity
        else:d['exposure_bias']=a.get_editor_property('settings').get_editor_property('auto_exposure_bias')
        out['lighting'].append(d)
    if isinstance(a,u.StaticMeshActor) and a.static_mesh_component.get_editor_property('visible'):
        c=a.static_mesh_component
        out['meshes'].append({'label':a.get_actor_label(),'path':a.get_path_name(),'folder':str(a.get_folder_path()),'mesh':c.static_mesh.get_path_name() if c.static_mesh else None,'materials':[m.get_path_name() if m else None for m in c.get_materials()],'collision':str(c.get_collision_enabled()),'distance_field':c.get_editor_property('affect_distance_field_lighting')})
    if str(a.get_folder_path()) in ['EasySnow/Weather','EasySnow/Weather Layers']:
        d={'label':a.get_actor_label(),'settings':{}}
        for key in ['spawnRate -','driftsEnable -','DriftingSnowAmount -','driftOpacity -','snowAmount','windStrength -','spawnRadius','spawnRadiusHeight','Transition Sharpness','windBuildupOverride','breakupIntensity']:
            d['settings'][key]=a.get_editor_property(key)
        out['weather'].append(d)
(root/'Saved/EasySnow/contact-before.json').write_text(json.dumps(out,indent=2))
