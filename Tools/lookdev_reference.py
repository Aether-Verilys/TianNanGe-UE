"""Build editable native UE lighting; no reference-image projection or compositing."""
import unreal as u
import json,math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEST='/Game/TianNanGe/Revision_fdf5e67'
DATA=json.loads((ROOT/'Transfer_fdf5e67/scene.json').read_text())
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
tools=u.AssetToolsHelpers.get_asset_tools()
warnings=[]

def prop(obj,key,value):obj.set_editor_property(key,value)
def optional(obj,key,value):
    try:prop(obj,key,value)
    except Exception as error:warnings.append(key+': '+str(error))
def exp(mat,cls,x,y):return u.MaterialEditingLibrary.create_material_expression(mat,cls,x,y)
def link(a,p,b,i):assert u.MaterialEditingLibrary.connect_material_expressions(a,p,b,i),(a,b,i)
def output(n,p,mat,slot):assert u.MaterialEditingLibrary.connect_material_property(n,p,slot)
def constant(mat,value,x=0,y=0):
    n=exp(mat,u.MaterialExpressionConstant,x,y);prop(n,'r',value);return n
def color(mat,value,x=0,y=0):
    n=exp(mat,u.MaterialExpressionConstant3Vector,x,y);prop(n,'constant',u.LinearColor(*value));return n
def make_material(name,unlit=False):
    path=DEST+'/Lookdev/'+name
    mat=assets.load_asset(path) if assets.does_asset_exist(path) else tools.create_asset(name,DEST+'/Lookdev',u.Material,u.MaterialFactoryNew())
    u.MaterialEditingLibrary.delete_all_material_expressions(mat)
    prop(mat,'two_sided',True)
    prop(mat,'shading_model',u.MaterialShadingModel.MSM_UNLIT if unlit else u.MaterialShadingModel.MSM_DEFAULT_LIT)
    return mat
def custom(mat,code,inputs,kind=u.CustomMaterialOutputType.CMOT_FLOAT3):
    n=exp(mat,u.MaterialExpressionCustom,-200,0);prop(n,'code',code);prop(n,'output_type',kind)
    values=[]
    for name,node in inputs.items():
        value=u.CustomInput();prop(value,'input_name',name);values.append(value)
    prop(n,'inputs',values)
    for name,node in inputs.items():link(node,'',n,name)
    return n

# Replace only lighting in the revision map. The original migration remains intact.
for actor in actors.get_all_level_actors():
    if isinstance(actor,(u.DirectionalLight,u.SkyLight,u.SkyAtmosphere,u.ExponentialHeightFog,u.PostProcessVolume)) or actor.get_actor_label().startswith('Lookdev '):
        actors.destroy_actor(actor)

def sun(label,direction,temperature_color,lux):
    actor=actors.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,700))
    actor.set_actor_label(label);actor.set_folder_path('Lookdev/Lighting')
    actor.set_actor_rotation(u.MathLibrary.make_rot_from_x(u.Vector(*direction)),False)
    comp=actor.get_component_by_class(u.DirectionalLightComponent)
    comp.set_mobility(u.ComponentMobility.MOVABLE);comp.set_light_color(u.LinearColor(*temperature_color));comp.set_intensity(lux)
    prop(comp,'atmosphere_sun_light',False);prop(comp,'light_source_angle',2.2)
    optional(comp,'contact_shadow_length',0.06)
    optional(comp,'volumetric_scattering_intensity',0.6)
    return actor
sun('Lookdev Warm backlight',(-.72,-.3,-.5),(1.0,.82,.60),42000)
sun('Lookdev Cool soft fill',(.45,.3,-.75),(.43,.65,1.0),3800)

sky=actors.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,500));sky.set_actor_label('Lookdev Cold environment');sky.set_folder_path('Lookdev/Lighting')
sc=sky.get_component_by_class(u.SkyLightComponent);sc.set_mobility(u.ComponentMobility.MOVABLE)
prop(sc,'source_type',u.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
prop(sc,'real_time_capture',False);prop(sc,'lower_hemisphere_is_black',False)
sc.set_cubemap(u.load_asset('/Game/TianNanGe/Lighting/T_Kloofendal_Cube'));sc.set_source_cubemap_angle(163.7267);sc.set_intensity(2800)
sc.set_light_color(u.LinearColor(.72,.86,1.0))

mat=make_material('M_WinterSky',True);prop(mat,'is_sky',True)
wp=exp(mat,u.MaterialExpressionWorldPosition,-800,0);cp=exp(mat,u.MaterialExpressionCameraPositionWS,-800,200)
delta=exp(mat,u.MaterialExpressionSubtract,-600,0);link(wp,'',delta,'A');link(cp,'',delta,'B')
skycode='''float3 d=normalize(D); float h=saturate(d.z*1.8); float3 c=lerp(float3(3900,4900,5600),float3(1600,2550,3400),h); float sun=saturate(dot(d,normalize(float3(.72,.3,.5)))); c+=float3(4200,3200,1800)*pow(sun,28); c+=float3(42000,31000,16000)*pow(sun,1400); return c;'''
n=custom(mat,skycode,{'D':delta});output(n,'',mat,u.MaterialProperty.MP_EMISSIVE_COLOR)
u.MaterialEditingLibrary.recompile_material(mat);assets.save_loaded_asset(mat)
actor=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0));actor.set_actor_label('Lookdev Winter sky');actor.set_folder_path('Lookdev/Atmosphere');actor.set_actor_scale3d(u.Vector(2000,2000,2000))
c=actor.static_mesh_component;c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Sphere'));c.set_material(0,mat);c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
for key in ['cast_shadow','affect_distance_field_lighting','affect_dynamic_indirect_lighting']:prop(c,key,False)

fog=actors.spawn_actor_from_class(u.ExponentialHeightFog,u.Vector(0,0,-250));fog.set_actor_label('Lookdev Blue depth haze');fog.set_folder_path('Lookdev/Atmosphere')
fc=fog.get_component_by_class(u.ExponentialHeightFogComponent)
for key,value in dict(fog_density=.028,fog_height_falloff=.09,start_distance=650.0,fog_max_opacity=.88,fog_inscattering_luminance=u.LinearColor(.33,.51,.68),enable_volumetric_fog=True,volumetric_fog_albedo=u.Color(190,215,240),volumetric_fog_scattering_distribution=.45,volumetric_fog_distance=18000.0).items():prop(fc,key,value)

pp=actors.spawn_actor_from_class(u.PostProcessVolume,u.Vector(0,0,0));pp.set_actor_label('Lookdev Reference grade EV12');pp.set_folder_path('Lookdev/PostProcess');prop(pp,'unbound',True);prop(pp,'priority',10.0)
s=pp.get_editor_property('settings')
def setting(key,value):
    prop(s,'override_'+key,True);prop(s,key,value)
for key,value in dict(auto_exposure_method=u.AutoExposureMethod.AEM_MANUAL,auto_exposure_bias=-12.0,auto_exposure_apply_physical_camera_exposure=False,motion_blur_amount=0.0,bloom_intensity=.22,vignette_intensity=.12,scene_fringe_intensity=0.0,color_saturation=u.Vector4(.84,.84,.84,1),color_contrast=u.Vector4(1.06,1.06,1.06,1),color_gain_shadows=u.Vector4(.82,.97,1.13,1),color_gain_highlights=u.Vector4(1.07,1.02,.94,1),color_saturation_shadows=u.Vector4(.88,.88,.88,1),ambient_occlusion_intensity=.75,ambient_occlusion_radius=60.0,dynamic_global_illumination_method=u.DynamicGlobalIlluminationMethod.LUMEN,reflection_method=u.ReflectionMethod.LUMEN,lumen_scene_lighting_quality=2.0,lumen_final_gather_quality=2.0).items():setting(key,value)
prop(pp,'settings',s)

# Snow has fine world-space variation and realistic reflectance, retaining mesh snow caps.
snow=make_material('M_PowderSnow')
wp=exp(snow,u.MaterialExpressionWorldPosition,-800,0)
n=custom(snow,'float f=.5+.5*sin(P.x*.82+sin(P.y*.61))*sin(P.y*.94+sin(P.z*.4));return lerp(float3(.62,.70,.77),float3(.85,.90,.94),f*.45+.3);',{'P':wp})
output(n,'',snow,u.MaterialProperty.MP_BASE_COLOR);output(constant(snow,.84),'',snow,u.MaterialProperty.MP_ROUGHNESS);output(constant(snow,.24),'',snow,u.MaterialProperty.MP_SPECULAR)
u.MaterialEditingLibrary.recompile_material(snow);assets.save_loaded_asset(snow)
timber=make_material('M_ColdTimber_SnowTop')
wp=exp(timber,u.MaterialExpressionWorldPosition,-800,0)
normal=exp(timber,u.MaterialExpressionVertexNormalWS,-800,200)
n=custom(timber,'float f=.5+.5*sin(P.x*.12+sin(P.y*.2))*sin(P.z*.32);float cap=smoothstep(.28,.72,N.z+(f-.5)*.22);return lerp(float3(.035,.058,.075)*(f*.25+.8),float3(.76,.83,.89),cap);',{'P':wp,'N':normal})
output(n,'',timber,u.MaterialProperty.MP_BASE_COLOR);output(constant(timber,.8),'',timber,u.MaterialProperty.MP_ROUGHNESS)
u.MaterialEditingLibrary.recompile_material(timber);assets.save_loaded_asset(timber)

# Preserve the delivered dragon normal map but grade the body toward dark slate/olive.
dragon=assets.load_asset(DEST+'/Materials/M_004')
wp=exp(dragon,u.MaterialExpressionWorldPosition,-800,-600)
n=custom(dragon,'float f=.5+.5*sin(P.x*.035+sin(P.y*.05))*sin(P.z*.045);return lerp(float3(.045,.068,.085),float3(.14,.155,.105),f*.65);',{'P':wp})
output(n,'',dragon,u.MaterialProperty.MP_BASE_COLOR);output(constant(dragon,.48),'',dragon,u.MaterialProperty.MP_ROUGHNESS);output(constant(dragon,.22),'',dragon,u.MaterialProperty.MP_METALLIC)
u.MaterialEditingLibrary.recompile_material(dragon);assets.save_loaded_asset(dragon)
eye=assets.load_asset(DEST+'/Materials/M_005')
# Eye texture also contains non-eye UV regions: retain its red-channel mask.
old=u.MaterialEditingLibrary.get_material_property_input_node(eye,u.MaterialProperty.MP_BASE_COLOR)
if old:
    mask=exp(eye,u.MaterialExpressionCustom,-200,-500);prop(mask,'code','float m=saturate((C.r-max(C.g,C.b))*4);return float3(4200,1600,80)*m;')
    prop(mask,'output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
    ci=u.CustomInput();prop(ci,'input_name','C');prop(mask,'inputs',[ci]);link(old,'',mask,'C');output(mask,'',eye,u.MaterialProperty.MP_EMISSIVE_COLOR)
u.MaterialEditingLibrary.recompile_material(eye);assets.save_loaded_asset(eye)
snow_ids={m['id'] for m in DATA['materials'] if m['name'].lower() in ('snow','surfacesnow')}
nodes={n['path']:n for n in DATA['nodes']}
snow_slots=0
for actor in actors.get_all_level_actors():
    if not isinstance(actor,u.StaticMeshActor):continue
    path=str(actor.get_folder_path())+'/'+actor.get_actor_label()
    node=nodes.get(path)
    if not node:continue
    for index,mat_id in enumerate(node['materials']):
        if mat_id in snow_ids:actor.static_mesh_component.set_material(index,snow);snow_slots+=1
        elif mat_id=='M_002':actor.static_mesh_component.set_material(index,timber)

camera=next(a for a in actors.get_all_level_actors() if isinstance(a,u.CameraActor) and a.get_actor_label().startswith('Main Camera'))
camera.set_actor_label('Main Camera (reference look)')
u.EditorLevelLibrary.set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation())
u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(ROOT/'lookdev-result.json').write_text(json.dumps({'map':'/Game/TianNanGe/Maps/TianNanGe_ReferenceLook','reference':'D:/Dev/TianNanGe/4TianNan1_4k_fb78c.jpg','key_lux':42000,'fill_lux':3800,'sky_strength':2800,'fixed_ev':12,'snow_material_slots':snow_slots,'warnings':warnings},indent=2))
u.log('TIANNANGE_LOOKDEV_OK')
