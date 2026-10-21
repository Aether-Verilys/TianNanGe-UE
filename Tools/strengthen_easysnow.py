"""Increase Niagara storm density and mesh-surface accumulation without touching the light rig."""
import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];actors=u.get_editor_subsystem(u.EditorActorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/' in world.get_path_name()
all_actors=actors.get_all_level_actors();report={'weather':[],'surface_snow':{}}
def lights():
    values=[]
    for a in all_actors:
        if isinstance(a,(u.DirectionalLight,u.SkyLight,u.PostProcessVolume)):
            r=a.get_actor_rotation();d={'name':a.get_name(),'rotation':[r.pitch,r.yaw,r.roll]}
            if isinstance(a,u.DirectionalLight):
                c=a.get_component_by_class(u.DirectionalLightComponent);d.update(intensity=c.intensity,color=str(c.light_color).split('{')[-1],angle=c.get_editor_property('light_source_angle'))
            elif isinstance(a,u.SkyLight):d['intensity']=a.get_component_by_class(u.SkyLightComponent).intensity
            else:d['exposure_bias']=a.get_editor_property('settings').get_editor_property('auto_exposure_bias')
            values.append(d)
    return values
before=lights()
for a in all_actors:
    if str(a.get_folder_path()) not in ['EasySnow/Weather','EasySnow/Weather Layers']:continue
    ground='Ground' in a.get_actor_label();far='Distant' in a.get_actor_label()
    common={'Preset':None,'windStrength -':5.5,'windUpdraftStrength -':.4,'turbulenceIntensity -':.75,'turbulenceFrequency -':.7,'snowChaos -':1.2,'Collision':True}
    if ground:
        values={**common,'spawnRate -':0.,'DriftingSnowAmount -':22.,'driftOpacity -':.28,'spawnRadius':650.,'spawnRadiusHeight':110.,'snowLifetime -':6.,'driftsEnable -':True,'driftsSizeMin -':300.,'driftsSizeMax -':700.,'windUpdraftStrength -':.07,'driftsCameraFadeDistance':100.,'Geometry Fading Distance':65.,'driftsTextureSpeed':1.8,'driftsEmissive':u.LinearColor(75,95,125,1)}
    elif far:
        values={**common,'spawnRate -':11000.,'spawnRadius':1900.,'spawnRadiusHeight':1250.,'snowLifetime -':8.,'distantParticleSize -':2.3,'distantParticleAlpha':2.6,'NearParticleSizeMin -':.35,'NearParticleSizeMax -':.85}
    else:
        values={**common,'spawnRate -':16000.,'spawnRadius':1150.,'spawnRadiusHeight':1000.,'snowLifetime -':8.,'NearParticleSizeMin -':.35,'NearParticleSizeMax -':.95,'distantParticleSize -':2.,'distantParticleAlpha':2.2,'HighDetailMaxDistance':400.,'MidDetailMaxDistance':1100.,'cameraFadeDistance':80.,'snowAmount':.48,'Transition Sharpness':2.2,'breakupIntensity':.38,'windBuildupOverride':1.,'World Snow Displacement Multiplier':.75}
    a.modify()
    for key,val in values.items():a.set_editor_property(key,val)
    a.call_method('UserConstructionScript')
    for c in a.get_components_by_class(u.NiagaraComponent):c.activate(True)
    report['weather'].append({'label':a.get_actor_label(),'values':{k:str(v) for k,v in values.items()}})
after=lights();assert before==after,'Weather edit changed lighting'
report['lighting_unchanged']=True;report['lighting']=after
mpc=u.load_asset('/Game/EasySnow/System/MP_WF_WorldData')
report['surface_snow']={k:u.MaterialLibrary.get_scalar_parameter_value(world,mpc,k) for k in ['Snow Amount','Snow Displacement Multiplier','windStrength','windBuildupOverride']}
assert abs(report['surface_snow']['Snow Amount']-.48)<.0001
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(root/'Saved/EasySnow/stronger-weather.json').write_text(json.dumps(report,indent=2))
