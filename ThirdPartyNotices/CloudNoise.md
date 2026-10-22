# Cloud volume noise

The imported cloud-shape and erosion data come from Tyler Dodds' **VolumetricCloudsTutorial**, licensed under MIT, copyright (c) 2019 Tyler Dodds.

- Repository: https://github.com/TylerDodds/VolumetricCloudsTutorial
- Original files: `Assets/VolumetricCloudsTutorial/CloudDensity/NoiseTextures/noiseShape.tga` and `noiseErosion.tga`.
- Source documentation: https://github.com/TylerDodds/VolumetricCloudsTutorial/blob/master/Assets/VolumetricCloudsTutorial/CloudDensity/NoiseTextures/NoiseTextures.md
- Full license: [LICENSE-TylerDodds.txt](../SourceAssets/CloudNoise/LICENSE-TylerDodds.txt).
- Original downloads, source URLs and SHA256 values: `SourceAssets/CloudNoise/sources.json`.

Changes: the original horizontal slice strips were rearranged into two-dimensional slice grids for UE import. They were imported as linear, wrapping VolumeTexture assets of **128×128×128 RGBA** (Perlin–Worley shape and packed Worley octaves) and **32×32×32 RGBA** (Worley erosion). The voxel channel values were preserved. `Tools/fetch_cloud_noise.py` and `Tools/import_cloud_noise.py` reproduce this conversion.

The upstream documentation credits Sébastien Hillaire's TileableVolumeNoise work for the generation method. That generator is a technical reference here; its code has not been copied into this project.

Additional research candidate, not imported: Christoph Peters' CC0 blue-noise textures, distributed at https://github.com/Calinou/free-blue-noise-textures. Blue noise is appropriate for sampling jitter, rather than the cloud density itself.
