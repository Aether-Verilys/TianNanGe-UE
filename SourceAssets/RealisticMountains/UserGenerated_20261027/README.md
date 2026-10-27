# 用户生成写实山体：下载、导入与替换

2026-10-27，使用用户已生成的三件 Tripo H3.1 结果，本次没有创建新生成任务。

按网页列表顺序编号：01_Rocky（台阶岩体）、02_Peak（尖峰）、03_Cliff（横向岩壁）。源 GLB 和 PBR 贴图按 8k Current 设置导出，下载后通过 Tripo Orbit CPU CLI 检查。来源任务链接、字节数和 SHA256 见 manifest.json，结构报告见 inspection-01/02/03.json。

UE 资源目录：/Game/TianNanGe/RealisticMountains，各模型及其贴图、材质使用独立子目录，开启 Nanite。

当前关卡：/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow。

替换脚本按旧山体的世界包围范围匹配尺寸、中心和高度；新实例位于 Outliner 的 RealisticMountains。原山体保留并隐藏，不删除原网格资源。建筑承托薄板保留，相机、灯光和云海参数不做修改。

记录：scene-before.json、original-visibility.json、ue-import-01/02/03.json、replacement.json、validation.json。后两个文件仅在替换和验证成功后生成。

回退：在已加载当前关卡的 UE Python 环境运行 Tools/restore_original_mountains.py。它只恢复本批隐藏的原山体，并移除本批带专用标记的替换 Actor。整关卡磁盘备份：Backups/RealisticMountains_20261027/TianNanGe_EasySnow.umap。

结构检查不保证视觉完美或网格封闭。GLB 中的积雪颜色来自生成贴图，后续仍可在 UE 调整材质与独立雪覆盖。此目录记录来源，不另行授予生成服务或其他资产的使用权。

已完成：11 个新实例、14 个原组件 Actor 隐藏；所有原 Actor 变换和相机 FOV 验证一致。实际贴图尺寸为 Base Color 8192²、Normal 与打包 PBR 4096²。原有编辑器中未保存的当前状态已先保存并备份到 TianNanGe_EasySnow_live.umap。

后续清理说明：14 个隐藏旧山体 Actor 已在 2026-10-27 场景清理中删除，原共享网格资产保留。旧可见性恢复脚本不再能直接使用；需要先恢复 Backups/SceneCleanupNanite_20261027 中的整关卡备份。当前清理和 Nanite 验证见 SourceAssets/SceneCleanup_20261027。
