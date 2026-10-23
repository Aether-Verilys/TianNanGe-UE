"""Fine, dense airborne snow; disable added surface buildup and particle collision."""
import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];actors=u.get_editor_subsystem(u.EditorActorSubsystem)
all_actors=actors.get_all_level_actors();world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/' in world.get_path_name()
integration=json.loads((root/'Saved/EasySnow/integration.json').read_text())
source_map={d['material']:d['source'] for d in integration['materials']}
surface_report=root/'Saved/EasySnow/surface-snow.json'
if surface_report.exists():
    for entry in json.loads(surface_report.read_text())['materials']:
        source_map[entry['material']]=entry['source']
geometry_report=root/'Saved/EasySnow/surface-geometry.json'
if geometry_report.exists():
    for entry in json.loads(geometry_report.read_text())['materials']:
        base=entry['material'].replace('/DisplacedMaterials/','/Materials/').replace('_Geometry','')
        assert base in source_map,base
        source_map[entry['material']]=source_map[base]
report={'profile':'fine_dense_weather_only','collision_enabled':False,'added_surface_accumulation':False,'restored_material_slots':[],'weather':[]}
light_rotations={a.get_name():a.get_actor_rotation() for a in all_actors if isinstance(a,u.DirectionalLight)}
for a in all_actors:
    if not isinstance(a,u.StaticMeshActor):continue
    c=a.static_mesh_component
    for slot,mi in enumerate(c.get_materials()):
        if not mi or not any(p in mi.get_path_name() for p in ['/EasySnowIntegration/Materials/','/EasySnowIntegration/SurfaceSnow/']):continue
        parent=mi.get_editor_property('parent') if isinstance(mi,u.MaterialInstanceConstant) else mi
        original=source_map.get(parent.get_path_name())
        assert original,(mi.get_path_name(),parent.get_path_name())
        source=u.load_asset(original);assert source
        report['restored_material_slots'].append({'actor':a.get_path_name(),'slot':slot,'snow_material':mi.get_path_name(),'restored_source':source.get_path_name()})
        a.modify();c.set_material(slot,source)
for a in all_actors:
    if str(a.get_folder_path()) not in ['EasySnow/Weather','EasySnow/Weather Layers']:continue
    ground='Ground' in a.get_actor_label();far='Distant' in a.get_actor_label()
    common={'Collision':False,'Preset':None,'windStrength -':5.5,'windUpdraftStrength -':.4,'turbulenceIntensity -':.75,'snowChaos -':1.2,'snowAmount':0.,'windBuildupOverride':0.,'World Snow Displacement Multiplier':0.,'Snow Glimmer Intensity':0.}
    if ground:
        values={**common,'spawnRate -':0.,'DriftingSnowAmount -':18.,'driftOpacity -':.20,'windUpdraftStrength -':.07,'driftsEnable -':True}
    elif far:
        values={**common,'spawnRate -':32000.,'distantParticleSize -':.85,'distantParticleAlpha':2.2,'NearParticleSizeMin -':.12,'NearParticleSizeMax -':.32}
    else:
        values={**common,'spawnRate -':60000.,'spawnRadius':1000.,'spawnRadiusHeight':900.,'NearParticleSizeMin -':.12,'NearParticleSizeMax -':.34,'distantParticleSize -':.8,'distantParticleAlpha':2.,'HighDetailMaxDistance':250.,'MidDetailMaxDistance':700.,'cameraFadeDistance':95.}
    a.modify()
    for key,value in values.items():a.set_editor_property(key,value)
    a.call_method('UserConstructionScript')
    for c in a.get_components_by_class(u.NiagaraComponent):c.activate(True)
    report['weather'].append({'label':a.get_actor_label(),'settings':values})
for a in all_actors:
    if a.get_name() in light_rotations:
        before=light_rotations[a.get_name()];after=a.get_actor_rotation()
        assert max(abs(before.pitch-after.pitch),abs(before.yaw-after.yaw),abs(before.roll-after.roll))<1e-8
report['lighting_direction_unchanged']=True
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(root/'Saved/EasySnow/fine-snow.json').write_text(json.dumps(report,indent=2))
