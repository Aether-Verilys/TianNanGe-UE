import unreal as u,json,traceback,re
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'Saved/EasySnow';out.mkdir(parents=True,exist_ok=True)
registry=u.AssetRegistryHelpers.get_asset_registry();registry.scan_paths_synchronous(['/Game/EasySnow'],True)
report={'engine':u.SystemLibrary.get_engine_version(),'assets':len(registry.get_assets_by_path('/Game/EasySnow',True)),'errors':[],'blueprints':{},'presets':{}}
def value(v):
    if isinstance(v,(float,int,str,bool)) or v is None:return v
    if isinstance(v,u.Object):return v.get_path_name()
    return str(v)
names=['Preset','speed','spawnRadius','spawnRadiusHeight','spawnRate','snowLifetime','HighDetailSnowflakesMaxDistance','MidDetailSnowflakesMaxDistance','snowChaos','collision','windDirection','windStrength','windUpdraftStrength','turbulenceIntensity','turbulenceFrequency','driftingSnow','driftingSnowAmount','driftsSpawnRate','globalSnow','Global Snow','snowAmount','Snow Amount','snowEmissive','snowFadeControl','Snow Fade Control','Snow Glimmering Intensity','Snow Displacement Multiplier','Set World Snow Material Settings','windBuildupOverride','breakupIntensity','SnowBP']
for name in ['BP_EasySnow','BP_EasySnowMask']:
    try:
        cls=u.load_class(None,'/Game/EasySnow/Blueprints/'+name+'.'+name+'_C');assert cls
        obj=u.get_default_object(cls);d={'class':cls.get_path_name(),'fields':{},'dir':[x for x in dir(obj) if not x.startswith('_')]}
        for n in names:
            try:d['fields'][n]=value(obj.get_editor_property(n))
            except Exception:pass
        report['blueprints'][name]=d
    except Exception:report['errors'].append(traceback.format_exc())
for name in ['Light','Flurries','Heavy','Blizzard','Foggy']:
    try:
        a=u.load_asset('/Game/EasySnow/System/Presets/EasySnowPreset_'+name);assert a
        d={'fields':{}}
        for n in names:
            try:d['fields'][n]=value(a.get_editor_property(n))
            except Exception:pass
        report['presets'][name]=d
    except Exception:report['errors'].append(traceback.format_exc())
function=u.load_asset('/Game/EasySnow/Materials/Functions/MF_WF_WorldSnow')
report['function_loaded']=bool(function)
report['material_api']=[x for x in dir(u.MaterialEditingLibrary) if any(k in x for k in ('function','input','output','expression'))]
if function:
    for k in ['get_material_function_input_names','get_material_function_output_names']:
        if hasattr(u.MaterialEditingLibrary,k):
            try:report[k]=[str(x) for x in getattr(u.MaterialEditingLibrary,k)(function)]
            except Exception:report[k]=traceback.format_exc()
    report['function_properties']=[x for x in dir(function) if not x.startswith('_')]
(out/'probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('EASYSNOW_PROBE_FINISHED')
