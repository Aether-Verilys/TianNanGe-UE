import unreal as u,json,shutil,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'SourceAssets/UECharacterLoop_20261028';OUT.mkdir(exist_ok=True)
actors=u.get_editor_subsystem(u.EditorActorSubsystem);level=u.get_editor_subsystem(u.LevelEditorSubsystem);assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world();MAP='/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow'
assert world.get_path_name().startswith(MAP+'.')
mesh=assets.load_asset('/Game/TianNanGe/Character/ornate-sword')
anim=assets.load_asset('/Game/TianNanGe/Character/LittleGreenArmature_001_TianNan_Breath_StrongWind_Loop_8s')
assert mesh and anim and mesh.skeleton==anim.get_skeleton()
allactors=actors.get_all_level_actors();old=next(a for a in allactors if a.get_actor_label()=='tripo_node_4dee5643')
oldpieces=[a for a in allactors if isinstance(a,u.StaticMeshActor) and str(a.get_folder_path()).startswith('PlayerArmature/Character/Visual_LittleGreen')]
assert len(oldpieces)==27
src=ROOT/'Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap'
disk=OUT/'TianNanGe_EasySnow_DiskBefore.umap'
if not disk.exists():shutil.copy2(src,disk)
assert level.save_current_level()
live=OUT/'TianNanGe_EasySnow_LiveBefore.umap'
if not live.exists():shutil.copy2(src,live)
def vec(v):return [v.x,v.y,v.z]
def tf(a):
 t=a.get_actor_transform();return {'location':vec(t.translation),'rotation':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'scale':vec(t.scale3d)}
before={'world':world.get_path_name(),'actors':[dict(name=a.get_name(),label=a.get_actor_label(),transform=tf(a),hidden=a.is_hidden_ed()) for a in allactors],
 'old_character':[dict(name=a.get_name(),label=a.get_actor_label(),transform=tf(a),visible=a.static_mesh_component.get_editor_property('visible'),hidden_in_game=a.static_mesh_component.get_editor_property('hidden_in_game')) for a in oldpieces]}
if not (OUT/'before_replacement.json').exists():(OUT/'before_replacement.json').write_text(json.dumps(before,indent=2))
with u.ScopedEditorTransaction('Replace static LittleGreen with looping animated character'):
 matches=[a for a in allactors if a.get_actor_label()=='LittleGreen_Animated_StrongWind']
 actor=matches[0] if matches else actors.spawn_actor_from_class(u.SkeletalMeshActor,old.get_actor_location(),u.Rotator(pitch=0,yaw=80,roll=0))
 actor.modify();actor.set_actor_label('LittleGreen_Animated_StrongWind');actor.set_folder_path('Characters/Animated')
 actor.set_actor_location(old.get_actor_location(),False,True);actor.set_actor_rotation(u.Rotator(pitch=0,yaw=80,roll=0),True);actor.set_actor_scale3d(u.Vector(1.96,1.96,1.96))
 c=actor.skeletal_mesh_component;c.modify();c.set_skeletal_mesh_asset(mesh)
 c.set_mobility(u.ComponentMobility.MOVABLE);c.set_simulate_physics(False);c.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
 c.override_animation_data(anim,True,True,0.,1.)
 c.set_editor_property('use_ref_pose_on_init_anim',False);c.set_update_animation_in_editor(True);c.set_component_tick_enabled(True)
 c.set_editor_property('visibility_based_anim_tick_option',u.VisibilityBasedAnimTickOption.ALWAYS_TICK_POSE_AND_REFRESH_BONES)
 c.set_bounds_scale(1.5)
 actor.tags=list(actor.tags)+['TNG_AnimatedCharacter','TNG_StrongWindLoop_8s']
 for a in oldpieces:
  a.modify();a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
  component=a.static_mesh_component;component.modify();component.set_visibility(False,True);component.set_hidden_in_game(True,True);component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
 actor.set_actor_hidden_in_game(False);c.set_visibility(True,True);c.set_hidden_in_game(False,True)
level.editor_set_viewport_realtime(False);level.editor_set_viewport_realtime(True)
actors.set_selected_level_actors([actor])
assert assets.save_directory('/Game/TianNanGe/Character',only_if_is_dirty=True,recursive=True)
assert level.save_current_level()
report={'world':world.get_path_name(),'actor':actor.get_actor_label(),'actor_path':actor.get_path_name(),'transform':tf(actor),'mesh':mesh.get_path_name(),'animation':anim.get_path_name(),'duration':anim.sequence_length,'hidden_static_actors':len(oldpieces),'animation_data':str(c.animation_data),'num_bones':c.get_num_bones()}
(OUT/'replacement_result.json').write_text(json.dumps(report,indent=2))
print('CHARACTER_REPLACED',json.dumps(report))
