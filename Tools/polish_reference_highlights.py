import unreal as u
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
bylabel={a.get_actor_label():a for a in actors.get_all_level_actors()}
with u.ScopedEditorTransaction('Warm character and dragon rim highlights'):
 for label,intensity,temp in [('Reference - Hero warm rim',260000,4100),('Reference - Hero soft key',85000,4800)]:
  c=bylabel[label].get_component_by_class(u.RectLightComponent);c.modify();c.set_intensity(intensity);c.set_temperature(temp)
 label='Reference - Dragon warm rim'
 a=bylabel.get(label)
 position=u.Vector(260,100,490);target=u.Vector(80,-135,265)
 if a is None:a=actors.spawn_actor_from_class(u.RectLight,position,u.Rotator())
 a.modify();a.set_actor_label(label);a.set_folder_path('Lighting/Reference Look')
 a.set_actor_location(position,False,True);a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(position,target),True)
 a.tags=['TNG_ReferenceLighting']
 c=a.get_component_by_class(u.RectLightComponent);c.modify();c.set_mobility(u.ComponentMobility.MOVABLE)
 c.set_intensity_units(u.LightUnits.LUMENS);c.set_intensity(1000000);c.set_light_color(u.LinearColor(1,1,1,1));c.set_temperature(4300)
 for k,v in {'use_temperature':True,'source_width':110.,'source_height':300.,'attenuation_radius':1000.,'volumetric_scattering_intensity':0.,'indirect_lighting_intensity':0.,'cast_shadows':True,'specular_scale':.7}.items():c.set_editor_property(k,v)
 channels=c.get_editor_property('lighting_channels')
 for k,v in {'channel0':False,'channel1':False,'channel2':True}.items():channels.set_editor_property(k,v)
 c.set_editor_property('lighting_channels',channels)
u.get_editor_subsystem(u.LevelEditorSubsystem).editor_invalidate_viewports()
print('WARM_HIGHLIGHT_POLISH_APPLIED')
