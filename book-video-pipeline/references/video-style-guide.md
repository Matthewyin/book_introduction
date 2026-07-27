# 视频风格规范

From the reference image provided by the user, the target illustration style for this book video is **collage / scrapbook illustration**: layered paper textures, torn edges, washi tape strips, soft pastel paper blocks, watercolor washes, paper-cut figures, hand-drawn accents, and mixed-media elements. The style feels handmade, warm, nostalgic, and intimate, like a personal journal page brought to life. It is not oil painting, not 3D render, not realistic photography, and not flat vector.

When adapting for this book video, preserve the **collage / scrapbook style**: layered paper, gentle textures, torn edges, tape accents, and soft watercolor or paper-wash highlights. The bottom 1/3 of the 9:16 frame should remain visually quiet for Chinese subtitles. No readable text, no watermark, no UI elements inside the generated image.

## 参考视频深度分析（ep001）

| 维度 | 观察 |
|------|------|
| 规格 | 1080×1920 竖屏，30fps，H.264，119 秒 |
| 画面 | 参考附件为现代扁平矢量插画风格，简洁色块、清晰轮廓、无厚重油画质感 |
| 开头 | 深色渐变背景，极简，聚焦感强 |
| 正文 | 场景插画 + 黄字字幕，逐句叙事推进 |
| 结尾 | 品牌色收束，logo 呈现 |
| 字幕 | 黄色居中，叙事性短句，底部 1/3 区域 |
| 品牌 | 左上角圆形 logo"二味图书馆" |
| 音频 | 旁白配音 + 背景音乐 |

### 插画风格精确描述（用于 AI 生图提示词）

经用户最终确认的参考图（shot_001_collage.png），统一插画风格为：

| 维度 | 特征 |
|------|------|
| **绘画媒介** | 拼贴 / 剪贴簿插画（collage / scrapbook illustration），混合纸材、水彩、手绘线条 |
| **笔触** | 纸张边缘、撕边、胶带、手绘线条、水彩晕染，有手工温度但不粗糙 |
| **光影** | 以纸张层次和水彩色块表达明暗，光源方向明确但不写实，无厚重体积阴影 |
| **色彩** | 奶油纸底 #F5F1EA + 浅粉 #E8C4C4 + 雾蓝 #A8C0D0 + 暖金 #E8C37A + 牛皮纸 #C4A882；痛点场景偏冷蓝/灰，治愈场景偏暖金/粉 |
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

### 配色（心理励志垂类）

| 调性 | 适用 | 配色 |
|------|------|------|
| **warm 暖色** | 治愈、成长、自我接纳 | 奶油底 #F5F0E8 + 暖金 #E8B565 + 赭石 #B85C38 |
| **calm 沉静** | 深度思考、哲学、内省 | 浅灰蓝 #D6E0E8 + 雾蓝 #7B9EA8 + 米白 #F8F6F2 |
| **contrast 强对比** | 痛点觉醒、反常识、冲击 | 冷灰底 #E8E4E0 + 暗蓝 #2C3E50 + 强调红/金 |

### 字幕规范

```
位置：底部 1/3 处（距底部约 180px）
颜色：#FFD700（金黄）
字体：Noto Sans CJK SC（思源黑体）
字号：52px
描边：黑色 2px
阴影：1px
对齐：水平居中
每行：≤16 字
每条：≤4 秒
风格：叙事性短句，不堆关键词
```

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
