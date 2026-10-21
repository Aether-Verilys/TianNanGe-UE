import unreal as u,json
from pathlib import Path
actors=u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors();out=[]
for a in actors:
    if not isinstance(a,(u.StaticMeshActor,u.SkyAtmosphere,u.ExponentialHeightFog)):continue
    if isinstance(a,u.StaticMeshActor) and 'sky' not in a.get_actor_label().lower():continue
    d={'label':a.get_actor_label(),'hidden_editor':a.is_hidden_ed()}
    for k in ['hidden','is_editor_only_actor']:
        try:d[k]=str(a.get_editor_property(k))
        except Exception:pass
    if isinstance(a,u.StaticMeshActor):
        c=a.static_mesh_component;d['fields']={}
        for k in ['visible','hidden_in_game','render_in_main_pass','owner_no_see','only_owner_see','ld_max_draw_distance','bounds_scale','cast_shadow']:
            try:d['fields'][k]=str(c.get_editor_property(k))
            except Exception:pass
        d['bounds']=str(a.get_actor_bounds(False));d['materials']=[str(m) for m in c.get_materials()]
    if isinstance(a,u.ExponentialHeightFog):
        fc=a.get_component_by_class(u.ExponentialHeightFogComponent)
        d['fog']={k:str(fc.get_editor_property(k)) for k in ['fog_density','enable_volumetric_fog','volumetric_fog_distance','fog_cutoff_distance']}
    out.append(d)
(Path(__file__).resolve().parents[1]/'Saved/ChaoticSkies/visibility.json').write_text(json.dumps(out,indent=2))
