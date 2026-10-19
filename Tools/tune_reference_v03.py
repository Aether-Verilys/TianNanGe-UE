import unreal as u,json,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
for a in actors.get_all_level_actors():
    if a.get_actor_label().startswith('Lookdev Snow detail'):actors.destroy_actor(a)
    elif isinstance(a,u.DirectionalLight):a.get_component_by_class(u.DirectionalLightComponent).set_editor_property('volumetric_scattering_intensity',0.0)
    elif isinstance(a,u.ExponentialHeightFog):
        c=a.get_component_by_class(u.ExponentialHeightFogComponent)
        for key,value in dict(enable_volumetric_fog=False,fog_density=.075,start_distance=450.0,fog_inscattering_luminance=u.LinearColor(.22,.39,.60),directional_inscattering_luminance=u.LinearColor(.35,.48,.65)).items():c.set_editor_property(key,value)
    elif isinstance(a,u.PostProcessVolume):
        s=a.get_editor_property('settings');s.set_editor_property('auto_exposure_bias',-12.5);a.set_editor_property('settings',s)
data=json.loads((ROOT/'Transfer_fdf5e67/scene.json').read_text())
snow=u.load_asset('/Game/TianNanGe/Revision_fdf5e67/Lookdev/M_PowderSnow')
cylinder=u.load_asset('/Engine/BasicShapes/Cylinder');cone=u.load_asset('/Engine/BasicShapes/Cone')
count=0;rng=random.Random(233)
def mesh(name,position,scale,rotation,asset):
    global count
    a=actors.spawn_actor_from_class(u.StaticMeshActor,position,rotation)
    a.set_actor_label('Lookdev Snow detail '+name);a.set_folder_path('Lookdev/Bridge snow')
    a.set_actor_scale3d(scale);c=a.static_mesh_component;c.set_static_mesh(asset);c.set_material(0,snow);c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION);count+=1
for n in data['nodes']:
    p=n['position']
    if '/ExtendedRailings/' not in n['path'] or not n['name'].startswith('Rail_') or not -600<p['x']<1500:continue
    length=n['scale']['x']*100
    mesh('cap '+str(count),u.Vector(p['x'],p['y'],p['z']+9),u.Vector(.105,.09,length/100+.05),u.MathLibrary.make_rot_from_z(u.Vector(1,0,0)),cylinder)
    if p['z']>100:
        for fraction in (.22,.55,.83):
            height=rng.uniform(9,26)
            mesh('icicle '+str(count),u.Vector(p['x']+(fraction-.5)*length,p['y']+rng.uniform(-3,3),p['z']+5-height/2),u.Vector(.022,.022,height/100),u.Rotator(roll=180,pitch=0,yaw=0),cone)
u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(ROOT/'Tools/Live/tuning-v03.json').write_text(json.dumps({'fixed_ev':12.5,'fog_density':.075,'volumetric_fog':False,'bridge_snow_detail_actors':count}))
