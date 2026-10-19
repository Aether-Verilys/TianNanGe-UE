import unreal as u,json,math,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
commandlet=os.environ.get('TIANNANGE_BRIDGE_VALIDATE_RELOAD')=='1'
if commandlet:
    assert u.EditorLoadingAndSavingUtils.load_map(str(ROOT/'Content/TianNanGe/Maps/TianNanGe_ReferenceLook.umap'))
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
by_path={a.get_path_name():a for a in actors}
before=json.loads((ROOT/'Tools/Baselines/bridge-actors-before.json').read_text())
result={'engine':u.SystemLibrary.get_engine_version(),'errors':[],'lights_and_camera_preserved':True,'new_bridge':[],'legacy_bridge_hidden':0,'scene':u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name()}
def fail(s):result['errors'].append(s)
for d in before:
    if d['class_name'] not in ('DirectionalLight','SkyLight','CameraActor'):continue
    a=by_path.get(d['path'])
    if not a:fail('Missing light/camera: '+d['label']);continue
    p=a.get_actor_location();r=a.get_actor_rotation()
    actual=[p.x,p.y,p.z,r.pitch,r.yaw,r.roll];expected=d['position']+d['rotation']
    if any(abs(x-y)>(.5 if d['class_name']=='CameraActor' and i<3 else .001) for i,(x,y) in enumerate(zip(actual,expected))):fail('Transform changed: '+d['label'])
    if isinstance(a,u.DirectionalLight):value=a.get_component_by_class(u.DirectionalLightComponent).intensity
    elif isinstance(a,u.SkyLight):value=a.get_component_by_class(u.SkyLightComponent).intensity
    else:value=a.camera_component.field_of_view
    original=d.get('intensity',d.get('fov'))
    if abs(value-original)>.001:fail('Intensity/FOV changed: '+d['label'])
    if isinstance(a,u.DirectionalLight) and str(a.get_component_by_class(u.DirectionalLightComponent).light_color).split('{')[-1]!=d['color'].split('{')[-1]:fail('Light color changed')
result['lights_and_camera_preserved']=not result['errors']
for a in actors:
    if not isinstance(a,u.StaticMeshActor):continue
    f=str(a.get_folder_path());c=a.static_mesh_component
    if f in ['TianNanGe_Blockout/Bridge/ExtendedRailings','TianNanGe_Blockout/Bridge','Lookdev/Bridge snow']:
        if c.get_editor_property('visible'):fail('Legacy component still visible: '+a.get_actor_label())
        else:result['legacy_bridge_hidden']+=1
    if f=='Reference/Bridge':
        mesh=c.static_mesh;settings=mesh.get_editor_property('nanite_settings')
        result['new_bridge'].append({'label':a.get_actor_label(),'asset':mesh.get_path_name(),'visible':c.get_editor_property('visible'),'nanite':settings.get_editor_property('enabled'),'bounds':str(mesh.get_bounds()),'materials':[m.get_path_name() for m in c.get_materials()]})
        if not c.get_editor_property('visible'):fail('New bridge hidden')
        # The 5.8 automatic Nanite/fallback build loses small disconnected snow forms.
        # These modest-size bridge meshes intentionally render at their full original resolution.
        if settings.get_editor_property('enabled'):fail('Bridge should retain full non-Nanite geometry')
if len(result['new_bridge'])!=7:fail('Expected seven bridge mesh actors')
if result['legacy_bridge_hidden']!=309:fail('Unexpected legacy bridge actor count: '+str(result['legacy_bridge_hidden']))
result['passed']=not result['errors']
filename='bridge-validation-reloaded.json' if commandlet else 'bridge-validation-live.json'
(ROOT/filename).write_text(json.dumps(result,indent=2),encoding='utf-8')
assert result['passed'],result['errors']
u.log('BRIDGE_VALIDATION_PASSED')
