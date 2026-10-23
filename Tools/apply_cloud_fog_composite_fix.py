"""Disable the depth-dependent volumetric-fog imprint on native cloud shading.

Scene fog, cloud extinction, lighting, shadowing and all actor settings remain
unchanged. No shader compilation, scene captures, input or camera moves.
"""
import datetime,json,shutil,time
from pathlib import Path
import unreal as u

root=Path(__file__).resolve().parents[1]
api=u.get_editor_subsystem(u.EditorActorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/' in world.get_path_name()
actors=api.get_all_level_actors()
assert not any(isinstance(a,u.SceneCapture2D) for a in actors)
mel=u.MaterialEditingLibrary
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
key=level.get_active_viewport_config_key()
clouds=[a.get_component_by_class(u.HeterogeneousVolumeComponent) for a in actors
        if isinstance(a,u.HeterogeneousVolume) and a.get_component_by_class(u.HeterogeneousVolumeComponent).is_visible()]
assert len(clouds)==1
parameter_names=[str(n) for n in mel.get_scalar_parameter_names(clouds[0].get_material(0))]

def snapshot():
    result={'actors':{},'view':[],'clouds':{},'controllers':{},'lights':{},'fog':{},'snow':{},'cameras':{}}
    p,r=level.get_level_viewport_camera_info(key)
    result['view']=[p.export_text(),r.export_text()]
    for a in api.get_all_level_actors():
        path=a.get_path_name()
        result['actors'][path]=a.get_actor_transform().export_text()
        if isinstance(a,u.HeterogeneousVolume):
            c=a.get_component_by_class(u.HeterogeneousVolumeComponent);m=c.get_material(0)
            result['clouds'][path]={'material':m.get_path_name(),'visible':c.is_visible(),
                'scalars':{str(n):m.get_scalar_parameter_value(n) for n in mel.get_scalar_parameter_names(m)},
                'vectors':{str(n):m.get_vector_parameter_value(n).export_text() for n in mel.get_vector_parameter_names(m)}}
        if a.get_class().get_name().startswith('BP_CloudSeaController'):
            result['controllers'][path]={n:str(a.get_editor_property(n)) for n in parameter_names}
        if isinstance(a,(u.DirectionalLight,u.SkyLight)):
            c=a.get_component_by_class(u.DirectionalLightComponent if isinstance(a,u.DirectionalLight) else u.SkyLightComponent)
            result['lights'][path]={k:str(c.get_editor_property(k)) for k in ['intensity','light_color','cast_shadows','cast_volumetric_shadow','volumetric_scattering_intensity']}
        if isinstance(a,u.ExponentialHeightFog):
            c=a.get_component_by_class(u.ExponentialHeightFogComponent)
            result['fog'][path]={k:str(c.get_editor_property(k)) for k in ['fog_density','fog_height_falloff','fog_max_opacity','start_distance','fog_cutoff_distance','volumetric_fog_extinction_scale']}
        for c in a.get_components_by_class(u.NiagaraComponent):
            result['snow'][c.get_path_name()]={'active':c.is_active(),'visible':c.is_visible()}
        for c in a.get_components_by_class(u.CameraComponent):
            result['cameras'][c.get_path_name()]={'fov':c.field_of_view,'settings':c.get_editor_property('post_process_settings').export_text()}
    return result

before=snapshot()
name='r.HeterogeneousVolumes.VolumetricFog'
old=u.SystemLibrary.get_console_variable_int_value(name)
config=root/'Config/DefaultEngine.ini'
text=config.read_text(encoding='utf-8')
lines=text.splitlines()
value=name+'=0'
if any(line.strip().startswith(name+'=') for line in lines):
    lines=[value if line.strip().startswith(name+'=') else line for line in lines]
else:
    index=lines.index('[SystemSettings]')+1
    lines[index:index]=[
        '; Avoid scene-depth silhouettes from volumetric fog linearized across the cloud ray.',
        '; Keep scene volumetric fog, height fog, cloud lighting and shadows enabled.',value]
updated='\n'.join(lines)+'\n'
backup=root/'Backups'/('CloudFogComposite_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
backup.mkdir(parents=True,exist_ok=False)
shutil.copy2(config,backup/config.name)
try:
    u.SystemLibrary.execute_console_command(world,name+' 0')
    assert u.SystemLibrary.get_console_variable_int_value(name)==0
    config.write_text(updated,encoding='utf-8')
    after=snapshot()
    assert before==after,'Unexpected scene mutation during fog composition update.'
except Exception:
    u.SystemLibrary.execute_console_command(world,name+' '+str(old))
    shutil.copy2(backup/config.name,config)
    raise
report={'time':time.time(),'setting':name,'previous':old,'current':0,'backup':str(backup),
        'scene_preserved':True,'snapshot':after,
        'scene_volumetric_fog':u.SystemLibrary.get_console_variable_int_value('r.VolumetricFog'),
        'cloud_height_fog':u.SystemLibrary.get_console_variable_int_value('r.HeterogeneousVolumes.HeightFog')}
(root/'Saved/cloud-fog-composite-applied.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('Cloud fog composition fix applied; scene settings preserved.')
