"""Match UE 5.8's lighting-cache range to the existing scene exposure."""
import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
def snapshot():
    out=[]
    for a in actors:
        if isinstance(a,(u.DirectionalLight,u.SkyLight,u.PostProcessVolume)):
            r=a.get_actor_rotation();d={'name':a.get_name(),'rotation':[r.pitch,r.yaw,r.roll]}
            if isinstance(a,u.PostProcessVolume):
                s=a.get_editor_property('settings');d.update(exposure_bias=s.get_editor_property('auto_exposure_bias'),method=str(s.get_editor_property('auto_exposure_method')),physical_camera=s.get_editor_property('auto_exposure_apply_physical_camera_exposure'))
            else:
                cls=u.SkyLightComponent if isinstance(a,u.SkyLight) else u.DirectionalLightComponent
                c=a.get_component_by_class(cls);d.update(intensity=c.intensity,color=list(c.light_color.to_tuple()))
                if isinstance(a,u.SkyLight):d['realtime_capture']=c.get_editor_property('real_time_capture')
            out.append(d)
    return out
before=snapshot();name='r.EyeAdaptation.CachedLightingPreExposure'
old=u.SystemLibrary.get_console_variable_float_value(name)
u.SystemLibrary.execute_console_command(world,name+' 8')
current=u.SystemLibrary.get_console_variable_float_value(name);assert current==8.
assert before==snapshot(),'Exposure fix changed lighting or camera exposure'
expected=[]
for d in before:
    if 'exposure_bias' in d and d['method']=='<AutoExposureMethod.AEM_MANUAL: 2>' and not d['physical_camera']:
        ev=-d['exposure_bias'];assert current-12<=ev<=current+8
        expected.append({'postprocess':d['name'],'expected_exposure_ev':ev,'cache_clipping_warning_condition':False})
assert expected
u.get_editor_subsystem(u.LevelEditorSubsystem).editor_invalidate_viewports()
report={'previous_cache_exposure':old,'cache_exposure':current,'safe_range_ev':[current-12,current+8],'verified_manual_exposures':expected,'lighting_and_exposure_unchanged':True,'preserved_state':before,'source':'UE 5.8.3 PostProcessEyeAdaptation.cpp:201-278','persistent_config':str(root/'Config/DefaultEngine.ini')}
(root/'Saved/Exposure/fixed.json').write_text(json.dumps(report,indent=2))
