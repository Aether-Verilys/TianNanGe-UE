# 当前风雪云海场景资源

2026-10-26，按用户要求，将 `/Game/TianNanGe/EasySnowIntegration` 当前关卡和自定义资产纳入 Git LFS，并包含它们实际引用的第三方资源。资源原始目录路径保留，避免断开蓝图、Niagara、材质函数、纹理和网格引用。

- **EasySnow v1.0.0 UE 5.4**：用户提供；作者 William Faucher。[资源页面](https://www.fab.com/listings/4fda5b2e-c44d-4df5-b7e2-afb7f2d6ed35?lang=en)。场景使用其天气/遮罩蓝图、Niagara、积雪材质函数、粒子网格、纹理及系统资产。
- **Matte Painting Skybox Pack: Chaotic Skies II**：用户提供，原始本机目录 `Chaotic_Skies_II`。场景使用天空球网格、天空纹理及流向图；自定义天空材质和旋转参数位于工程集成目录。
- 原 Unity 模型、参考图、龙模型、Poly Haven 环境和原创云海噪声的来源仍见 README 及本目录对应说明。

此同步不改变原素材的版权归属或许可，不为这些素材新增开源授权。仓库仍不采用覆盖所有资源的统一许可证。

`SourceAssets/SceneDependencies/TianNanGe_EasySnow.json` 记录保存场景和全部自定义集成资产的递归项目依赖、文件大小与 SHA256。引擎自带资源和插件资源单独列出，由 UE 5.8.3 提供。第三方包中未被引用的演示/示例内容不纳入同步。

获取仓库后运行 `git lfs pull`，用 UE 5.8.3 打开 `TianNanGe.uproject`，默认进入当前场景。验证工具为 `Tools/verify_scene_dependencies.py`；它加载已保存地图并读取资产注册表，不保存场景或改变美术参数。依赖加载验证不等同于 GPU 渲染或打包验收。
