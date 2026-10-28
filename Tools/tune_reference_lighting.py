import unreal as u,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
command=globals().get('COMMAND',{})
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
bylabel={a.get_actor_label():a for a in actors.get_all_level_actors()}
with u.ScopedEditorTransaction('Balance reference lighting softness and atmosphere'):
 sun=bylabel['DirectionalLight'];c=sun.get_component_by_class(u.DirectionalLightComponent);c.modify()
 sun.modify();sun.set_actor_rotation(u.Rotator(pitch=-18,yaw=105,roll=0),True)
 c.set_intensity(44000);c.set_editor_property('light_source_angle',4.)
 sky=bylabel['Lookdev Cold environment'];c=sky.get_component_by_class(u.SkyLightComponent);c.modify()
 c.set_intensity(5200);c.set_light_color(u.LinearColor(.82,.92,1,1))
 for label,intensity,temp,width,height in [
  ('Reference - Hero warm rim',150000,4800,100,180),
  ('Reference - Hero soft key',45000,5900,180,220),
  ('Reference - Dragon sculpting key',200000,5600,450,320)]:
  c=bylabel[label].get_component_by_class(u.RectLightComponent);c.modify();c.set_intensity(intensity);c.set_temperature(temp)
  c.set_editor_property('source_width',width);c.set_editor_property('source_height',height)
  c.set_editor_property('specular_scale',.6 if 'Dragon' in label else .8)
 pp=bylabel['Lookdev Reference grade EV12'];pp.modify();s=pp.settings
 for k,v in {'auto_exposure_bias':-11.85,'white_temp':4800.,'color_contrast':u.Vector4(1.,1.,1.,1.),'color_saturation':u.Vector4(.92,.92,.92,1.),'bloom_intensity':1.5,'film_toe':.47}.items():
  s.set_editor_property(k,v);s.set_editor_property('override_'+k,True)
 pp.set_editor_property('settings',s)
 c=bylabel['Lookdev Blue depth haze'].component;c.modify()
 for k,v in {'fog_density':.78,'fog_max_opacity':.82,'start_distance':350.,'fog_inscattering_luminance':u.LinearColor(1550,2400,3400,0),'volumetric_fog_extinction_scale':.85}.items():c.set_editor_property(k,v)
u.get_editor_subsystem(u.LevelEditorSubsystem).editor_invalidate_viewports()
print('LIGHTING_BALANCE_ITERATION_02')
