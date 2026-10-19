"""Read current live edits without saving/reloading/mutating the scene."""
import unreal as u,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
def value(obj,key):
    try:
        v=obj.get_editor_property(key)
        return v if isinstance(v,(str,int,float,bool)) else str(v)
    except Exception:return None
report={'time':time.time(),'world':world.get_path_name(),'selected':[a.get_actor_label() for a in actors.get_selected_level_actors()],'dirty_maps':[p.get_path_name() for p in u.EditorLoadingAndSavingUtils.get_dirty_map_packages()],'lights':[],'fog':[],'postprocess':[],'materials':{},'sky_meshes':[]}
for a in actors.get_all_level_actors():
    if isinstance(a,(u.DirectionalLight,u.SkyLight,u.PointLight,u.RectLight,u.SpotLight)):
        cls=u.SkyLightComponent if isinstance(a,u.SkyLight) else u.LightComponent
        c=a.get_component_by_class(cls)
        report['lights'].append({'label':a.get_actor_label(),'path':a.get_path_name(),'rotation':str(a.get_actor_rotation()),'forward':str(a.get_actor_forward_vector()),'component':{k:value(c,k) for k in ['intensity','mobility','visible','affects_world','cast_shadows','lighting_channels','light_color','indirect_lighting_intensity','volumetric_scattering_intensity','atmosphere_sun_light','light_source_angle','source_type','real_time_capture','cubemap','light_units']}})
    elif isinstance(a,u.ExponentialHeightFog):
        c=a.get_component_by_class(u.ExponentialHeightFogComponent)
        report['fog'].append({k:value(c,k) for k in ['fog_density','fog_height_falloff','start_distance','fog_inscattering_luminance','enable_volumetric_fog','volumetric_fog_distance']})
    elif isinstance(a,u.PostProcessVolume):
        s=a.get_editor_property('settings')
        report['postprocess'].append({'label':a.get_actor_label(),'unbound':value(a,'unbound'),'priority':value(a,'priority'),'settings':{k:value(s,k) for k in ['auto_exposure_method','auto_exposure_bias','auto_exposure_apply_physical_camera_exposure','dynamic_global_illumination_method','reflection_method','color_gain_shadows','color_offset_shadows']}})
    elif isinstance(a,u.StaticMeshActor):
        c=a.static_mesh_component
        for i in range(c.get_num_materials()):
            m=c.get_material(i)
            if not m or m.get_path_name() in report['materials']:continue
            report['materials'][m.get_path_name()]={k:value(m,k) for k in ['shading_model','blend_mode','is_sky','two_sided','used_with_nanite']}
        if 'sky' in a.get_actor_label().lower():report['sky_meshes'].append({'label':a.get_actor_label(),'cast_shadow':value(c,'cast_shadow'),'visible':value(c,'visible'),'affect_dynamic_indirect_lighting':value(c,'affect_dynamic_indirect_lighting')})
(ROOT/'Tools/Live/direct-light-diagnosis.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
