import unreal as u,math,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
u.get_editor_subsystem(u.LevelEditorSubsystem).load_level('/Game/TianNanGe/Maps/TianNanGe_Main')
tools=u.AssetToolsHelpers.get_asset_tools()
task=u.AssetImportTask()
for k,v in dict(filename=str(root/'Transfer/kloofendal_4k.hdr'),destination_path='/Game/TianNanGe/Lighting',destination_name='T_Kloofendal_Cube',automated=True,replace_existing=True,save=True,factory=u.TextureFactory()).items():task.set_editor_property(k,v)
tools.import_asset_tasks([task])
cube=next((u.load_asset(p) for p in task.imported_object_paths if isinstance(u.load_asset(p),u.TextureCube)),None)
assert cube,'HDR panorama did not import as TextureCube'
strength=18000/1.013969
angle=163.7267
for actor in actors.get_all_level_actors():
    if isinstance(actor,u.SkyAtmosphere) or actor.get_actor_label()=='Kloofendal HDRI Background':actors.destroy_actor(actor)
    elif isinstance(actor,u.SkyLight):
        c=actor.get_component_by_class(u.SkyLightComponent)
        c.set_editor_property('real_time_capture',False)
        c.set_editor_property('source_type',u.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
        c.set_editor_property('lower_hemisphere_is_black',False)
        c.set_cubemap(cube);c.set_source_cubemap_angle(angle);c.set_intensity(strength)
    elif isinstance(actor,u.DirectionalLight):actor.get_component_by_class(u.DirectionalLightComponent).set_editor_property('atmosphere_sun_light',False)
path='/Game/TianNanGe/Lighting/M_Kloofendal_Sky'
if assets.does_asset_exist(path):
    mat=assets.load_asset(path);u.MaterialEditingLibrary.delete_all_material_expressions(mat)
else:mat=tools.create_asset('M_Kloofendal_Sky','/Game/TianNanGe/Lighting',u.Material,u.MaterialFactoryNew())
mat.set_editor_property('two_sided',True);mat.set_editor_property('is_sky',True);mat.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
def node(cls,x,y):return u.MaterialEditingLibrary.create_material_expression(mat,cls,x,y)
def link(a,pin,b,name):assert u.MaterialEditingLibrary.connect_material_expressions(a,pin,b,name),(a,b,name)
world=node(u.MaterialExpressionWorldPosition,-1000,0)
camera=node(u.MaterialExpressionCameraPositionWS,-1000,200)
delta=node(u.MaterialExpressionSubtract,-800,0);link(world,'',delta,'A');link(camera,'',delta,'B')
rotate=node(u.MaterialExpressionCustom,-600,0)
rotate.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
input=u.CustomInput();input.set_editor_property('input_name','D');rotate.set_editor_property('inputs',[input])
a=math.radians(-angle)
rotate.set_editor_property('code',f'float3 v=normalize(D);float a={a:.10f};return float3(cos(a)*v.x-sin(a)*v.y,sin(a)*v.x+cos(a)*v.y,v.z);')
link(delta,'',rotate,'D')
sample=node(u.MaterialExpressionTextureSampleParameterCube,-400,0);sample.set_editor_property('parameter_name','Environment');sample.set_editor_property('texture',cube);sample.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR);link(rotate,'',sample,'UVs')
scale=node(u.MaterialExpressionConstant,-400,250);scale.set_editor_property('r',strength)
multiply=node(u.MaterialExpressionMultiply,-150,0);link(sample,'RGB',multiply,'A');link(scale,'',multiply,'B')
u.MaterialEditingLibrary.connect_material_property(multiply,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
u.MaterialEditingLibrary.recompile_material(mat);assets.save_loaded_asset(mat)
sky=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0))
sky.set_actor_label('Kloofendal HDRI Background');sky.set_folder_path('Lighting')
sky.set_actor_scale3d(u.Vector(2000,2000,2000))
c=sky.static_mesh_component;c.set_static_mesh(u.load_asset('/Engine/BasicShapes/Sphere'));c.set_material(0,mat);c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
c.set_editor_property('cast_shadow',False);c.set_editor_property('affect_distance_field_lighting',False);c.set_editor_property('affect_dynamic_indirect_lighting',False)
u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
(root/'hdri-result.json').write_text(json.dumps({'asset':cube.get_path_name(),'rotation_degrees':angle,'radiance_multiplier_approximate':strength,'source':'Poly Haven Kloofendal 38d Partly Cloudy Pure Sky, CC0','conversion':'EXR -> Radiance HDR with Blender image.save; linear data, no view transform'},indent=2))
u.log('TIANNANGE_HDRI_OK')
