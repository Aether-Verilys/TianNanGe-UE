"""Create original raymarched cloud banks along both sides of the reference bridge."""
import unreal as u,json,math,shutil,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
assets=u.get_editor_subsystem(u.EditorAssetSubsystem);actor_api=u.get_editor_subsystem(u.EditorActorSubsystem);mel=u.MaterialEditingLibrary
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert '/EasySnowIntegration/Maps/' in world.get_path_name()
actors=actor_api.get_all_level_actors()
backup=root/'Backups'/('CloudSea_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));backup.mkdir(parents=True)
shutil.copy2(root/'Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap',backup/'TianNanGe_EasySnow.umap')
dest='/Game/TianNanGe/CloudSea';path=dest+'/Materials/M_CloudSea_Raymarch'
m=assets.load_asset(path) if assets.does_asset_exist(path) else u.AssetToolsHelpers.get_asset_tools().create_asset('M_CloudSea_Raymarch',dest+'/Materials',u.Material,u.MaterialFactoryNew())
assert m
mel.delete_all_material_expressions(m)
m.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT)
m.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property('two_sided',True)
m.set_editor_property('use_translucency_vertex_fog',False)
m.set_editor_property('apply_cloud_fogging',False)
m.set_editor_property('translucency_pass',u.MaterialTranslucencyPass.MTP_BEFORE_DOF)
nodes={}
for name,cls in [('WorldPos',u.MaterialExpressionWorldPosition),('CameraPos',u.MaterialExpressionCameraPositionWS),('SceneDepthCm',u.MaterialExpressionSceneDepth),('PixelDepthCm',u.MaterialExpressionPixelDepth),('TimeSeconds',u.MaterialExpressionTime),('Facing',u.MaterialExpressionTwoSidedSign)]:
    nodes[name]=mel.create_material_expression(m,cls,-900,len(nodes)*130)
scalars={'Density':.65,'Extinction':.009,'NoiseScale':150.,'WindSpeed':4.,'Seed':0.,'StepCount':40.,'Brightness':1.0,'BridgeY':0.}
vectors={'CloudCenter':(0,0,-150),'CloudExtent':(650,500,175),'ShadowColor':(900,1350,1900),'HighlightColor':(4600,5200,5900),'SunDirection':(.29,-.95,.104)}
for name,value in scalars.items():
    node=mel.create_material_expression(m,u.MaterialExpressionScalarParameter,-600,len(nodes)*100)
    node.set_editor_property('parameter_name',name);node.set_editor_property('default_value',value);node.set_editor_property('group','云海');nodes[name]=node
for name,value in vectors.items():
    node=mel.create_material_expression(m,u.MaterialExpressionVectorParameter,-350,len(nodes)*100)
    node.set_editor_property('parameter_name',name);node.set_editor_property('default_value',u.LinearColor(*value,1));node.set_editor_property('group','云海');nodes[name]=node
custom=mel.create_material_expression(m,u.MaterialExpressionCustom,100,100)
custom.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT4)
custom.set_editor_property('code',(root/'Tools/Shaders/CloudSeaRaymarch.ush').read_text())
inputs=[]
for name in nodes:
    i=u.CustomInput();i.set_editor_property('input_name',name);inputs.append(i)
custom.set_editor_property('inputs',inputs)
for name,node in nodes.items():
    assert mel.connect_material_expressions(node,'RGB' if name in vectors else '',custom,name)
for prop,rgb in [(u.MaterialProperty.MP_EMISSIVE_COLOR,True),(u.MaterialProperty.MP_OPACITY,False)]:
    mask=mel.create_material_expression(m,u.MaterialExpressionComponentMask,500,100 if rgb else 300)
    for key in ['r','g','b']:mask.set_editor_property(key,rgb)
    mask.set_editor_property('a',not rgb)
    assert mel.connect_material_expressions(custom,'',mask,'')
    assert mel.connect_material_property(mask,'',prop)
mel.recompile_material(m);assert assets.save_loaded_asset(m)
cube=u.load_asset('/Engine/BasicShapes/Cube');assert cube
# Sample the actual deformed bridge export without re-running its generator.
vertices=[]
for line in (root/'Transfer_BridgeReference/SM_Bridge_Snow_Deck.obj').read_text().splitlines():
    if line.startswith('v '):
        x,y,z=map(float,line.split()[1:]);vertices.append((x,-y,z))
sunlight=next(a for a in actors if isinstance(a,u.DirectionalLight))
sun=-sunlight.get_actor_forward_vector()
report={'material':m.get_path_name(),'actors':[],'backup':str(backup),'shader':'original procedural 3D density and Beer-Lambert ray integration','external_textures':False}
for side in [-1,1]:
    for index,x in enumerate([100.,650.,1200.,1750.,2150.]):
        samples=[p for p in vertices if abs(p[0]-x)<40.]
        assert samples
        cy=sum(p[1] for p in samples)/len(samples);deck_z=sum(p[2] for p in samples)/len(samples)
        ext=(660.+index*45.,475.+index*35.,200.+index*10.)
        center=(x,cy+side*(470.+index*75.),deck_z-65.-index*8.)
        label=f'Cloud Sea - {"Left" if side<0 else "Right"} {index+1:02}'
        a=next((a for a in actors if a.get_actor_label()==label),None)
        a=a or actor_api.spawn_actor_from_class(u.StaticMeshActor,u.Vector(*center))
        a.modify();a.set_actor_label(label);a.set_folder_path('Lookdev/Cloud Sea')
        a.set_actor_location(u.Vector(*center),False,False);a.set_actor_scale3d(u.Vector(*(v/50. for v in ext)))
        c=a.static_mesh_component;c.set_static_mesh(cube);c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
        for key in ['cast_shadow','affect_distance_field_lighting','affect_dynamic_indirect_lighting']:c.set_editor_property(key,False)
        c.set_editor_property('translucency_sort_priority',-20-index)
        name=f'MI_CloudSea_{"L" if side<0 else "R"}_{index+1:02}';mipath=dest+'/Materials/'+name
        mi=assets.load_asset(mipath) if assets.does_asset_exist(mipath) else u.AssetToolsHelpers.get_asset_tools().create_asset(name,dest+'/Materials',u.MaterialInstanceConstant,u.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi,m)
        for key,value in {'CloudCenter':center,'CloudExtent':ext,'SunDirection':(sun.x,sun.y,sun.z)}.items():mel.set_material_instance_vector_parameter_value(mi,key,u.LinearColor(*value,1))
        for key,value in {'Seed':index*2.37+side*9.1,'BridgeY':cy,'Density':.58+index*.07}.items():mel.set_material_instance_scalar_parameter_value(mi,key,value)
        mel.update_material_instance(mi);assert assets.save_loaded_asset(mi);c.set_material(0,mi)
        report['actors'].append({'actor':a.get_path_name(),'label':label,'center':center,'extent':ext,'instance':mi.get_path_name()})
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(root/'Saved/cloud-sea.json').write_text(json.dumps(report,indent=2))
