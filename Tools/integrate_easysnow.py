"""Integrate a user-provided /Game/EasySnow package into a local scene variant."""
import unreal as u,json,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DEST='/Game/TianNanGe/EasySnowIntegration'
BASE='/Game/TianNanGe/Maps/TianNanGe_ReferenceLook';MAP=DEST+'/Maps/TianNanGe_EasySnow'
assets=u.get_editor_subsystem(u.EditorAssetSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem);level=u.get_editor_subsystem(u.LevelEditorSubsystem);mel=u.MaterialEditingLibrary
assert u.load_asset('/Game/EasySnow/Niagara/N_EasySnow_BP'),'Install the local EasySnow package first'
assert u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name().startswith(MAP+'.'),'Open the prepared EasySnow trial map first'
report={'map':MAP,'materials':[],'actors_changed':0,'errors':[]}
func=u.load_asset('/Game/EasySnow/Materials/Functions/MF_WF_WorldSnow');assert func

def link(a,ap,b,bp):assert mel.connect_material_expressions(a,ap,b,bp),(ap,bp)
def output(a,ap,m,p):assert mel.connect_material_property(a,ap,p),(ap,p)
def constant(m,v):
    n=mel.create_material_expression(m,u.MaterialExpressionConstant,-300,500);n.set_editor_property('r',v);return n
def vector(m,v):
    n=mel.create_material_expression(m,u.MaterialExpressionConstant3Vector,-300,650);n.set_editor_property('constant',u.LinearColor(*v,1));return n
def snow_material(source):
    name=source.get_name()+'_EasySnow';path=DEST+'/Materials/'+name
    if assets.does_asset_exist(path):return assets.load_asset(path)
    m=assets.duplicate_asset(source.get_path_name().split('.')[0],path);assert m
    fn=mel.create_material_expression(m,u.MaterialExpressionMaterialFunctionCall,600,0)
    fn.set_material_function(func)
    incoming={}
    mapping=[(u.MaterialProperty.MP_BASE_COLOR,'Base Color'),(u.MaterialProperty.MP_ROUGHNESS,'Roughness'),(u.MaterialProperty.MP_NORMAL,'Normal'),(u.MaterialProperty.MP_AMBIENT_OCCLUSION,'Ambient Occlusion')]
    for p,pin in mapping:
        n=mel.get_material_property_input_node(m,p)
        if n:
            op=mel.get_material_property_input_node_output_name(m,p);link(n,op,fn,pin);incoming[pin]=n.get_name()
    for pin,v in [('Snow Roughness',.9),('Snow Tiling',1.0),('Blend Snow/Source Normals',.12),('Snow Displacement Multiplier',0.0)]:link(constant(m,v),'',fn,pin)
    link(vector(m,(.73,.81,.88)),'',fn,'Snow Base Color');link(vector(m,(.25,.25,1)),'',fn,'Snow Normal Intensity')
    for p,pin in mapping:output(fn,pin,m,p)
    mel.recompile_material(m);assets.save_loaded_asset(m)
    report['materials'].append({'source':source.get_path_name(),'material':m.get_path_name(),'preserved_inputs':incoming})
    return m

chosen={
 '/Game/TianNanGe/Revision_fdf5e67/Lookdev/M_PowderSnow',
 '/Game/TianNanGe/BridgeReference/Materials/M_WeatheredBridgeTimber',
 '/Game/TianNanGe/Revision_fdf5e67/Lookdev/M_ColdTimber_SnowTop',
 '/Game/TianNanGe/Revision_fdf5e67/Materials/M_000',
 *('/Game/TianNanGe/Revision_fdf5e67/Materials/M_'+str(i).zfill(3) for i in range(6,15))
}
material_map={}
for a in actors.get_all_level_actors():
    if not isinstance(a,u.StaticMeshActor) or not a.static_mesh_component.get_editor_property('visible'):continue
    changed=False
    for i,m in enumerate(a.static_mesh_component.get_materials()):
        if not m or m.get_path_name().split('.')[0] not in chosen:continue
        if m.get_path_name() not in material_map:material_map[m.get_path_name()]=snow_material(m)
        a.modify();a.static_mesh_component.set_material(i,material_map[m.get_path_name()]);changed=True
    if changed:report['actors_changed']+=1

for a in list(actors.get_all_level_actors()):
    if str(a.get_folder_path())=='EasySnow/Weather':actors.destroy_actor(a)
cls=u.load_class(None,'/Game/EasySnow/Blueprints/BP_EasySnow.BP_EasySnow_C');assert cls
weather=actors.spawn_actor_from_class(cls,u.Vector(0,40,420));weather.set_actor_label('EasySnow - TianNanGe Light Flurries');weather.set_folder_path('EasySnow/Weather');weather.modify()
settings={
 'Preset':None,'Camera-Centric':False,'spawnRadius':1500.,'spawnRadiusHeight':1100.,
 'spawnRate -':900.,'snowLifetime -':7.,'snowChaos -':.4,'customSpeed -':.8,
 'NearParticleSizeMin -':.25,'NearParticleSizeMax -':.65,'distantParticleSize -':1.6,
 'distantParticleAlpha':1.2,'HighDetailMaxDistance':300.,'MidDetailMaxDistance':1100.,
 'windDirection':125.,'windStrength -':.45,'windUpdraftStrength -':.05,
 'turbulenceIntensity -':.15,'turbulenceFrequency -':.7,
 'driftsEnable -':False,'Collision':True,'castShadow':False,'cameraFadeDistance':100.,
 'baseColor':u.LinearColor(.78,.85,.93,1),'snowEmissive':u.LinearColor(0,0,0,1),
 'Set World Snow Material Settings':True,'snowAmount':.22,'Transition Sharpness':3.,
 'World Snow Displacement Multiplier':0.,'Snow Glimmer Intensity':0.,'windBuildupOverride':1.,
 'breakupIntensity':.45,'breakupTextureTiling':1.5
}
for k,v in settings.items():weather.set_editor_property(k,v)
weather.call_method('UserConstructionScript')
components=weather.get_components_by_class(u.NiagaraComponent);assert components,'EasySnow blueprint did not create a Niagara component'
for c in components:
    c.set_editor_property('auto_activate',True);c.set_component_tick_enabled(True);c.activate(True)
    c.set_can_render_while_seeking(True)
report['weather_settings']={k:str(v) for k,v in settings.items()};report['niagara_components']=[c.get_path_name() for c in components]
assert level.save_current_level()
camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
level.pilot_level_actor(camera);level.editor_set_game_view(True);level.editor_set_viewport_realtime(True);u.AutomationLibrary.set_editor_active_viewport_view_mode(u.ViewModeIndex.VMI_LIT)
(ROOT/'Saved/EasySnow/integration.json').write_text(json.dumps(report,indent=2))
u.log('EASYSNOW_INTEGRATED')
