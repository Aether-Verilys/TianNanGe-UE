# EasySnow 场景

当前试验关卡：`/Game/TianNanGe/EasySnowIntegration/Maps/TianNanGe_EasySnow`。
原来的 `TianNanGe_ReferenceLook` 和 `TianNanGe_Main` 关卡未改，文件 SHA256 已验证与接入前相同。

用户提供的 UE 5.4 EasySnow 内容已在本机 UE 5.8.3 加载、运行和渲染验证。原始资源仍保存在 E: 下载目录；工程里的 `/Game/EasySnow` 保留原始引用路径。来源为 William Faucher 的 [EasySnow](https://www.fab.com/listings/4fda5b2e-c44d-4df5-b7e2-afb7f2d6ed35?lang=en)。2026-10-26 起，当前场景、自定义集成资产及它们实际引用的资源依赖纳入 Git LFS，默认启动地图也已切换至此场景。具体范围见 [场景资源说明](ThirdPartyNotices/SceneDependencies.md)。

## 当前配置：细密飘雪、表面积雪与小幅几何位移，关闭碰撞

| 场景对象或材质 | 当前作用 |
| --- | --- |
| `EasySnow - TianNanGe Light Flurries` | 随相机移动的细密雪花，60000/s；近景尺寸 0.10–0.28 cm；风向 125°，风强 5.5；湍流及相机淡出 |
| `EasySnow - Courtyard Distant Flurries` | 庭院及建筑之间的远景雪幕，32000/s；近景尺寸 0.10–0.26 cm、远景尺寸倍率 0.68；固定区域 |
| `EasySnow - Bridge Ground Spindrift` | 桥面附近的低层吹雪，漂移粒子 18/s，不透明度 0.10；关闭此层普通雪花生成 |
| 雪花碰撞 | 按用户要求，三层全部关闭；Niagara 的 `User.collision` 同步关闭 |
| 新增表面积雪 | 已在屋顶、木结构、桥面、桥栏杆和岩石的环境材质中接入 EasySnow；覆盖量 0.28，以朝上的表面为主 |
| 几何积雪位移 | 屋顶、建筑和岩石共 18 个物体已启用 Nanite 位移；按实例缩放补偿，世界位移边界上限 0.6 cm，主天气位移倍率 0.5 |
| 迎风堆积、雪面闪烁 | 继续关闭；前景桥不启用 Nanite 位移，保留其独立雪层、雪团与冰挂网格 |
| `EasySnow Mask - Hero Footing` | 新材质启用原生 Custom Snow Masking，使用保留的脚下排除遮罩 |

只有主天气对象开启 `Set World Snow Material Settings`；`snowAmount` 当前为 0.28，`Transition Sharpness` 为 3.5，`breakupIntensity` 为 0.55，`breakupTextureTiling` 为 1.5。位移倍率为 0.5，迎风覆盖和闪烁参数为零，其余两层关闭全局参数写入。原模型的雪层、桥上雪团和冰挂继续保留。风雪由 EasySnow 的 Niagara 系统实际运行，动态预览不是图像合成。

新增积雪属于材质表面覆盖，不是雪花逐粒碰撞后形成的永久雪堆，也不会随运行时间自行增厚。人物、龙、剑和天空不追加积雪。新建的 12 组父材质及实例位于 `/Game/TianNanGe/EasySnowIntegration/SurfaceSnow/Materials`，保留源材质的输入和细节，独立于之前带位移的试验材质。初次绑定 176 个环境物体；用户同时编辑删除的物体不恢复，验证只检查现场仍存在的绑定。

其中 10 组建筑及岩石材质已复制到 `SurfaceSnow/DisplacedMaterials` 并接通完整 Material Attributes 的 Displacement 输出；这是当前的几何起伏版本。入口 `Tools/enable_surface_snow_geometry.py`，记录 `Saved/EasySnow/surface-geometry.json`。木结构仍使用无位移覆盖材质，桥的几何结构不改。纯覆盖版本的历史验证 `surface-verified.json` 不代表当前位移开关状态。

桥两侧新增的原创云海及三维噪声、原生体积光照见 [云海实现](云海实现.md)。没有使用商店 VolumeCloud 包。

前景桥继续使用完整的普通静态网格，未启用 Nanite，保留细雪团与冰挂。人物、龙和剑没有追加积雪覆盖；目前它们仍为静态姿态，EasySnow 的风不会自动驱动衣服或骨骼。

## 光照与画面对齐

直射光方向已恢复并验证为接入前值：Pitch **−6°**、Yaw **107°**、Roll **−20.69019°**。`tune_easysnow_features.py` 已移除修改灯光方向的代码。

试验关卡上一轮保留的其他光照调整是直射光强度 65000 lux、线性色彩 `(1, 0.84, 0.66)`、光源角度 2.2°，SkyLight 强度 4000，曝光偏移 −12.4；这些仅存在于试验关卡。本次天气调整没有改变灯光方向、强度、颜色和曝光，已逐项读回核对。目前尚未达到与原画像素级一致。

## 验证与继续调整

- 当前验证记录：`Saved/EasySnow/surface-verified.json`，包括灯光、雾、相机及天空参数保留，三层 Niagara 激活且碰撞关闭，新增积雪材质不启用细分和位移，原关卡哈希不变。
- 当前配置脚本：`Tools/enable_surface_snow.py`；绑定与参数记录为 `Saved/EasySnow/surface-snow.json`。`Tools/configure_fine_snow.py` 可恢复纯天气状态，已兼容新增材质；运行它会关闭本轮积雪。
- 前后原生渲染（各 12 帧，1280×620）：`Captures/SurfaceSnow_Before/` 与 `Captures/SurfaceSnow_After/`；使用相同主相机，屋瓦与木结构的覆盖变化可见。
- 之前纯飘雪版本的 3 秒预览：`Captures/EasySnowFineDenseFinal_Preview.mp4`；它不包含本轮新增的表面积雪。
- 更早的积雪位移试验材质保留备用，本轮不使用。`Saved/EasySnow/fine-snow-material-restoration.json` 记录了当时关闭的绑定。
- 调整表面积雪量：选择 `EasySnow - TianNanGe Light Flurries`，修改 `snowAmount`；设为 0 可关闭本轮覆盖，不影响原模型自带的雪层。
- 可分别调整主天气的 `spawnRate -`、`windStrength -`，以及低层吹雪的 `DriftingSnowAmount -`、`driftOpacity -`。保持主光方向不变。

## 当前天空：Chaotic Skies II 第 04 款

已使用用户提供的 `Chaotic_Skies_II/Textures/Skies/T_chaotic_sky_II_04` 替换原背景，保留冷灰云层与缓慢流动。资源按原 `/Game/Chaotic_Skies_II` 路径放入本机工程，只复制天空及其流图、材质和网格依赖，没有导入演示地图或地形。

- 天空对象：`Lookdev Chaotic winter sky 04`；已恢复编辑器可见性。
- 可调实例：`/Game/TianNanGe/EasySnowIntegration/Skies/MI_Chaotic_WinterSky_04`。
- 在该实例的“天空角度”分组中勾选 `SkyRotationDegrees`，即可水平旋转天空显示角度；单位为度，滑条范围 0–360，负角度和超过 360° 的值也可循环。0° 保留当前构图。它同时偏移天空与流向图的 U 坐标，不改变天空球 Transform、直射光方向及其他材质参数。
- 安装初始参数：Brightness 5000、Contrast 0.95、Tint `(0.76, 0.88, 1)`、Speed 0.004、NoiseStrength 0.04，天空自身 Yaw −75°。后续手调以本机实例读数为准，旋转脚本保留已有外观参数；重新运行天空安装脚本会重设这些参数。
- 当前场景启用了体积雾，密度为 0.9。天空使用有深度测试的 Unlit 透明材质，关闭自身重复雾化，排序位于雪花之后的远背景；建筑和人物继续使用原有体积雾。试验过的雾截止距离已恢复为原值 0。
- 直射光方向、强度、颜色、SkyLight Cubemap、曝光及风雪参数均保留。天空自身的旋转不改变直射光方向。
- 2026-10-26 天空边界修正：当前天空纹理的 U 保持 Wrap、V 改为 Mirror。天空球网格在赤道折返 V，原先纵向循环会将边缘采样送到图像另一端，出现水平横带；镜像纵向寻址保留流动与水平旋转。只修改纹理采样元数据，导出前后原图像素哈希一致；用户当前角度、亮度、对比度、颜色及速度均保留。用户已在原视角确认横带消失。维护入口为 `Tools/fix_sky_horizon_sampling.py`，实时资源更新需先串行准备、完成后恢复普通渲染，不移动相机或接管桌面输入。
- 备份：`Backups/ChaoticSky_20261020/TianNanGe_EasySnow.umap`；安装记录：`Saved/ChaoticSkies/installed.json`。
- 新预览：`Captures/ChaoticWinterSky04_Clouds_Preview.mp4`；静帧：`Captures/ReferenceLook/Chaotic_Winter_Sky_04.png`。

代码和说明已合并到 `main`。当前试验关卡及依赖现已纳入同步，`Saved/`、`Backups/` 和临时渲染预览继续仅在本机保留；不需要运行历史安装脚本才能打开已保存场景。

## 脚本用途与前置数据

| 脚本 | 用途与注意事项 |
| --- | --- |
| `prepare_easysnow_map.py` | 独立 UE 进程中从 ReferenceLook 保存本地试验副本；不能用于覆盖已有手调关卡 |
| `integrate_easysnow.py` | 最初接入材质与主天气的历史入口，会重建主天气；其中碰撞和低密度设置不代表当前配置 |
| `configure_fine_snow.py` | 应用细密飘雪，恢复源材质并关闭新增积雪；依赖接入时生成的 `Saved/EasySnow/integration.json` |
| `enable_surface_snow.py` | 在已有三层天气上加入当前不带位移的表面积雪；不修改灯光和天空 |
| `install_chaotic_winter_sky.py` | 在本地试验关卡替换天空，需先安装相应天空资源；会重设天空初始外观参数 |
| `add_sky_rotation.py`、`set_sky_rotation.py` | 创建水平旋转参数、设置角度；后者可接收 `{"angle":90}` 命令参数 |
| `fix_cached_exposure.py`、`verify_exposure_startup.py` | 应用缓存预曝光并验证启动配置；持久值由 `Config/DefaultEngine.ini` 提供 |
| `inspect_surface_snow.py`、`verify_surface_snow.py` | 修改前记录场景；修改后用 `{"verify":true}` 记录，再核对差异；依赖本机前后快照及渲染完成记录 |
| `capture_easysnow_motion.py`、`encode_easysnow_preview.py` | UE 原生序列渲染及普通 Python 视频编码；编码依赖 `imageio-ffmpeg`，当前要求 72 帧 |

`probe_*`、其他 `inspect_*`、`strengthen_easysnow.py`、`tune_easysnow_features.py` 和位移脚本属于历史探测或中间试验，会依赖当时的本地报告，部分会修改天气、材质或光强。它们不是当前配置的批量重放入口。脚本输出位于被忽略的 `Saved/`；新环境运行前按需要创建 `Saved/EasySnow`、`Saved/ChaoticSkies` 和 `Saved/Exposure` 目录。普通 Python 使用的 `imageio-ffmpeg` 可安装到本机 Python，或本地 `Tools/Live/encoding` 目录。

## Lumen 缓存曝光范围

2026-10-21 修复了红色 `Cached lighting in Lumen ... is going to be clipped` 警告。场景手动曝光约 EV 12.4，UE 5.8.3 默认缓存预曝光 4 对应安全范围 [−8, 12]，当前曝光超过上限。按本机引擎 `PostProcessEyeAdaptation.cpp` 的实际定义，将 `r.EyeAdaptation.CachedLightingPreExposure=8` 写入 `Config/DefaultEngine.ini` 的 RendererSettings，并应用到当前编辑器，安全范围变为 [−4, 16]。相机曝光、灯光和天空材质未改。

运行检查：`Saved/Exposure/fixed.json`；独立启动检查：`Saved/Exposure/startup-verified.json`。该警告同时提到实时天空捕获，但当前 SkyLight 的实时捕获仍为关闭状态，触发项是共用缓存范围与当前曝光不匹配。
