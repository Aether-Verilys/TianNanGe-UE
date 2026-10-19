import unreal as u,json,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DEST='/Game/TianNanGe/BridgeReference'
data=json.loads((ROOT/'Transfer_BridgeReference/manifest.json').read_text())
assets=u.get_editor_subsystem(u.EditorAssetSubsystem);actors=u.get_editor_subsystem(u.EditorActorSubsystem)
asset_tools=u.AssetToolsHelpers.get_asset_tools();mel=u.MaterialEditingLibrary

def e(m,cls,x=-400,y=0):return mel.create_material_expression(m,cls,x,y)
def output(n,p,m,slot):assert mel.connect_material_property(n,p,slot)
def link(a,ap,b,bp):assert mel.connect_material_expressions(a,ap,b,bp)
def constant(m,value,slot,y):
    n=e(m,u.MaterialExpressionConstant,y=y);n.set_editor_property('r',value);output(n,'',m,slot)
def material(name,color,rough,spec,grain=False):
    path=DEST+'/Materials/'+name
    if assets.does_asset_exist(path):return assets.load_asset(path)
    m=asset_tools.create_asset(name,DEST+'/Materials',u.Material,u.MaterialFactoryNew())
    m.set_editor_property('two_sided',True)
    c=e(m,u.MaterialExpressionConstant3Vector);c.set_editor_property('constant',u.LinearColor(*color,1))
    if grain:
        pos=e(m,u.MaterialExpressionWorldPosition,-800,100)
        custom=e(m,u.MaterialExpressionCustom,-500,100);custom.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT3)
        inp=u.CustomInput();inp.set_editor_property('input_name','P');custom.set_editor_property('inputs',[inp])
        custom.set_editor_property('code','float g=.5+.5*sin(P.x*.075+2*sin(P.z*.085)+sin(P.y*.37));float fine=.5+.5*sin(P.x*.41+sin(P.z*.23));return float3(.045,.067,.083)*(.72+.23*g+.05*fine);')
        link(pos,'',custom,'P');output(custom,'',m,u.MaterialProperty.MP_BASE_COLOR)
    else:output(c,'',m,u.MaterialProperty.MP_BASE_COLOR)
    constant(m,rough,u.MaterialProperty.MP_ROUGHNESS,220);constant(m,spec,u.MaterialProperty.MP_SPECULAR,320)
    mel.recompile_material(m);assets.save_loaded_asset(m);return m

mats={'timber':material('M_WeatheredBridgeTimber',(.04,.06,.08),.85,.22,True),'ice':material('M_OpaqueFrostedIce',(.47,.63,.73),.34,.4),'snow':u.load_asset('/Game/TianNanGe/Revision_fdf5e67/Lookdev/M_PowderSnow')}
assert all(mats.values())
loaded={};report={'assets':[],'hidden_legacy_actors':[],'new_actors':[]}
for info in data['meshes']:
    path=DEST+'/Meshes/'+info['name']
    task=u.AssetImportTask()
    for k,v in dict(filename=str(ROOT/'Transfer_BridgeReference'/(info['name']+'.obj')),destination_path=DEST+'/Meshes',destination_name=info['name'],automated=True,replace_existing=True,save=True).items():task.set_editor_property(k,v)
    options=u.FbxImportUI()
    for k,v in dict(import_mesh=True,import_as_skeletal=False,import_materials=False,import_textures=False,import_animations=False,automated_import_should_detect_type=False,mesh_type_to_import=u.FBXImportType.FBXIT_STATIC_MESH).items():options.set_editor_property(k,v)
    for k,v in dict(combine_meshes=True,convert_scene=False,convert_scene_unit=False,force_front_x_axis=False,import_uniform_scale=1.,generate_lightmap_u_vs=False,auto_generate_collision=False,normal_import_method=u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS).items():options.static_mesh_import_data.set_editor_property(k,v)
    task.set_editor_property('options',options);asset_tools.import_asset_tasks([task])
    mesh=next((assets.load_asset(p) for p in task.imported_object_paths if isinstance(assets.load_asset(p),u.StaticMesh)),None)
    assert mesh,info['name']
    mesh.set_material(0,mats[info['material']])
    settings=mesh.get_editor_property('nanite_settings');settings.set_editor_property('enabled',False)
    settings.set_editor_property('fallback_relative_error',0.0)
    settings.set_editor_property('fallback_percent_triangles',1.0)
    settings.set_editor_property('position_precision',-2147483648)
    u.get_editor_subsystem(u.StaticMeshEditorSubsystem).set_nanite_settings(mesh,settings,True)
    body=mesh.get_editor_property('body_setup')
    if body:body.set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    assets.save_loaded_asset(mesh);loaded[info['name']]=mesh
    report['assets'].append(dict(asset=mesh.get_path_name(),bounds=str(mesh.get_bounds()),triangles=info['triangles']))

# Only change the bridge after every import has succeeded. All original actors remain recoverable.
with u.ScopedEditorTransaction('Match foreground bridge to TianNanGe painting'):
    for a in list(actors.get_all_level_actors()):
        folder=str(a.get_folder_path())
        if folder=='Reference/Bridge':actors.destroy_actor(a);continue
        label=a.get_actor_label()
        replace=folder in ['TianNanGe_Blockout/Bridge/ExtendedRailings','Lookdev/Bridge snow','TianNanGe_Blockout/Bridge']
        if replace and isinstance(a,u.StaticMeshActor):
            a.modify();a.static_mesh_component.modify();a.static_mesh_component.set_visibility(False,True);a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
            report['hidden_legacy_actors'].append(a.get_path_name())
    for info in data['meshes']:
        a=actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(0,0,0),u.Rotator(pitch=0,yaw=0,roll=0))
        a.set_actor_label('Reference Bridge '+info['name'].replace('SM_Bridge_',''));a.set_folder_path('Reference/Bridge')
        a.modify();c=a.static_mesh_component;c.set_static_mesh(loaded[info['name']]);c.set_material(0,mats[info['material']])
        c.set_collision_enabled(u.CollisionEnabled.QUERY_AND_PHYSICS if info['name'].endswith('Deck') else u.CollisionEnabled.NO_COLLISION)
        report['new_actors'].append(a.get_path_name())
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
report['lights_and_cameras_edited']=False
(ROOT/'Tools/Live/bridge-import.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
u.log('REFERENCE_BRIDGE_IMPORTED')
