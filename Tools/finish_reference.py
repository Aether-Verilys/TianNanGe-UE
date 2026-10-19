"""Final native snow detail and restrained highlight/midtone grading."""
import unreal as u,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST='/Game/TianNanGe/Revision_fdf5e67'
assets=u.get_editor_subsystem(u.EditorAssetSubsystem)
tools=u.AssetToolsHelpers.get_asset_tools()
texture_path=DEST+'/Lookdev/T_Source_Snow_Normal'
if assets.does_asset_exist(texture_path):normal=assets.load_asset(texture_path)
else:
    task=u.AssetImportTask()
    for key,value in dict(filename='D:/Dev/TianNanGe/Project_TianNanGe/Assets/TianNanGe/Effects/Snow/SurfaceSnow/Textures/Snow_1_Normal.tga',destination_path=DEST+'/Lookdev',destination_name='T_Source_Snow_Normal',automated=True,save=True,replace_existing=False).items():task.set_editor_property(key,value)
    tools.import_asset_tasks([task]);normal=assets.load_asset(texture_path)
assert normal
normal.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP);normal.set_editor_property('srgb',False);normal.set_editor_property('flip_green_channel',True);assets.save_loaded_asset(normal)
mat=assets.load_asset(DEST+'/Lookdev/M_PowderSnow')
def node(cls,x,y):return u.MaterialEditingLibrary.create_material_expression(mat,cls,x,y)
def link(a,p,b,i):assert u.MaterialEditingLibrary.connect_material_expressions(a,p,b,i),(a,b,i)
uv=node(u.MaterialExpressionTextureCoordinate,-800,600);uv.set_editor_property('u_tiling',12.0);uv.set_editor_property('v_tiling',12.0)
t=node(u.MaterialExpressionTextureSample,-600,600);t.set_editor_property('texture',normal);t.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_NORMAL);link(uv,'',t,'UVs')
strength=node(u.MaterialExpressionConstant3Vector,-600,850);strength.set_editor_property('constant',u.LinearColor(.2,.2,1))
multiply=node(u.MaterialExpressionMultiply,-350,600);link(t,'RGB',multiply,'A');link(strength,'',multiply,'B')
normalize=node(u.MaterialExpressionNormalize,-100,600);link(multiply,'',normalize,'VectorInput')
assert u.MaterialEditingLibrary.connect_material_property(normalize,'',u.MaterialProperty.MP_NORMAL)
mat.set_editor_property('used_with_nanite',True);u.MaterialEditingLibrary.recompile_material(mat);assets.save_loaded_asset(mat)
actors=u.get_editor_subsystem(u.EditorActorSubsystem)
for a in actors.get_all_level_actors():
    if isinstance(a,u.ExponentialHeightFog):a.get_component_by_class(u.ExponentialHeightFogComponent).set_editor_property('fog_density',.18)
    elif isinstance(a,u.PostProcessVolume):
        s=a.get_editor_property('settings')
        for key,value in dict(color_gain_highlights=u.Vector4(1.12,1.03,.86,1),color_gamma_midtones=u.Vector4(1.06,1.06,1.06,1)).items():
            s.set_editor_property('override_'+key,True);s.set_editor_property(key,value)
        a.set_editor_property('settings',s)
u.get_editor_subsystem(u.LevelEditorSubsystem).save_current_level()
(ROOT/'Tools/Live/final-profile.json').write_text(json.dumps({'fog_density':.18,'snow_normal':texture_path,'snow_normal_strength':.2,'highlight_gain':[1.12,1.03,.86,1],'midtone_gamma':1.06,'render_path':'UE native main viewport HighResScreenshot, DX12 SM6, Lumen, no external grading'},indent=2))
