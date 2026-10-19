import bpy
image=bpy.data.images.load('D:/Dev/TianNanGe/Project_TianNanGe/Assets/TianNanGe/Lighting/HDRI/kloofendal_38d_partly_cloudy_puresky_4k.exr')
print('Loaded EXR',image.size[:],image.channels,image.has_data,image.pixels[0])
image.file_format='HDR'
image.filepath_raw='D:/UnrealProject/TianNanGe_UE58/Transfer/kloofendal_4k.hdr'
image.save()
print('TIANNANGE_HDRI_CONVERTED',tuple(image.size))
