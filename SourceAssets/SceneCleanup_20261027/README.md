# 场景清理与 Nanite

2026-10-27，处理关卡 `/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow`，在原有编辑器中执行并保存，没有修改其他工程。

## 清理结果

- 删除 309 个已停用旧桥白盒、积雪细节 Actor，以及 14 个被写实山体替换的隐藏旧山体 Actor，共 323 个。
- 场景 Actor 数量由 472 降为 149。
- 保留桥头石阶、连接件、建筑可行走结构、建筑承托薄板，以及用户调整和新增的写实山体实例。
- 此批涉及的 7 份项目共享网格仍被保留几何或历史关卡引用，未删除网格资产文件；没有强制移除引用。

精确删除清单、共享资产引用见 `cleanup.json`，处理前完整清单见 `audit-before.json`。

## Nanite

34 份场景几何静态网格、134 个组件已启用 Nanite，并检查组件未设置 `Disallow Nanite`。其中 27 份网格原本已经开启，本次新增开启 7 份桥体网格。

桥体保留全部源三角形、不预裁剪、100% 回退三角形、回退相对误差 0，位置精度设为 8。UE 5.8 的精度定义为步长 `2^(-PositionPrecision)` cm，因此该值对应 1/256 cm。雪栏、雪团和冰挂使用 `Preserve Area`；所有桥体网格的回退顶点数与开启前相同。重导入口 `Tools/import_reference_bridge.py` 和精度修正入口 `Tools/fix_bridge_precision.py` 已同步这些设置。

例外：半透明天空球不适用 Nanite，保留现有材质与渲染方式；摄像机图标属于编辑器辅助网格，不修改引擎共享资产。体积云与 Niagara 粒子不属于本批静态几何组件。

## 验证与恢复

`verification.json` 验证删除清单、保留 Actor 的变换/可见性/材质、全部场景几何的 Nanite 和组件覆盖设置，以及桥体精度与回退顶点数。`nanite-progress.json` 保留逐网格处理记录。画面对比文件为 `Captures/RealisticMountains/cleanup-before.png` 和 `cleanup-after.png`，栏杆、积雪、冰挂仍可见；动态风雪会造成两帧之间的差异。

备份目录：`Backups/SceneCleanupNanite_20261027`，包含清理前的完整关卡和修改前的 7 份桥体网格。恢复整关卡可以恢复被删除的原 Actor；恢复网格资产前应关闭该工程编辑器，避免在文件被占用时覆盖。旧的 `restore_original_mountains.py` 只针对山体替换当时的可见性恢复；清理后需先恢复清理备份中的关卡，不能直接运行它。

这些检查不构成所有视距、所有平台或打包版本的性能验收。当前更改已保存到本地，未执行 Git 提交或推送。
