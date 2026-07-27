# hyperframes 合成规范

> Step 8 使用。HyperFrames 从 HTML 渲染视频：一个组合就是一个 HTML 文件，用 `data-*` 属性声明时序。

## 为什么用 hyperframes 而不是 ffmpeg 拼接

| 能力 | ffmpeg 静帧拼接 | hyperframes |
|------|----------------|-------------|
| 镜头运动（Ken Burns 推拉） | 需手写复杂 filter | HTML/CSS 声明式 |
| 转场 | 需 xfade 逐段拼 | `transition_in` 属性 |
| 字幕 | 本机 ffmpeg 无 libass，只能烧进像素 | 独立图层，源文件可改 |
| 改一句字幕 | 重烧全部帧 + 重编码 | 改 HTML 重渲染 |
| 字幕与动效同源 | 分离，容易错位 | 同一时间轴 |

**本项目本机 ffmpeg 缺 libass/libfreetype**（`ffmpeg -filters` 里没有 `subtitles`/`drawtext`），这是必须用 hyperframes 的直接原因。

## 入口与安装

```bash
npx hyperframes skills update general-video
```

路由：本项目是**带旁白的图书带货叙事视频**，走 `/general-video`（`/faceless-explainer` 的甜点是 30-90s 且偏抽象图形，本项目有既定插画素材和固定片头片尾，用 general-video 更合适）。

按 `hyperframes/SKILL.md` § 1 的状态表，项目已有 `STORYBOARD.md` 时从项目文件恢复，不重跑意图访谈。

## 项目结构

```
episodes/ep00X-书名/
├── 02-script/
│   ├── SCRIPT.md            # 锁定旁白（Step 3）
│   ├── STORYBOARD.md        # 分镜含动效字段（Step 6）
│   └── shot-timing.json     # 真实时间轴（Step 5）
├── 03-assets/
│   ├── scenes/shot_*.png    # 场景图（Step 7）
│   └── audio/
│       ├── voiceover.wav    # 旁白（Step 4）
│       └── bgm.mp3          # 背景音乐
├── compositions/
│   ├── main.html            # 主组合
│   └── frames/
│       ├── 01-hook.html     # 逐帧子组合
│       └── ...
└── 04-video/
    ├── output.mp4           # 成片
    └── subtitle.srt         # 独立字幕文件
```

## 字幕图层规范（不烧录）

字幕写在每帧 HTML 的独立 `<div>` 图层里，与背景图分离：

```html
<div class="subtitle-layer" data-hf-track="subtitle">
  <p data-hf-in="0" data-hf-out="2.4">你总是先道歉，对吧？</p>
  <p data-hf-in="2.4" data-hf-out="4.878">哪怕错的，根本不是你。</p>
</div>
```

样式按 `references/subtitle-style.md`：金黄 #FFD700、黑色描边 4px、底部留白 210px、每行 ≤14 字。

**同时导出独立 SRT**：`04-video/subtitle.srt`，时间码与 HTML 图层一致，供平台二次编辑或上传软字幕。

## 音轨规范

| 轨道 | 音量 | 说明 |
|------|------|------|
| 旁白 | 1.0 | 基准 |
| BGM | 0.15 | 不盖人声 |
| 片头片尾 | 静音 | **必须 `-an` 去除原视频背景音** |

## 片头片尾拼接

固定素材 `assets/brand/intro.mp4`（1.5s）+ `assets/brand/outro.mp4`（3.04s），已去音轨。

切割注意事项（Step 0 的教训）：
- 参考视频的品牌页可能**自带动画**（如 logo 飞向左上角），直接截取会把动画带进来；循环拉长会导致动画重复播放。
- 正确做法：用像素质心分析定位**静止窗口**，取单帧定格拉长。
- 必须验证：多个时间点抽帧，确认 logo 质心坐标恒定。

## 渲染与校验

```bash
npx hyperframes render          # 渲染成片
npx hyperframes check           # 校验组合
python3 scripts/validate-spec.py 04-video/output.mp4
```

规格红线：1080×1920、30fps CFR、H.264 High@4.0 + AAC 48kHz、≤180s。

## 动效层：必须 seek-safe

HyperFrames 逐帧 seek 渲染，**没有"播放"这回事**。任何依赖"经过前一帧才到达本帧"的状态都会失效——CSS 无限循环动画渲出来是卡住的静帧。

### 硬性规则

```js
// ✅ 正确：注册到 window.__timelines 的 paused 时间轴
const tl = gsap.timeline({ paused: true });
tl.fromTo("#dust-1", { y: 0, opacity: 0.3 },
          { y: -40, opacity: 0.6, duration: 3, ease: "none" }, startTime);
window.__timelines["main"] = tl;
```

| 禁止 | 原因 | 替代 |
|------|------|------|
| `repeat: -1` | 无限循环无法推断时长 | `Math.max(0, Math.floor(dur / cycle) - 1)`，用 `floor` 不用 `ceil` |
| `Math.random()` | 每次渲染结果不同 | 构建时用固定种子算好，写死进 HTML |
| `Date.now()` / `performance.now()` | 依赖真实时钟 | 用时间轴位置参数 |
| `setTimeout` / `requestAnimationFrame` | 渲染器不走时间流 | 改写成 tween |
| CSS `animation: ... infinite` | 无法 seek | 改用 GSAP tween |
| 动 `display` / `visibility` | 不可插值 | 用 `opacity`，或 `autoAlpha` |
| 对 `.clip` 元素做动画 | HyperFrames 拥有它的生命周期 | 动 clip **内部**的包裹层 |

可动的属性：`opacity`、`x`、`y`、`scale`、`rotation`、`color`、`backgroundColor`、`borderRadius`、transforms。

### 常用动效配方

| 效果 | 做法 |
|------|------|
| 光束呼吸 | 光束层 `opacity` 0.6↔0.9，`yoyo: true`，有限 `repeat` |
| 尘埃浮动 | N 个小圆点，种子随机定位，各自 `y` 上飘 + `opacity` 渐隐，相位错开 |
| 热气升腾 | SVG path，`y` 上移 + `opacity` 0→0.5→0，三缕错开起始时间 |
| 纸张呼吸 | 整层 `scale` 1.0↔1.008，极缓，`ease: "sine.inOut"` |
| 光斑流动 | 模糊圆 `x`/`y` 沿直线缓移 |
| 影子起伏 | 多个影子层 `y` + `opacity` 微幅波动，各自相位不同 |
| 金句浮起 | `y: 20→0` + `opacity: 0→1`，`ease: "power2.out"`，0.6s |

**相位错开**是关键：多个元素同步动会显得机械，给每个元素不同的起始偏移。

**尘埃/光点参数**（太小看不见，太大会变成 UFO）：
- 尺寸 8-14px，不透明度峰值 0.55-0.85
- 用纯色 `background` + `box-shadow`，**不要用 `radial-gradient`**（大量 gradient 会触发黑帧缺陷）
- 位置用固定种子在构建时算好，写死进 HTML

## 金句层（两种样式，用途不同）

从书中摘句贴进画面。**中文不靠 AI 生成**——用 hyperframes 文字层渲染。

| 样式 | 用在哪 | 字体 | 颜色 | 背景 | 出现方式 |
|------|--------|------|------|------|----------|
| **ink**（墨色） | 书页、概念镜 | 宋体/楷体 | 深墨色 `#2e1f10` | **透明**（靠书页本身做底） | `opacity 0→1` + `scale 1.04→1` + `blur 3px→0`，2s，模拟墨水渗透纸面 |
| **note**（便签） | 实景镜 | 黑体 | 白色 `#fff` + 3px 黑描边 | **透明** | `opacity 0→1` + `y 16→0`，0.7s |

- 每镜最多 1 句
- 位置在画面中上部，与底部口播字幕分离
- 字号 ink 46px / note 40px，均小于口播字幕（48px），不抢主次
- **金句位置必须避开画面主体**（杯子、人脸、书脊），渲染后抽帧验证

## i2v + 书页金句的集成模式

当 i2v 视频用于"翻书"等揭示性动作时，金句不能浮在翻飞过程中，要在纸落定后才显影：

```
i2v 翻书视频（5-7s，末帧是翻开后的书页）
  → 视频 clip 播完，末帧定格
  → GSAP 金句在静止书页上做"墨水显影"（ink 样式）
```

- 视频末帧最好就是带简笔画/英文标题的书页图（用首尾帧模式 `frames2video` 生成）
- 金句的中文用 hyperframes 文字层叠上去，因为 i2v 写不了准确中文
- 不要试图在翻飞过程中显示文字——平面的文字层无法跟着翻动的纸页做透视变形

## i2v：即梦 dreamina

### 用量控制

```bash
dreamina user_credit              # 先看余额
```

- **每集 i2v 镜头不超过 2 个**，其余用 GSAP 动效
- 只给"动作本身就是内容"的镜头：书页翻开、门被推开、水面晃动
- **不要给人物面部特写**——模型容易把简笔画的脸渲染成写实的，风格崩

### 提示词：必须走 seedance-prompt-zh skill

**不要自己写。** 调用 `seedance-prompt-zh`（`~/.agents/skills/seedance2-skill-zh/SKILL.md`），它是即梦 Seedance 2.0 的官方提示词规范。

核心语法是 `@` 引用系统——每个素材都要说明用途：

| 用途 | 写法 |
|------|------|
| 首帧 | `@图片1 作为首帧` |
| 尾帧 | `@图片2 作为尾帧` |
| 人物形象 | `参考 @图片1 的人物形象` |
| 运镜 | `参考 @视频1 的运镜效果` |

结构公式：`[主体设定] + [场景] + [动作] + [运镜] + [分时段] + [风格氛围]`

10 秒以上要分时段写（`0–3秒 / 3–6秒 / …`），5 秒可省略。

### 命令

```bash
dreamina image2video \
  --image=<首帧.png> \
  --prompt="<seedance-prompt-zh 写好的提示词>" \
  --model_version=seedance2.0fast_vip \
  --duration=5 \
  --video_resolution=720p \
  --poll=180
```

模型可选：`seedance2.0fast_vip`（快，够用）、`seedance2.0_vip`（支持 1080p/4k，更贵）。
时长范围：seedance2.0 系列 4-15 秒。输出分辨率上限 720p，不要要求 1080p。

其他子命令：`text2video`、`frames2video`（首尾帧）、`multiframe2video`（多图故事）、`multimodal2video`（全能参考）。

### 时长不匹配的处理

口播 8 秒但视频只有 5 秒时：

- ✅ **视频播完定格最后一帧**，剩余时间叠 GSAP 轻微动效
- ❌ 不要慢放——动作会变得不自然，一眼看出来
- ❌ 不要循环播放——接缝处会跳

### 风格保持（拼贴风必写）

模型默认会"优化"画面，把纸质拼贴渲染成写实风。提示词里必须显式拦住：

```
严格保持 @图片1 的拼贴剪纸画风和纸张质感，
不要渲染成写实风格，不要磨平纸纹，不要加 3D 光影。
只让 <具体动作> 动起来，其余保持静止。固定镜头。
```

### 其他限制

- **不支持写实真人脸部素材**，系统会自动拦截
- 输入图片 ≤9 张、每张 <30MB；视频 ≤3 个、总时长 2–15s
- **生成结果自带 BGM/配乐/音效，集成前必须剥离**（`ffmpeg -i input.mp4 -c:v copy -an output.mp4`），否则会污染全片旁白
- 视频容器帧率可能虚标 60fps（实际 24fps 源），合成时以源帧率处理

## 金句层

从书中摘句贴进画面。**中文不靠 AI 生成**——AI 写中文常出错字、缺笔画，改用 hyperframes 文字层渲染，清晰可改还能做动画。

| 类型 | 用在哪 | 样式 |
|------|--------|------|
| **浮起** | 书页、概念镜 | 无底纹，直接浮在画面上，`y` 上飘 + 渐显 |
| **便签** | 实景镜 | 米色纸块 + washi tape + 轻微旋转（±2°），贴角落 |

- 每镜最多 1 句
- 位置在画面中上部，与底部字幕分离
- 字号约 40-46px，小于口播字幕，不抢主次

## 常见坑

| 坑 | 表现 | 解法 |
|----|------|------|
| concat 后帧率变 60 | `r_frame_rate=60/1` | 拼接后重编码，加 `-vf fps=30 -video_track_timescale 30000` |
| 音画不同步 | 画面比旁白慢/快 | 分镜 `duration` 必须来自 shot-timing.json，不能估算 |
| 配音前导静音被算进第一镜 | 全片字幕早于人声约 200ms | `realign-shots.py` 先用 `silencedetect` 定位人声真实起点，再按比例切分 |
| 换音色后全废 | 时长变化，字幕错位 | **TTS 必须在分镜之前定稿**（SKILL.md 的顺序铁律） |
| 素材分辨率不一 | 缩放后构图偏移 | 统一 center-crop 到 1080×1920，或生图时就固定尺寸 |
| 单镜超过 15 秒 | 观众划走 | 拆镜，或换画面（例如把长段观点改成书页金句轮换） |
| 动效渲染出来是静帧 | CSS 无限循环、`Math.random()` | 全部改写成 GSAP paused 时间轴上的 tween |
| heavy overlay 导致渲染全黑 | 40+ 个 `radial-gradient`/`filter:blur` 元素触发捕获层缺陷，渲出纯黑帧 | 尘埃等重复元素改用纯色 `background` + `box-shadow` 代替 `radial-gradient`；每镜只保留 1 个光晕层。渲染后抽样测亮度，<12 为黑帧 |
| `<video>` 嵌套在带 `data-start` 的 div 里 | 视频 FROZEN，渲染不动 | `<video>` 必须是 root 的直接子元素；动效层另放一个同级 clip |
| Ken Burns 放大导致 overflow 告警 | check 报 `container_overflow` | 这是预期行为，给 scene 容器加 `data-layout-allow-overflow` |
| 字幕压住画面主体 | 底部三分之一被占满 | 字号 48px，生图提示词里写明底部留白 |
| 金句被画面元素遮挡 | 金句落在杯子/人脸上 | 金句位置用 `top` 百分比精确避开主体；渲染后抽帧验证每条金句可读 |
| i2v 视频自带 BGM | 集成后 BGM 污染全片旁白 | 下载后立即 `ffmpeg -i input.mp4 -c:v copy -an output.mp4` 剥离 |
