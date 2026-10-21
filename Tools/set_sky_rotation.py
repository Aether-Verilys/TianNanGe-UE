"""Set only the sky material's horizontal rotation; used for visual checks."""
import unreal as u
command=globals().get('COMMAND',{});angle=float(command.get('angle',0.))
mi=u.load_asset('/Game/TianNanGe/EasySnowIntegration/Skies/MI_Chaotic_WinterSky_04');assert mi
u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi,'SkyRotationDegrees',angle)
assert abs(u.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(mi,'SkyRotationDegrees')-angle)<.0001
u.MaterialEditingLibrary.update_material_instance(mi)
assert u.get_editor_subsystem(u.EditorAssetSubsystem).save_loaded_asset(mi)
