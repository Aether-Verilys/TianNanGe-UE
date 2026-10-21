"""Snapshot the live scene before adding non-displacing surface snow."""
import unreal as u
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/' in world.get_path_name()

def serial(v):
    if v is None or isinstance(v, (str, int, float, bool)): return v
    if isinstance(v, u.Object): return v.get_path_name()
    if isinstance(v, (list,tuple)): return [serial(x) for x in v]
    if hasattr(v, 'to_tuple'): return [serial(x) for x in v.to_tuple()]
    return str(v).split(' {')[-1]

out = {'world': world.get_path_name(), 'environment': {}, 'meshes': {}, 'weather': {}}
for a in actors:
    if isinstance(a, (u.DirectionalLight, u.SkyLight, u.PostProcessVolume, u.ExponentialHeightFog, u.CameraActor)) or a.get_actor_label().startswith('Lookdev Chaotic'):
        d = {'transform': [serial(a.get_actor_location()), serial(a.get_actor_rotation()), serial(a.get_actor_scale3d())]}
        if isinstance(a, (u.DirectionalLight, u.SkyLight)):
            c = a.get_component_by_class(u.DirectionalLightComponent if isinstance(a, u.DirectionalLight) else u.SkyLightComponent)
            d.update({k: serial(c.get_editor_property(k)) for k in ['intensity', 'light_color']})
            if isinstance(a,u.SkyLight): d.update({k:serial(c.get_editor_property(k)) for k in ['real_time_capture','cubemap']})
        if isinstance(a, u.PostProcessVolume):
            s = a.get_editor_property('settings')
            d.update({k: serial(s.get_editor_property(k)) for k in ['auto_exposure_method', 'auto_exposure_bias', 'auto_exposure_apply_physical_camera_exposure']})
        if isinstance(a, u.ExponentialHeightFog):
            c = a.get_component_by_class(u.ExponentialHeightFogComponent)
            d.update({k:serial(c.get_editor_property(k)) for k in ['fog_density','enable_volumetric_fog','volumetric_fog_distance','fog_cutoff_distance']})
        out['environment'][a.get_path_name()] = d
    if isinstance(a, u.StaticMeshActor):
        c = a.static_mesh_component
        out['meshes'][a.get_path_name()] = {'label': a.get_actor_label(), 'materials': [serial(m) for m in c.get_materials()], 'mesh': serial(c.static_mesh)}
    if str(a.get_folder_path()) in ['EasySnow/Weather','EasySnow/Weather Layers']:
        fields = ['Collision','spawnRate -','NearParticleSizeMin -','NearParticleSizeMax -','distantParticleSize -','windDirection','windStrength -','DriftingSnowAmount -','driftOpacity -','snowAmount','windBuildupOverride','World Snow Displacement Multiplier','Snow Glimmer Intensity','Set World Snow Material Settings']
        out['weather'][a.get_path_name()] = {k: serial(a.get_editor_property(k)) for k in fields}
mi = u.load_asset('/Game/TianNanGe/EasySnowIntegration/Skies/MI_Chaotic_WinterSky_04')
out['sky'] = {str(k):u.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(mi,k) for k in u.MaterialEditingLibrary.get_scalar_parameter_names(mi)}
target = root/'Saved/EasySnow/surface-before.json'
if globals().get('COMMAND',{}).get('verify'): target = root/'Saved/EasySnow/surface-after.json'
target.write_text(json.dumps(out,indent=2))
