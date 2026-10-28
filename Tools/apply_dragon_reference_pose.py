"""Reapply the reviewed dragon pose to the current EasySnow level.

Run inside UE 5.8. Keeps the imported skeletal mesh and reference skeleton intact;
stores bone transforms in a dedicated, non-playing AnimSequence.
"""
import json
from pathlib import Path
import unreal as u

ROOT = Path(__file__).resolve().parents[1]
MAP = '/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow'
POSE = '/Game/TianNanGe/Dragon/Poses/AS_Dragon_ReferencePose'
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith(MAP + '.'), 'Open TianNanGe_EasySnow first'
data = json.loads((ROOT/'SourceAssets/DragonReferencePose/pose.json').read_text())
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
matches = [a for a in actors.get_all_level_actors() if a.get_actor_label() == 'dragon_Skeleton']
assert len(matches) == 1, 'Expected exactly one dragon_Skeleton actor'
actor = matches[0]
component = actor.get_component_by_class(u.SkeletalMeshComponent)
mesh = component.skeletal_mesh_asset
assert mesh.get_path_name() == '/Game/TianNanGe/Dragon/dragon.dragon'
assets = u.get_editor_subsystem(u.EditorAssetSubsystem)
sequence = assets.load_asset(POSE) if assets.does_asset_exist(POSE) else None
if sequence is None:
    factory = u.AnimSequenceFactory()
    factory.target_skeleton = mesh.skeleton
    factory.preview_skeletal_mesh = mesh
    sequence = u.AssetToolsHelpers.get_asset_tools().create_asset(
        'AS_Dragon_ReferencePose', '/Game/TianNanGe/Dragon/Poses', u.AnimSequence, factory)
assert sequence.get_skeleton() == mesh.skeleton

with u.ScopedEditorTransaction('Dragon reference camera pose'):
    controller = sequence.controller
    controller.open_bracket('Dragon reference camera pose')
    try:
        controller.set_frame_rate(u.FrameRate(30, 1))
        controller.set_number_of_frames(u.FrameNumber(1))
        for name, transform in data['bones'].items():
            controller.add_bone_curve(name)
            assert controller.set_bone_track_keys(
                name, [u.Vector(*transform['location'])]*2,
                [u.Quat(*transform['rotation'])]*2,
                [u.Vector(*transform['scale'])]*2), name
    finally:
        controller.close_bracket()
    actor.modify()
    component.modify()
    actor.set_actor_location(u.Vector(*data['location']), False, False)
    actor.set_actor_rotation(u.Quat(*data['rotation']).rotator(), False)
    actor.set_actor_scale3d(u.Vector(*data['scale']))
    component.override_animation_data(sequence, False, False, 0.0, 1.0)
    component.set_editor_property('use_ref_pose_on_init_anim', False)
    component.set_update_animation_in_editor(True)
    component.set_position(0.0, False)
    # The old static dragon was hidden only for the previous editor session.
    # Persist that replacement state without deleting the original actor.
    for old in actors.get_all_level_actors():
        if old.get_actor_label() == 'dragon' and isinstance(old, u.StaticMeshActor):
            old.modify()
            old.set_actor_hidden_in_game(True)
            old.set_is_temporarily_hidden_in_editor(True)
            old_mesh = old.get_component_by_class(u.StaticMeshComponent)
            old_mesh.modify()
            old_mesh.set_editor_property('visible', False)
            old_mesh.set_editor_property('hidden_in_game', True)

# The replacement dragon was newly imported in the user's live session. Save
# its dependencies as well so reopening the level cannot lose the replacement.
assert assets.save_directory('/Game/TianNanGe/Dragon', only_if_is_dirty=True, recursive=True)
assert assets.save_loaded_asset(sequence, only_if_is_dirty=False)
assert u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
u.log('DRAGON_REFERENCE_POSE_SAVED ' + POSE)
