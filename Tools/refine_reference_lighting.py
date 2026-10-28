"""Tune the live scene lighting with a recoverable live-map backup."""
import unreal as u,json,shutil,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'SourceAssets/ReferenceLighting_20261028';OUT.mkdir(exist_ok=True)
CAP=ROOT/'Captures/ReferenceLighting_20261028';CAP.mkdir(exist_ok=True)
command=globals().get('COMMAND',{})
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
assert world.get_path_name().startswith('/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.')
allactors=actors.get_all_level_actors()
bylabel={a.get_actor_label():a for a in allactors}
pp=bylabel['Lookdev Reference grade EV12']
sun=bylabel['DirectionalLight'];sky=bylabel['Lookdev Cold environment'];fog=bylabel['Lookdev Blue depth haze']
hero=bylabel['LittleGreen_Animated_StrongWind'];dragon=bylabel['Dragon_X_Breathing']
def tf(a):
 t=a.get_actor_transform()
 return {'location':[t.translation.x,t.translation.y,t.translation.z],'rotation':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'scale':[t.scale3d.x,t.scale3d.y,t.scale3d.z]}
def val(obj,k):
 try:
  v=obj.get_editor_property(k)
  return v if isinstance(v,(bool,int,float,str)) else str(v)
 except Exception:return None
keys=['intensity','light_color','temperature','use_temperature','volumetric_scattering_intensity','indirect_lighting_intensity','light_source_angle','lighting_channels','source_radius','attenuation_radius']
ppkeys=['bloom_intensity','bloom_method','bloom_threshold','lens_flare_intensity','scene_fringe_intensity','vignette_intensity','white_temp','white_tint','auto_exposure_bias','color_saturation','color_contrast','color_gain_shadows','color_gain_highlights','color_gain','motion_blur_amount']
fogkeys=['fog_density','fog_height_falloff','start_distance','fog_max_opacity','fog_inscattering_luminance','volumetric_fog_extinction_scale','volumetric_fog_scattering_distribution']
before={'time':time.time(),'actors':[{'name':a.get_name(),'label':a.get_actor_label(),'transform':tf(a)} for a in allactors],
 'lights':[{'label':a.get_actor_label(),'transform':tf(a),'values':{k:val(c,k) for k in keys}} for a in allactors for c in a.get_components_by_class(u.LightComponentBase)],
 'postprocess':{k:val(pp.settings,k) for k in ppkeys+['override_'+k for k in ppkeys]},'fog':{k:val(fog.component,k) for k in fogkeys},
 'hero_channels':str(hero.skeletal_mesh_component.get_editor_property('lighting_channels')),
 'dragon_channels':str(dragon.skeletal_mesh_component.get_editor_property('lighting_channels'))}
mapfile=ROOT/'Content/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow.umap'
if not (OUT/'Before_Lighting.json').exists():
 shutil.copy2(mapfile,OUT/'TianNanGe_EasySnow_DiskBefore.umap')
 assert level.save_current_level()
 shutil.copy2(mapfile,OUT/'TianNanGe_EasySnow_LiveBefore.umap')
 (OUT/'Before_Lighting.json').write_text(json.dumps(before,indent=2))
 source=ROOT/'Captures/ReferenceReview_20261028/Current_MainCamera.png'
 if source.exists():shutil.copy2(source,CAP/'Before.png')

def channels(c,c0,c1,c2):
 ch=c.get_editor_property('lighting_channels')
 ch.set_editor_property('channel0',c0);ch.set_editor_property('channel1',c1);ch.set_editor_property('channel2',c2)
 c.set_editor_property('lighting_channels',ch)
def rect(label,position,target,intensity,temperature,width,height,radius,channel):
 a=bylabel.get(label)
 if a is None:a=actors.spawn_actor_from_class(u.RectLight,u.Vector(*position),u.Rotator())
 a.modify();a.set_actor_label(label);a.set_folder_path('Lighting/Reference Look')
 a.set_actor_location(u.Vector(*position),False,True)
 a.set_actor_rotation(u.MathLibrary.find_look_at_rotation(u.Vector(*position),u.Vector(*target)),True)
 c=a.get_component_by_class(u.RectLightComponent);c.modify();c.set_mobility(u.ComponentMobility.MOVABLE)
 c.set_intensity_units(u.LightUnits.LUMENS);c.set_intensity(intensity)
 c.set_light_color(u.LinearColor(1,1,1,1));c.set_temperature(temperature);c.set_editor_property('use_temperature',True)
 for k,v in {'source_width':width,'source_height':height,'attenuation_radius':radius,'volumetric_scattering_intensity':0.,'indirect_lighting_intensity':0.,'cast_shadows':True}.items():c.set_editor_property(k,v)
 channels(c,False,channel==1,channel==2)
 a.tags=list(dict.fromkeys([str(t) for t in a.tags]+['TNG_ReferenceLighting']))
 return a

with u.ScopedEditorTransaction('Reference lighting and postprocess refinement'):
 sun.modify();sc=sun.get_component_by_class(u.DirectionalLightComponent);sc.modify()
 sun.set_actor_rotation(u.Rotator(pitch=-26,yaw=50,roll=0),True)
 sc.set_intensity(45000);sc.set_light_color(u.LinearColor(1,1,1,1));sc.set_temperature(5300);sc.set_editor_property('use_temperature',True)
 sc.set_editor_property('light_source_angle',2.5);sc.set_editor_property('volumetric_scattering_intensity',.35)
 sky.modify();sk=sky.get_component_by_class(u.SkyLightComponent);sk.modify()
 sk.set_intensity(2800);sk.set_light_color(u.LinearColor(.88,.94,1,1));sk.set_editor_property('volumetric_scattering_intensity',1.)
 for a in [hero,dragon]:a.modify();a.skeletal_mesh_component.modify()
 channels(hero.skeletal_mesh_component,True,True,False)
 channels(dragon.skeletal_mesh_component,True,False,True)
 rect('Reference - Hero warm rim',(160,150,280),(0,32,160),220000,4700,70,140,600,1)
 rect('Reference - Hero soft key',(-170,-100,255),(0,30,165),110000,5500,130,160,500,1)
 rect('Reference - Dragon sculpting key',(-280,-340,560),(70,-120,205),650000,5400,300,220,1200,2)
 for label in ['Dragon_EyeGold_L','Dragon_EyeGold_R']:
  a=bylabel[label];a.modify();c=a.get_component_by_class(u.PointLightComponent);c.modify()
  c.set_intensity(6000);c.set_light_color(u.LinearColor(1,.66,.22,1))
 pp.modify();settings=pp.settings
 ppvalues={'bloom_intensity':2.5,'lens_flare_intensity':.18,'scene_fringe_intensity':0.,'vignette_intensity':.23,'white_temp':5400.,'white_tint':0.,'color_saturation':u.Vector4(.93,.93,.93,1.),'color_contrast':u.Vector4(1.03,1.03,1.03,1.),'motion_blur_amount':.08}
 for k,v in ppvalues.items():
  settings.set_editor_property(k,v);settings.set_editor_property('override_'+k,True)
 pp.set_editor_property('settings',settings)
 fog.modify();fc=fog.component;fc.modify()
 for k,v in {'fog_density':.58,'fog_max_opacity':.75,'start_distance':700.,'fog_inscattering_luminance':u.LinearColor(1700,2300,3000,0),'volumetric_fog_extinction_scale':.8,'volumetric_fog_scattering_distribution':.25}.items():fc.set_editor_property(k,v)
level.editor_set_viewport_realtime(True);level.editor_invalidate_viewports()
(OUT/'Applied_Values.json').write_text(json.dumps({'sun_lux':sc.intensity,'sun_rotation':str(sun.get_actor_rotation()),'sky_intensity':sk.intensity,'postprocess':{k:val(settings,k) for k in ppkeys},'fog':{k:val(fc,k) for k in fogkeys}},indent=2))
print('LIGHTING_APPLIED_NOT_YET_SAVED')
