# A 线·金句流完整工作流

> **A 线 = 金句流（60 秒短视频，快速涨粉）。B 线 = 方法论流（现有 8 段螺旋结构，深度留存）。**
> 两线并存于 book-video-pipeline 插件，共享 pipeline.yaml / assets / brand 资源。

## 什么时候用 A 线

- 用户说"金句流"/"金句视频"/"A 线" → 触发 A 线
- 用户说"方法论"/"深度解读"/"B 线" → 触发 B 线（现有流程）
- 默认推荐 A 线（制作快、爆款概率高）

## 8 步工作流

### Step Q1：选书 + 获取金句数据

```bash
python3 scripts/weread-highlights.py --book "一生 莫泊桑" --output 02-script/quotes-top20.json
```

- 调微信读书 `/store/search` 搜书 → bookId
- 调 `/book/bestbookmarks` 获取全书热门划线 Top20（含划线原文 + 划线人数 + 章节）
- 展示 Top20 给用户审核
- 🔴 **审核点 Q1**：用户确认要用的金句

### Step Q2：金句筛选 + 拼接

调 DeepSeek V4 Flash，输入 Top20 划线，system prompt 约束：
- 筛选 3-5 句（独立成句、情感冲击、口语化、15-35 字/句）
- 按情绪递进排序：扎心 → 深入 → 升华
- 加极少量过渡词，拼成 90-150 字朗读稿
- 输出 `quote-script.md` + `voiceover-text.txt`

```bash
python3 scripts/deepseek-call.py templates/quote-selector-system.md \
  02-script/quotes-top20.json \
  02-script/quote-script.md --model deepseek-v4-flash
```

- 🔴 **审核点 Q2**：用户确认金句稿

### Step Q3：配音

```bash
python3 scripts/tts-minimax.py 02-script/voiceover-text.txt \
  03-assets/audio/voiceover.wav --voice danya_xuejie --speed 0.9
```

- 慢一档（0.9 倍速），适合金句的留白感
- 🔴 **审核点 Q3**：用户确认配音

### Step Q4：搜索 + 下载实拍素材

用 ego-browser 从 Pixabay 搜索暖调实拍视频素材：

```bash
python3 scripts/pixabay-fetch.py --query "cozy reading book warm" \
  --count 5 --output-dir 03-assets/footage/
```

- 搜索词由金句情绪决定（见 `pixabay-keywords.md`）
- 下载 3-5 个 mp4，每个 5-15 秒
- 🔴 **审核点 Q4**：用户确认素材

### Step Q5：暖调封面生成（写实摄影）

A 线是实拍素材 + 写实风格，封面用 `--art realistic`（写实摄影底图）。

```bash
# 写实底图已预生成在 assets/cover-image/cover-3x4-realistic.png
# 直接用 cover-compose.py 叠字（无需每集重生图）
python3 scripts/cover-compose.py \
  --book-title "书名" --hook "金句钩子" \
  --art realistic --palette warm \
  --out-dir episodes/ep00X-书名/03-assets/cover
```

- 底图 prompt：`assets/cover-image/prompts/cover-3x4-realistic.md`（暖调写实摄影）
- 风格卡参考：`templates/styles/warm-still-life.md`（暖奶油/暖琥珀/暖棕，无人物）
- 缺失时用 `genimage.py --promptfiles cover-3x4-realistic.md` 重新生成
- 🔴 **审核点 Q5**：用户确认封面

### Step Q6：hyperframes 合成

写 `composition.html`：
- 每句金句对应一个 clip，嵌入 `<video>`（实拍素材）
- 配音用独立 `<audio>`（src=voiceover.wav）
- 字幕独立 `<div>` 图层（暖白大字居中，暖色底条，样式见 `quote-subtitle-style.md`）
- 转场淡入，金句之间呼吸停顿
- 片头 intro.mp4（1s）+ 片尾 outro.mp4（3.2s）

时间轴：ffmpeg silencedetect 检测 voiceover.wav 的句子间隔 → 驱动字幕和素材切换。

```bash
npx hyperframes render composition.html --output 04-output/quote-video.mp4
```

- 🔴 **审核点 Q6**：用户确认成片

### Step Q7：字幕校准

- 检查字幕与配音对齐（字幕领先旁白 0.3-0.5 秒）
- 金句停留 ≥3 秒

### Step Q8：发布准备

- 标题统一格式：`今天分享《{书名}》——{最扎心金句前半句}…`
- 标签统一：`#读书 #好书推荐 #情感共鸣`
- 生成发布文案（1-2 句书的核心价值主张）

## 与 B 线的关系

| 维度 | A 线·金句流 | B 线·方法论流 |
|------|------------|--------------|
| 时长 | ≤60 秒 | 165-240 秒 |
| 文案来源 | 书中原句（微信读书划线） | DeepSeek 原创 |
| 结构 | 无结构（金句串联） | 8 段螺旋 |
| 画面 | Pixabay 实拍素材 | AI 生图 |
| 合成 | hyperframes（`<video>` 嵌入） | hyperframes（静帧 + 动效） |
| 制作成本 | 低 | 高 |
| 爆款概率 | 高 | 中等 |
| 粉丝粘性 | 中 | 高 |
| 配音 | 0.9 倍速（慢） | 1.1 倍速（正常） |

## 同书双发策略

同一本书可以先发 A 线金句流（引流），3 天后发 B 线方法论（深度），同书两波流量。
