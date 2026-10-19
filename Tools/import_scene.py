"""Rebuild a baked Unity scene as editable UE assets/actors. Run with UE Python."""
import unreal as u
import json, math, traceback, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get('TIANNANGE_SOURCE','D:/Dev/TianNanGe/Project_TianNanGe'))
DATA = json.loads((ROOT/'Transfer/scene.json').read_text(encoding='utf-8'))
DEST = '/Game/TianNanGe'
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
tools = u.AssetToolsHelpers.get_asset_tools()
version_file=SOURCE/'ProjectSettings/ProjectVersion.txt'
source_version=version_file.read_text().splitlines()[0].split(':',1)[1].strip() if version_file.exists() else '6000.3.10f1'
report = {'engine': u.SystemLibrary.get_engine_version(), 'source_unity': source_version, 'export_unity': DATA['unityVersion'], 'source_commit': '43e985267fca227ab23816204ca6dc6deaa80078', 'meshes': {}, 'materials': {}, 'actors': 0, 'errors': [], 'warnings': DATA['warnings']}
force_rebuild=os.environ.get('TIANNANGE_REBUILD')=='1'

def vec(v): return u.Vector(v['x'],v['y'],v['z'])
def col(v): return u.LinearColor(v['r'],v['g'],v['b'],v.get('a',1))
def prop(obj,name,value): obj.set_editor_property(name,value)
def save_report(): (ROOT/'migration-result.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')

def import_file(path, destination, name, options=None):
    task=u.AssetImportTask()
    for key,value in dict(filename=str(path),destination_path=destination,destination_name=name,automated=True,replace_existing=True,save=True).items(): prop(task,key,value)
    if options: prop(task,'options',options)
    tools.import_asset_tasks([task])
    return [assets.load_asset(p) for p in task.imported_object_paths]

def import_texture(path, normal=False):
    if not path:return None
    filename=SOURCE/path
    if not filename.exists(): report['warnings'].append('Missing texture: '+path); return None
    name='T_'+filename.stem.replace('(','').replace(')','').replace('+','_').replace(' ','_').replace('-','_')
    # Include parent hash: dragon and character can share texture names.
    import hashlib
    name += '_'+hashlib.sha1(path.encode()).hexdigest()[:6]
    target=DEST+'/Textures/'+name
    tex=assets.load_asset(target) if assets.does_asset_exist(target) else next((v for v in import_file(filename,DEST+'/Textures',name) if isinstance(v,u.Texture)),None)
    if tex and normal:
        prop(tex,'compression_settings',u.TextureCompressionSettings.TC_NORMALMAP); prop(tex,'srgb',False); prop(tex,'flip_green_channel',True); assets.save_loaded_asset(tex)
    return tex

def expression(mat,cls,x,y): return u.MaterialEditingLibrary.create_material_expression(mat,cls,x,y)
def output(expr,pin,mat,slot):
    assert u.MaterialEditingLibrary.connect_material_property(expr,pin,slot),(expr,slot)
def connect(a,pin,b,input):
    assert u.MaterialEditingLibrary.connect_material_expressions(a,pin,b,input),(a,b,input)

def material(info):
    target=DEST+'/Materials/'+info['id']
    report['materials'][info['id']]={'source':info['source'],'name':info['name'],'asset':target}
    if assets.does_asset_exist(target):
        mat=assets.load_asset(target)
        if not force_rebuild:return mat
        u.MaterialEditingLibrary.delete_all_material_expressions(mat)
    else:mat=tools.create_asset(info['id'],DEST+'/Materials',u.Material,u.MaterialFactoryNew())
    prop(mat,'two_sided',True)
    c=expression(mat,u.MaterialExpressionConstant3Vector,-500,0); prop(c,'constant',col(info['color']))
    tex=import_texture(info.get('baseTexture'))
    if tex:
        sample=expression(mat,u.MaterialExpressionTextureSample,-800,-100);prop(sample,'texture',tex)
        mul=expression(mat,u.MaterialExpressionMultiply,-250,0); connect(sample,'RGB',mul,'A');connect(c,'',mul,'B'); output(mul,'',mat,u.MaterialProperty.MP_BASE_COLOR)
    else: output(c,'',mat,u.MaterialProperty.MP_BASE_COLOR)
    r=expression(mat,u.MaterialExpressionConstant,-250,200);prop(r,'r',max(.08,1-info.get('smoothness',.25)));output(r,'',mat,u.MaterialProperty.MP_ROUGHNESS)
    m=expression(mat,u.MaterialExpressionConstant,-250,300);prop(m,'r',info.get('metallic',0));output(m,'',mat,u.MaterialProperty.MP_METALLIC)
    normal=import_texture(info.get('normalTexture'),True)
    if normal:
        n=expression(mat,u.MaterialExpressionTextureSample,-500,400);prop(n,'texture',normal);prop(n,'sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL);output(n,'RGB',mat,u.MaterialProperty.MP_NORMAL)
    # Unity HDRP packed mask: R metallic, G occlusion, A smoothness.
    mask=import_texture(info.get('maskTexture'))
    if mask:
        prop(mask,'srgb',False);assets.save_loaded_asset(mask)
        t=expression(mat,u.MaterialExpressionTextureSample,-800,600);prop(t,'texture',mask);prop(t,'sampler_type',u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
        output(t,'R',mat,u.MaterialProperty.MP_METALLIC);output(t,'G',mat,u.MaterialProperty.MP_AMBIENT_OCCLUSION)
        inv=expression(mat,u.MaterialExpressionOneMinus,-400,600);connect(t,'A',inv,'');output(inv,'',mat,u.MaterialProperty.MP_ROUGHNESS)
    u.MaterialEditingLibrary.recompile_material(mat);assets.save_loaded_asset(mat)
    report['materials'][info['id']]={'source':info['source'],'name':info['name'],'asset':target}
    return mat

def import_mesh(mesh_id,force=False):
    target=DEST+'/Meshes/'+mesh_id
    if assets.does_asset_exist(target) and not force and not force_rebuild:
        mesh=assets.load_asset(target)
        report['meshes'][mesh_id]={'asset':target,'materials':len(mesh.static_materials),'bounds':str(mesh.get_bounds())}
        return mesh
    options=u.FbxImportUI()
    for key,value in dict(import_mesh=True,import_as_skeletal=False,import_materials=False,import_textures=False,import_animations=False,automated_import_should_detect_type=False,mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH).items():prop(options,key,value)
    sm=options.static_mesh_import_data
    for key,value in dict(combine_meshes=True,convert_scene=False,convert_scene_unit=False,force_front_x_axis=False,import_uniform_scale=1.0,generate_lightmap_u_vs=False,auto_generate_collision=True,normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS).items():prop(sm,key,value)
    imported=import_file(ROOT/'Transfer/Meshes'/f'{mesh_id}.obj',DEST+'/Meshes',mesh_id,options)
    mesh=next((a for a in imported if isinstance(a,u.StaticMesh)),None)
    if not mesh: raise RuntimeError('No mesh imported for '+mesh_id)
    body=mesh.get_editor_property('body_setup')
    if body:prop(body,'collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    assets.save_loaded_asset(mesh)
    report['meshes'][mesh_id]={'asset':target,'materials':len(mesh.static_materials),'bounds':str(mesh.get_bounds())}
    return mesh

def build_lighting():
    for light_index,light in enumerate(DATA['lights']):
        actor=actors.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,600))
        actor.set_actor_label(light['name']);actor.set_folder_path('Lighting')
        actor.set_actor_rotation(u.MathLibrary.make_rot_from_x(vec(light['forward'])),False)
        component=actor.get_component_by_class(u.DirectionalLightComponent)
        component.set_mobility(u.ComponentMobility.MOVABLE)
        component.set_light_color(col(light['color']))
        component.set_intensity(light['intensity'])
        prop(component,'atmosphere_sun_light',light['name']=='Sun')
    sky=actors.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,500))
    sky.set_actor_label('Kloofendal Environment');sky.set_folder_path('Lighting')
    component=sky.get_component_by_class(u.SkyLightComponent);component.set_mobility(u.ComponentMobility.MOVABLE);component.set_intensity(1);prop(component,'real_time_capture',True)
    # Atmosphere supplies a native Unreal background; HDRI is imported separately below.
    actors.spawn_actor_from_class(u.SkyAtmosphere,u.Vector(0,0,0)).set_folder_path('Lighting')
    fog=actors.spawn_actor_from_class(u.ExponentialHeightFog,u.Vector(0,0,-200));fog.set_folder_path('Lighting')
    fc=fog.get_component_by_class(u.ExponentialHeightFogComponent)
    prop(fc,'fog_density',.012);prop(fc,'fog_height_falloff',.2);prop(fc,'fog_inscattering_luminance',u.LinearColor(.42,.58,.72));prop(fc,'enable_volumetric_fog',True)
    pp=actors.spawn_actor_from_class(u.PostProcessVolume,u.Vector(0,0,0));pp.set_folder_path('Lighting');prop(pp,'unbound',True)
    settings=pp.get_editor_property('settings')
    for key,value in dict(override_auto_exposure_method=True,auto_exposure_method=u.AutoExposureMethod.AEM_MANUAL,override_auto_exposure_bias=True,auto_exposure_bias=-12.0,override_auto_exposure_apply_physical_camera_exposure=True,auto_exposure_apply_physical_camera_exposure=False,override_motion_blur_amount=True,motion_blur_amount=0.0).items():prop(settings,key,value)
    prop(pp,'settings',settings)

def build():
    map_path='/Game/TianNanGe/Maps/TianNanGe_Main'
    if assets.does_asset_exist(map_path) and os.environ.get('TIANNANGE_REBUILD')!='1':
        raise RuntimeError('Map already exists. Back up hand edits, then explicitly set TIANNANGE_REBUILD=1 to rebuild.')
    if assets.does_asset_exist(map_path):
        u.get_editor_subsystem(u.LevelEditorSubsystem).load_level(map_path)
        for actor in actors.get_all_level_actors():
            if not isinstance(actor,(u.WorldSettings,u.Brush)):actors.destroy_actor(actor)
    elif not u.get_editor_subsystem(u.LevelEditorSubsystem).new_level(map_path):
        raise RuntimeError('Could not create map '+map_path)
    mats={}
    for info in DATA['materials']:
        try:mats[info['id']]=material(info)
        except Exception:report['errors'].append('Material '+info['id']+'\n'+traceback.format_exc())
    meshes={}
    for mesh_id in sorted({n['mesh'] for n in DATA['nodes']}):
        try: meshes[mesh_id]=import_mesh(mesh_id)
        except Exception:report['errors'].append('Mesh '+mesh_id+'\n'+traceback.format_exc())
        save_report()
    for node in DATA['nodes']:
        if node['mesh'] not in meshes:continue
        actor=actors.spawn_actor_from_class(u.StaticMeshActor,vec(node['position']))
        actor.set_actor_label(node['name']);actor.set_folder_path('/'.join(node['path'].split('/')[:-1]))
        rotation=node['rotation'];actor.set_actor_rotation(u.Quat(rotation['x'],rotation['y'],rotation['z'],rotation['w']).rotator(),False)
        actor.set_actor_scale3d(vec(node['scale']))
        component=actor.static_mesh_component;component.set_static_mesh(meshes[node['mesh']])
        for i,mat_id in enumerate(node['materials']):
            if mat_id in mats:component.set_material(i,mats[mat_id])
        component.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS if node['collider'] else u.CollisionEnabled.NO_COLLISION)
        report['actors']+=1
    build_lighting()
    camera=DATA['camera']
    actor=actors.spawn_actor_from_class(u.CameraActor,vec(camera['position']))
    actor.set_actor_label('Main Camera (Unity composition)');actor.set_folder_path('Cameras')
    actor.set_actor_rotation(u.MathLibrary.make_rot_from_xz(vec(camera['forward']),vec(camera['up'])),False)
    actor.camera_component.set_field_of_view(math.degrees(2*math.atan(math.tan(math.radians(camera['fov'])/2)*camera['aspect'])))
    prop(actor.camera_component,'aspect_ratio',camera['aspect']);prop(actor.camera_component,'constrain_aspect_ratio',True)
    prop(actor,'auto_activate_for_player',u.AutoReceiveInput.PLAYER0)
    u.EditorLevelLibrary.set_level_viewport_camera_info(actor.get_actor_location(),actor.get_actor_rotation())
    start=actors.spawn_actor_from_class(u.PlayerStart,u.Vector(100,35,180));start.set_actor_label('Preview Start')
    u.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    save_report()
    u.log('TIANNANGE_IMPORT_OK '+str(report['actors'])+' actors; '+str(len(report['errors']))+' errors')

try:build()
except Exception:
    report['errors'].append(traceback.format_exc());save_report();raise
