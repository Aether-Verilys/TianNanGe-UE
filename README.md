# 天南阁 · Unreal Engine 5.8

从 [TianNanGe Unity 源工程](https://github.com/Aether-Verilys/TianNanGe) 迁移的 UE 场景原型，包含已经导入的场景、网格、材质、骨架资源，以及 Python 编辑器迁移、光照、桥体重建和验证工具。

当前同步的 Unity 源版本为 `fdf5e672e4081c53729675a72b944f8cde8f5c28`。本工程实际使用 **Unreal Engine 5.8.3**，Windows、DirectX 12、Shader Model 6、Lumen。

![当前 UE 实际渲染](Captures/ReferenceLook/Bridge_Reference_Rebuilt_4K.png)

## 获取和打开

需要先安装 [Git LFS](https://git-lfs.com/)。UE 资产、关卡和大型三维文件通过 LFS 保存；仅下载 GitHub 源码 ZIP 无法可靠取得这些资产。

```powershell
git lfs install
git clone https://github.com/Aether-Verilys/TianNanGe-UE.git
cd TianNanGe-UE
git lfs pull
```

用 UE 5.8.3 打开根目录的 `TianNanGe.uproject`，等待首次着色器和距离场构建。默认打开 `/Game/TianNanGe/Maps/TianNanGe_ReferenceLook`。选中 `Main Camera (reference look)` 并 Pilot 查看参考构图；使用 `Lit` 显示完整材质，`Lighting Only` 显示光照白模。

工程同时保留首次迁移的 `/Game/TianNanGe/Maps/TianNanGe_Main`。已有 UE 资产可以直接打开，无需安装 Unity、Blender 或重新运行导入脚本。

## 当前内容

- 最新源场景的 388 个网格对象、29 份共享网格和 21 份源材质，包含八栋建筑和雪山实例。
- UE 原生材质、环境光、方向光、固定曝光、高度雾及后处理；保留当前手调结果。
- 重建的前景雪桥：稀疏立柱、非对称栏杆、雪团、细绳、冰挂和弯曲桥面。后段加深下沉与右弯，远端回升接平台。
- 原始人物、龙的骨架资源；场景中的展示对象仍采用烘焙静态姿态。

新桥位于 Outliner 的 `Reference/Bridge`，资产在 `/Game/TianNanGe/BridgeReference`。旧桥的 309 个白盒及雪细节 Actor 保留但关闭组件可见性与游戏可见性。桥体网格使用完整普通静态网格精度，避免本次 UE 5.8.3 Nanite/回退构建吞掉小雪团和细冰挂；其他资产的 Nanite 设置保留。

## 工具与复现

`Tools/` 内主要为 UE 编辑器 Python，`TianNanGeExport.cs` 为 Unity 导出入口。项目启用了引擎内置的 `PythonScriptPlugin` 和 `EditorScriptingUtilities`，没有额外 C++ 模块。

本分支还同步了本机 EasySnow 风雪与表面积雪、Chaotic Skies II 天空替换及 `SkyRotationDegrees` 旋转参数的集成脚本，以及 Lumen 缓存曝光范围修复。具体配置、操作入口和验证记录见 [EasySnow 接入说明](EasySnow接入说明.md)。用户提供的商业资源包及依赖它们的 `/Game/TianNanGe/EasySnowIntegration` 试验关卡没有上传；克隆仓库后默认仍打开上文的 ReferenceLook 关卡，不会直接获得本机最新风雪场景。使用可选工具前，需要自行准备相应资源和本地试验关卡；历史调试脚本不能按文件名顺序批量运行。

体积云使用原生 HeterogeneousVolume 连续云海，通过场景中的 `BP_CloudSeaController` 分组参数调整高度、密度、形态、流动、避让和颜色，并写入 `MI_CloudSea_Layer` 派生的动态实例，见 [云海实现](云海实现.md)。本轮同步控制器、密度倍率上限20、确定性采样与分层修正，以及云表面出现云下模型硬轮廓的雾光合成修正。旧云团 Actor、材质和生成脚本已清理，共用的 128³ 主形状和 32³ 侵蚀噪声保留。噪声采用 MIT 许可，来源见 [CloudNoise](ThirdPartyNotices/CloudNoise.md)。云海所在的本地试验关卡仍不随仓库分发。

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

`bridge-validation-reloaded.json` 是独立 UE 命令行进程重新加载已保存关卡后的验证结果，检查七个新桥 Actor、309 个旧桥 Actor 的隐藏状态，以及灯光/相机参数保留。最终截图来自 UE 原生渲染。

这是静态场景迁移原型，尚未完成 UE Character、移动控制、AnimBP、动态骨骼挂剑、完整碰撞及打包验收。构图和桥体经过调整，但没有达到原画像素级一致。

更多历史记录见 [迁移说明](迁移说明.md)、[原画光影对齐](原画光影对齐.md) 和 [桥体重建记录](桥体重建记录.md)。这些记录包含当时的本机路径、临时日志及备份位置，其中部分中间文件未纳入本仓库；以当前 README 的打开方式和提交的资产为准。

## 资产来源

- 模型与参考图来自上述 Unity 源仓库。保留各原资产的权利归属，本仓库没有为整个工程另行添加统一许可证。
- MAXDESIGN-3D 的 Chinese dragon 及适配内容：见 [署名、CC BY 4.0 和修改说明](ThirdPartyNotices/MAXDESIGNChineseDragon.md)。
- Poly Haven Kloofendal 天空环境：见 [来源说明](ThirdPartyNotices/PolyHavenKloofendal.md)。
- 本次生成的桥体作者标记为 `Pleasant233`；该标记不授予其他原画或模型的使用权。

云海场景调参：选中 `Cloud Sea Controls - TianNanGe`，在细节面板的 `Cloud Sea` 分类直接调整。外部蓝图修改该控制器的公开变量后调用 `Apply Cloud Parameters`；详情见 [云海实现](云海实现.md)。
