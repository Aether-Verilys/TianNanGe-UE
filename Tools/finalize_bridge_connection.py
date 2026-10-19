import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];actors=u.get_editor_subsystem(u.EditorActorSubsystem);changed=[]
for a in actors.get_all_level_actors():
    if str(a.get_folder_path())!='TianNanGe_Blockout/Bridge/BridgeConnections':continue
    p=a.get_actor_location()
    if p.x<0:continue
    a.modify();p.x=2340;a.set_actor_location(p,False,False)
    if a.get_actor_label()=='FarAbutment':
        scale=a.get_actor_scale3d();scale.x=3.8;a.set_actor_scale3d(scale)
    changed.append(a.get_actor_label())
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(root/'Tools/Live/bridge-connections.json').write_text(json.dumps({'adjusted_far_platform':changed,'new_start_x_cm':2150,'new_end_x_cm':2530,'lights_edited':False},indent=2))
