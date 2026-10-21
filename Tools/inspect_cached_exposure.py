import unreal as u,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
out={'world':u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world().get_path_name(),'cvars':{},'postprocess':[],'skylights':[]}
for name in ['r.EyeAdaptation.CachedLightingPreExposure','r.EyeAdaptation.PreExposureOverride','r.UsePreExposure','r.DefaultFeature.AutoExposure']:
    out['cvars'][name]=u.SystemLibrary.get_console_variable_float_value(name)
for a in actors:
    if isinstance(a,u.PostProcessVolume):
        s=a.get_editor_property('settings');out['postprocess'].append({'name':a.get_actor_label(),'method':str(s.get_editor_property('auto_exposure_method')),'bias':s.get_editor_property('auto_exposure_bias'),'physical_camera':s.get_editor_property('auto_exposure_apply_physical_camera_exposure')})
    if isinstance(a,u.SkyLight):
        c=a.get_component_by_class(u.SkyLightComponent);out['skylights'].append({'name':a.get_actor_label(),'realtime':c.get_editor_property('real_time_capture'),'intensity':c.intensity})
folder=root/'Saved/Exposure';folder.mkdir(exist_ok=True)
(folder/'before.json').write_text(json.dumps(out,indent=2))
