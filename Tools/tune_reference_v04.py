import unreal as u,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
for a in actors.get_all_level_actors():
    if isinstance(a,u.ExponentialHeightFog):
        c=a.get_component_by_class(u.ExponentialHeightFogComponent);c.set_editor_property('fog_density',.22);c.set_editor_property('start_distance',600.0)
    elif isinstance(a,u.PostProcessVolume):
        s=a.get_editor_property('settings')
        for key,value in dict(auto_exposure_bias=-12.0,color_saturation=u.Vector4(.94,.94,.94,1),color_gain_shadows=u.Vector4(.85,1.0,1.17,1),color_offset_shadows=u.Vector4(.004,.012,.025,0)).items():
            s.set_editor_property('override_'+key,True);s.set_editor_property(key,value)
        a.set_editor_property('settings',s)
    elif a.get_actor_label()=='Lookdev Warm backlight':
        a.set_actor_rotation(u.MathLibrary.make_rot_from_x(u.Vector(-.94,-.06,-.36)),False)
    elif a.get_actor_label()=='dragon':
        a.modify();a.set_actor_location(u.Vector(204.0648,41.7084,-29.5042),False,False);a.set_actor_scale3d(u.Vector(1.848,1.848,1.848))
    elif isinstance(a,u.StaticMeshActor) and a.static_mesh_component.get_material(0) and a.static_mesh_component.get_material(0).get_name()=='M_008':
        a.modify();a.set_actor_location(u.Vector(3850,-350,a.get_actor_location().z),False,False)
sky=assets.load_asset('/Game/TianNanGe/Revision_fdf5e67/Lookdev/M_WinterSky')
expression=u.MaterialEditingLibrary.get_material_property_input_node(sky,u.MaterialProperty.MP_EMISSIVE_COLOR)
expression.set_editor_property('code','float3 d=normalize(D);float h=saturate(d.z*1.8);float3 c=lerp(float3(3900,4900,5600),float3(1600,2550,3400),h);float sun=saturate(dot(d,normalize(float3(.94,.06,.36))));c+=float3(4200,3200,1800)*pow(sun,28);c+=float3(42000,31000,16000)*pow(sun,1400);return c*2.2;')
u.MaterialEditingLibrary.recompile_material(sky);assets.save_loaded_asset(sky)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(ROOT/'Tools/Live/tuning-v04.json').write_text(json.dumps({'fog_density':.22,'fixed_ev':12,'dragon_scale_relative_to_source':1.32,'sky_radiance_scale':2.2,'far_pavilion_location':[3850,-350]}))
