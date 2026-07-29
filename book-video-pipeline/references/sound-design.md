# 声音设计

> 来源：参考 video-shotcraft `sound-design.md` 的方法论，按图书带货视频（TTS 旁白 + BGM + 可选 SFX）场景适配。
>
> 准则编号 S1–S3 见 `references/shot-structure.md` 审美规则清单。

## 方法

**顺序：画面结构基本锁定 → 先铺 BGM 定能量骨架 → 逐拍钉 SFX（如有）。**

声音是时间线级资产，排在画面锁定之后。任何改变镜头时长/顺序的修改，收尾动作必须包含"SFX 全表重对"（S3）。

## BGM

### 选型

图书带货视频的 BGM 和产品宣传片不同——**旁白是主角，BGM 是配角**。

| 维度 | 要求 |
|------|------|
| 风格 | 轻钢琴 / 氛围乐 / lo-fi，**无歌词、无强鼓点** |
| 情绪 | 安静、温暖、不抢旁白 |
| 音量 | **0.15**（远低于产品宣传片的 0.34，因为旁白是核心信息载体） |
| 淡入 | 1s |
| 淡出 | 2s（在视频结束前 2s 开始衰减） |
| 时长 | ≥ 视频总时长（≥120s），或可循环 |
| 许可 | 可商用、无需署名（pixabay 自有许可优先） |

### BGM 下载

pixabay 有 Cloudflare 挑战，必须用 `ego-browser` 浏览器下载（详见 SKILL.md Step 9b）。

搜索关键词推荐：`calm piano`、`ambient soft`、`lo-fi quiet`。

## SFX 词汇表（可选，按需启用）

SFX 不是必选项——如果 BGM + 旁白已经足够，可以不加 SFX。但在以下场景，SFX 能显著提升观感：

| 场景 | 推荐音效类型 | 用途 |
|------|-------------|------|
| **书页翻开**（i2v 翻书镜头） | `paper/`（翻页、纸张） | 配合翻书动作的拟音 |
| **金句出现** | `light/`（sparkle、光效） | 金句墨水显影时的余韵光效 |
| **场景转场** | `transition/`（whoosh、sweep） | 关键转场的运镜音 |
| **结尾品牌收尾** | `impact/`（落地重音） + `riser/`（铺垫上升） | 结尾能量峰值的 riser→impact 句式 |

### 音效选型纪律

| 规则 | 说明 |
|------|------|
| **按电影类型选，不按事件选** | SFX 词汇 = whoosh(运镜) / impact(落地) / riser(铺垫) / sparkle(光效) / paper(纸张) |
| **禁游戏音包音色** | 合成器 pluck/bloop、卡通弹跳、game-over 音阶——闭眼听像手机游戏的不用 |
| **禁的是音色不是动作** | 画面真有翻页/点击就该配拟音，那是真实物件的声音 |
| **拟音优先于装饰音** | 画面动作配该动作的真实声音，泛用 swoosh 盖不住有辨识度的动作 |

### 免费音效来源

| 来源 | 授权 | 适用 |
|------|------|------|
| [Mixkit](https://mixkit.co/) | 免费商用、免署名 | 电影系 SFX（whoosh/impact/riser/sparkle）+ 拟音 |
| [pixabay](https://pixabay.com/sound-effects/) | pixabay 自有许可 | 各类音效 |

> 下载时记录原始文件名/URL，批量下载后 metadata 常被抹掉。

## SFX 钉帧方法

### 声明式管理

SFX 用 `{ from, src, volume }[]` 声明式表集中管理，逐条注释对应的画面动作：

```js
const SFX = [
  { from: 1450, src: "paper-turn.mp3", volume: 0.4 },  // 翻书动作
  { from: 2010, src: "sparkle.mp3", volume: 0.3 },     // 金句显影
];
```

### 相对钉帧（硬规则）

钉帧一律**相对镜头起点**（`shot.start + offset`），不写裸绝对帧号。这样镜头内部节拍不变时，改前面镜头的时长只需分镜表更新一处，SFX 自动跟随。

### 音量分层

| 层 | 音量 | 说明 |
|----|------|------|
| BGM | 0.15 | 打底，不盖旁白 |
| 旁白 | 1.0 | 基准（最高优先级） |
| SFX | 0.2–0.5 | 常规区间，用响度表达"这一拍多重要" |

> 注意：`volume` 是乘法系数不是目标音量。新增音效入库时用 `ffmpeg -af volumedetect` 检查峰值，低于 -12dB 的素材需要预归一化或换素材。

### 连发音效防机枪感

同类音效连发时（如多个金句连续出现），用三招避免机械复读：
1. **双样本交替**：两个近似样本轮流
2. **音量阶梯递减**：如 0.40→0.37→0.34→0.31→0.28→0.25
3. **间隔加速**：连发间隔跟随动画曲线收缩

### riser→impact 句式（结尾）

结尾能量峰值的三拍句式：

```
riser（铺垫上升） → 约 35 帧后 impact（重音落地） → 25 帧后 sparkle（余韵光效）
```

## 在 hyperframes 中集成 SFX

hyperframes 的 `<audio>` 元素支持 `data-start` 和 `data-duration`：

```html
<audio src="assets/sfx/paper-turn.mp3" data-start="48.33" data-duration="1.5" data-volume="0.4" data-track-index="12"></audio>
```

- SFX 文件放在 `video/assets/sfx/` 下（软链接或复制）
- `data-start` 来自 shot-timing.json 的镜头起点 + 偏移
- `data-volume` 控制音量（0–1）
- 声音在画面锁定后才钉，时间线一动全表重对
