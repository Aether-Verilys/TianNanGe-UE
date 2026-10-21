import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];actors=u.get_editor_subsystem(u.EditorActorSubsystem)
weather=next(a for a in actors.get_all_level_actors() if str(a.get_folder_path())=='EasySnow/Weather')
out={'weather':weather.get_path_name(),'components':[],'all_components':[c.get_class().get_name() for c in weather.get_components_by_class(u.ActorComponent)]}
for c in weather.get_components_by_class(u.NiagaraComponent):
    d={'name':c.get_name(),'active':c.is_active(),'tick_enabled':c.is_component_tick_enabled(),'asset':c.get_fx_system_asset().get_path_name(),'parameters':{}}
    for n in ['User.spawnRate','User.snowLifetime','User.snowChaos','User.windStrength','User.windDirection','User.spawnRadius','User.spawnRadiusHeight','User.Global Snow','User.collision']:
        d['parameters'][n]={'float':c.get_variable_float(n),'vec2':str(c.get_variable_vec2(n)),'bool':c.get_variable_bool(n)}
    out['components'].append(d)
out['material_count']=len(json.loads((root/'Saved/EasySnow/integration.json').read_text())['materials'])
(root/'Saved/EasySnow/runtime.json').write_text(json.dumps(out,indent=2))
