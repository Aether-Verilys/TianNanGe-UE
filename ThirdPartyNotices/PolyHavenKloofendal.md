# Kloofendal 天空环境

本工程沿用 Unity 源工程的 Kloofendal 38d Partly Cloudy Pure Sky 环境图，来源为 [Poly Haven](https://polyhaven.com/a/kloofendal_38d_partly_cloudy_puresky)。源工程将其标记为 CC0，作者为 Greg Zaal，天空编辑为 Jarod Guest。

UE 迁移进行了线性 EXR → Radiance HDR 转换，并重建为 `/Game/TianNanGe/Lighting/T_Kloofendal_Cube`。图像转换未应用显示色调映射；环境光强度、旋转及背景材质在 UE 中调整。

本说明只针对该环境图和本次适配，不把该许可扩展到其他模型、原画或工程内容。
