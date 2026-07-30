# 视频风格规范

> **本文件是插画风格的唯一控制源。** 所有生图提示词的风格段落必须由本文件派生，
> 落地形式是 `templates/style-prefix.en.md`（英文风格前缀常量）。
> DeepSeek 只负责写当镜的画面内容，**不得自行改写风格描述或色值**。
> 改风格 = 改本文件 → 重新派生 `style-prefix.en.md` → 全集重生图。

From the reference image provided by the user, the target illustration style for this book video is **collage / scrapbook illustration**: layered paper textures, torn edges, washi tape strips, soft pastel paper blocks, watercolor washes, paper-cut figures, hand-drawn accents, and mixed-media elements. The style feels handmade, warm, nostalgic, and intimate, like a personal journal page brought to life. It is not oil painting, not 3D render, not realistic photography, and not flat vector.

When adapting for this book video, preserve the **collage / scrapbook style**: layered paper, gentle textures, torn edges, tape accents, and soft watercolor or paper-wash highlights. The bottom 1/3 of the 9:16 frame should remain visually quiet for Chinese subtitles. No readable text, no watermark, no UI elements inside the generated image.

## 参考视频深度分析（ep001）

| 维度 | 观察 |
|------|------|
| 规格 | 1080×1920 竖屏，30fps，H.264 |
| 画面 | 拼贴剪贴簿插画，层叠纸材、撕边、胶带、水彩晕染，无厚重油画质感 |
| 开头 | 深色渐变背景，极简，聚焦感强 |
| 正文 | 场景插画 + 黄字字幕，逐句叙事推进 |
| 结尾 | 品牌色收束，logo 呈现 |
| 字幕 | 黄色居中，叙事性短句，底部 1/3 区域 |
| 品牌 | 左上角圆形 logo"二味图书馆" |
| 音频 | 旁白配音 + 背景音乐 |

### 插画风格精确描述（用于 AI 生图提示词）

风格来源：ep001 用同一镜头（shot_001）跑了 6 版风格试验（扁平矢量 / 黏土 / 2D 动画 /
线稿 / 波普 / 拼贴），用户最终选定 `shot_001_collage.png`。本节即由那条提示词反向固化而来。

| 维度 | 特征 |
|------|------|
| **绘画媒介** | 拼贴 / 剪贴簿插画（collage / scrapbook illustration），混合纸材、水彩、手绘线条 |
| **笔触** | 纸张边缘、撕边、胶带、手绘线条、水彩晕染，有手工温度但不粗糙 |
| **光影** | 以纸张层次和水彩色块表达明暗，光源方向明确但不写实，无厚重体积阴影 |
| **色彩** | 见下方「基准色板」，五色固定，情绪只调冷暖配比，不换 hex |
| **人物造型** | 剪纸风格人物，简洁轮廓，面部极简化，靠姿态和头发/衣服形状传情 |
| **场景细节** | 可辨识的纸质道具（书本、手机、杯子、椅子、门、窗等），层次叠加 |
| **质感纹理** | 纸张纹理、水彩纸纹、胶带质感、撕边，整体有手工日记感 |
| **艺术参照** | 个人手账 / 剪贴簿艺术（scrapbook journal / collage art），温暖、私密、有叙事感 |
| **整体氛围** | 从紧绷/孤独逐步过渡到轻盈/治愈，像一页被翻动的心灵日记 |

## 风格核心词

**拼贴剪贴簿插画（collage / scrapbook illustration）+ 纸张层次 + 水彩晕染 + 手绘线条 + 9:16 竖版**

用纸张、胶带、水彩和简洁线条讲故事，每个画面像一页温暖的心灵手账。

## 画面风格细则

### 插画风格

- **类型**：拼贴 / 剪贴簿插画（collage / scrapbook），混合纸材、撕边、胶带、水彩、手绘线条
- **场景**：有具体环境（房间/街道/咖啡馆/书桌等），但以纸质层次和色块表达，不追求写实
- **构图**：竖版 9:16 优化，主体居中或偏上，底部 1/3 留空给字幕
- **角色**：剪纸/拼贴风格人物，姿态传情，面部简化，不强调五官细节
- **禁止**：油画质感、厚涂笔触、写实照片、3D 渲染、复杂写实现实光影、纯扁平矢量

### 基准色板（唯一一套，不得新增 hex）

五个色值固定，**任何镜头、任何情绪都只用这五个**：

| 角色 | hex | 英文名（写进提示词用这个） |
|------|-----|---------------------------|
| 奶油纸底 | `#F5F1EA` | `cream paper #F5F1EA` |
| 浅粉 | `#E8C4C4` | `soft pink #E8C4C4` |
| 雾蓝 | `#A8C0D0` | `muted blue #A8C0D0` |
| 暖金 | `#E8C37A` | `warm gold paper #E8C37A` |
| 牛皮纸 | `#C4A882` | `kraft brown #C4A882` |

情绪差异**靠配比表达，不靠换色**：

| 调性 | 适用段落 | 配比 |
|------|---------|------|
| **cool 冷** | 钩子、扎心场景、痛点 | 雾蓝/牛皮纸为主，暖金仅作微弱光源 |
| **neutral 中** | 引入书、观点拆解 | 奶油纸底为主，冷暖均衡 |
| **warm 暖** | 方法实操、结尾引导 | 暖金/浅粉为主，雾蓝退为背景阴影 |

> ⚠️ ep001 教训：正式版提示词里出现过 `#8B6F52`、`#7A93A8`、`#D4E4EC` 三个本表之外的
> 色值——因为当时每镜风格段落都由模型重写。改用 `style-prefix.en.md` 常量拼接后，
> 色板物理上不可能漂移。

### 字幕规范

> 字幕/金句的完整规范以 `references/subtitle-style.md` 为准，本节只列生图相关约束。

```
位置：底部 1/3 处（距底部约 190px）
字号：48px
每行：≤16 字
```

**对生图的要求**：9:16 画面底部 1/3 必须视觉安静——不放主体、不放高对比细节，
留给字幕叠加。这条要写进每一条生图提示词（已固化在 `templates/style-prefix.en.md`）。

### 品牌 logo

```
位置：左上角
尺寸：80×80 px
透明度：0.85
形式：圆形或简约标识
```

## 转场规范

| 类型 | 用法 | 时长 |
|------|------|------|
| 叠化（crossfade） | 场景之间默认转场 | 0.8-1.2s |
| 渐入（fade in） | 开头从黑/品牌色渐入 | 1s |
| 渐出（fade out） | 结尾渐出到品牌色 | 1s |
| 硬切 | **不使用** | — |

不用花哨特效（缩放、旋转、滑动），保持沉稳的叙事感。

## 音频规范

| 元素 | 规范 |
|------|------|
| 旁白音量 | 1.0（基准） |
| BGM 音量 | 0.15（不盖过人声） |
| BGM 类型 | 轻钢琴/弦乐/氛围乐，无歌词 |
| BGM 节奏 | 慢-中速，不抢节奏 |
| 音频格式 | AAC 48kHz 立体声 192kbps |

## 节奏规范

| 段落 | 节奏 | 画面变化频率 |
|------|------|-------------|
| 开头钩子 | 慢，留白 | 1 个画面/5s |
| 场景演绎 | 中，沉浸 | 1 个画面/10-12s |
| 观点拆解 | 中快，推进 | 1 个画面/12-15s |
| 方法实操 | 中，清晰 | 1 个画面/13-15s |
| 结尾引导 | 慢，收束 | 1 个画面/10s |

**原则**：画面不频繁切换，给观众时间消化每个观点。每个插画画面至少停留 8 秒以上。

## 风格一致性原则

同一系列（同一本书的多条视频，或同一账号的所有视频）必须保持：

1. **配色统一**：选定一个 palette 贯穿始终
2. **插画风格统一**：相同笔触、光影、质感
3. **字幕规范统一**：同字体、同颜色、同位置
4. **品牌元素统一**：logo 位置和形式固定
5. **节奏感统一**：相似的画面停留时长和转场方式
