# 天南阁 · Unreal Engine 5.8

从 [TianNanGe Unity 源工程](https://github.com/Aether-Verilys/TianNanGe) 迁移的 UE 场景原型，包含已经导入的场景、网格、材质、骨架和动画资源，以及 Python 编辑器迁移、光照和桥体重建工具。

当前同步的 Unity 源版本为 `fdf5e672e4081c53729675a72b944f8cde8f5c28`。本工程实际使用 **Unreal Engine 5.8.3**，Windows、DirectX 12、Shader Model 6、Lumen。

![当前 UE 实际渲染](Captures/ReferenceLook/Bridge_Reference_Rebuilt_4K.png)

上图为早期 ReferenceLook 桥体验证图；当前风雪云海效果以仓库默认启动的 `TianNanGe_EasySnow` 关卡为准。

## 获取和打开

需要先安装 [Git LFS](https://git-lfs.com/)。UE 资产、关卡和大型三维文件通过 LFS 保存；仅下载 GitHub 源码 ZIP 无法可靠取得这些资产。

```powershell
git lfs install
git clone https://github.com/Aether-Verilys/TianNanGe-UE.git
cd TianNanGe-UE
git lfs pull
```

用 UE 5.8.3 打开根目录的 `TianNanGe.uproject`，等待首次着色器和距离场构建。默认打开当前风雪云海场景 `/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow`，其中保存了天空、积雪、风雪、云海控制器和相机参数。选中主相机并 Pilot 查看构图；使用 `Lit` 显示完整材质，`Lighting Only` 显示光照白模。

工程同时保留 `/Game/TianNanGe/Maps/TianNanGe_ReferenceLook` 和首次迁移的 `/Game/TianNanGe/Maps/TianNanGe_Main`。完成 `git lfs pull` 后，当前场景及其依赖可直接打开，无需安装 Unity、Blender 或重新运行导入脚本。

## 当前内容

- 最新源场景的 388 个网格对象、29 份共享网格和 21 份源材质，包含八栋建筑和雪山实例。
- UE 原生材质、环境光、方向光、固定曝光、高度雾及后处理；保留当前手调结果。
- 重建的前景雪桥：稀疏立柱、非对称栏杆、雪团、细绳、冰挂和弯曲桥面。后段加深下沉与右弯，远端回升接平台。
- 人物与龙的骨架及循环动画：人物使用 8 秒呼吸与强风衣裙动画，龙使用呼吸动画，并配置金色眼光及拖尾资源。
- 人物与龙的独立补光、暖色轮廓光，以及调整后的曝光、泛光、镜头光晕和雾；新增灯光位于 `Lighting/Reference Look`。

新桥位于 Outliner 的 `Reference/Bridge`，资产在 `/Game/TianNanGe/BridgeReference`。2026-10-27 已从当前关卡清除 309 个停用旧桥白盒及雪细节 Actor，以及 14 个已被写实山体替换的旧山体 Actor。仍被历史关卡和保留几何引用的共享网格资产保留。清理前的关卡和桥体网格备份位于 `Backups/SceneCleanupNanite_20261027`。

2026-10-27 检查的 34 份可渲染静态网格、134 个组件均已启用 Nanite。桥体保留全部源三角形、100% 回退网格，并使用 `Position Precision=8`（步长 1/256 cm）；雪栏、雪团和冰挂采用 `Preserve Area`，避免细小结构被粗化。半透明天空球和编辑器摄像机图标保留原渲染方式。历史清理与 Nanite 记录保存在本地 `SourceAssets/SceneCleanup_20261027/`。

## 工具与复现

`Tools/` 内主要为 UE 编辑器 Python，`TianNanGeExport.cs` 为 Unity 导出入口。项目启用了 `PythonScriptPlugin`、`EditorScriptingUtilities`、`ModelContextProtocol` 和 `EditorToolset`；后两项需要本机提供对应插件。`Tools/DragonTrailBuilder` 保留 Niagara 拖尾资源生成器源码，打开已生成资源无需运行生成器。

`SourceAssets/`、测试、探测、验证脚本及诊断截图由 `.gitignore` 排除，仅保留在本地；仓库提交 UE 中已导入的资产和保存的场景。部分制作脚本需要本地源文件或报告，不能在全新检出中直接运行。第三方许可保留在 `ThirdPartyNotices/`。

当前场景及 `/Game/TianNanGe/EasySnowIntegration` 自定义资产已纳入 Git LFS，并同步了它们实际引用的 EasySnow 风雪、表面积雪和 Chaotic Skies II 天空依赖；资源来源见 [场景资源说明](ThirdPartyNotices/SceneDependencies.md)。天空保留 `SkyRotationDegrees` 旋转参数，Lumen 缓存曝光修复也随配置同步。具体调节入口见 [EasySnow 接入说明](EasySnow接入说明.md)。历史调试和重建脚本不能按文件名顺序批量运行，日常打开保存的关卡即可。

体积云使用原生 HeterogeneousVolume 连续云海，通过场景中的 `BP_CloudSeaController` 分组参数调整高度、密度、形态、流动、避让和颜色，并写入 `MI_CloudSea_Layer` 派生的动态实例，见 [云海实现](云海实现.md)。已同步控制器、密度倍率上限20、确定性采样与分层修正，以及云表面出现云下模型硬轮廓的雾光合成修正。旧云团 Actor、材质和生成脚本已清理，共用的 128³ 主形状和 32³ 侵蚀噪声保留。噪声采用 MIT 许可，来源见 [CloudNoise](ThirdPartyNotices/CloudNoise.md)。场景依赖清单和资产 SHA256 位于 `SourceAssets/SceneDependencies/TianNanGe_EasySnow.json`。

当前桥体的 OBJ 与生成清单保存在 `Transfer_BridgeReference/`。使用带 NumPy 的普通 Python 可重新生成：

```powershell
python -m pip install -r Tools/requirements.txt
python Tools/build_reference_bridge.py
python Tools/curve_bridge_rear.py --refresh-base
```

在 UE 的 Python 控制台中执行下面的导入入口。它只替换 `Reference/Bridge` 的网格对象、隐藏旧桥，并保存当前关卡；先备份需要保留的手调几何。

```python
import unreal, runpy
from pathlib import Path
root = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
runpy.run_path(str(root / "Tools/import_reference_bridge.py"), run_name="__main__")
runpy.run_path(str(root / "Tools/finalize_bridge_connection.py"), run_name="__main__")
```

全场景迁移入口为 `Tools/build_reference.py`，首次旧版迁移入口为 `Tools/RunMigration.ps1`。这类重建会替换场景或重设光照，不能用于保留当前手调结果的日常打开操作。完整重导还需要 Unity 源工程及重新导出的 OBJ；本仓库仅保留两次 Unity 导出的 `scene.json`，排除体积较大的重复中间网格、Unity 工作副本和缓存。历史导出、HDRI、骨架脚本中的外部 Unity/Blender/引擎路径需按本机调整；`import_revision.py` 支持 `TIANNANGE_SOURCE` 指定 Unity 工程路径。

## 验证与限制

`bridge-validation-reloaded.json` 是早期桥体重建后独立 UE 进程重新加载关卡的历史验证结果，其中的旧桥隐藏状态已由上述清理取代。当前清理与 Nanite 验证见 `SourceAssets/SceneCleanup_20261027/verification.json`，检查删除清单、保留对象的变换/可见性/材质、全部场景几何的 Nanite 设置及桥体回退顶点数。截图来自 UE 原生渲染。

这是带人物与龙循环动画的场景原型，人物持剑包含在已导入骨骼资源中；尚未完成可操控 UE Character、移动控制、AnimBP、完整碰撞及打包验收。构图和桥体经过调整，但没有达到原画像素级一致。

更多历史记录见 [迁移说明](迁移说明.md)、[原画光影对齐](原画光影对齐.md) 和 [桥体重建记录](桥体重建记录.md)。这些记录包含当时的本机路径、临时日志及备份位置，其中部分中间文件未纳入本仓库；以当前 README 的打开方式和提交的资产为准。

## 资产来源

- 模型与参考图来自上述 Unity 源仓库。保留各原资产的权利归属，本仓库没有为整个工程另行添加统一许可证。
- MAXDESIGN-3D 的 Chinese dragon 及适配内容：见 [署名、CC BY 4.0 和修改说明](ThirdPartyNotices/MAXDESIGNChineseDragon.md)。
- Poly Haven Kloofendal 天空环境：见 [来源说明](ThirdPartyNotices/PolyHavenKloofendal.md)。
- 本次生成的桥体作者标记为 `Pleasant233`；该标记不授予其他原画或模型的使用权。

云海场景调参：选中 `Cloud Sea Controls - TianNanGe`，在细节面板的 `Cloud Sea` 分类直接调整。外部蓝图修改该控制器的公开变量后调用 `Apply Cloud Parameters`；详情见 [云海实现](云海实现.md)。
