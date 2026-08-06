# A 线·金句流完整工作流

> **A 线 = 金句流（60 秒短视频，快速涨粉）。B 线 = 方法论流（现有 8 段螺旋结构，深度留存）。**
> 两线并存于 book-video-pipeline 插件，共享 pipeline.yaml / assets / brand 资源。

## 什么时候用 A 线

- 用户说"金句流"/"金句视频"/"A 线" → 触发 A 线
- 用户说"方法论"/"深度解读"/"B 线" → 触发 B 线（现有流程）
- 默认推荐 A 线（制作快、爆款概率高）

## 8 步工作流

### Step Q1：选书 + 获取金句数据 + 确认书封

```bash
python3 scripts/weread-highlights.py --book "一生 莫泊桑" --output 02-script/quotes-top20.json
```

- 调微信读书 `/store/search` 搜书 → bookId
- 调 `/book/bestbookmarks` 获取全书热门划线 Top20（含划线原文 + 划线人数 + 章节）
- **确认书封存在**：检查 `assets/book-covers/{书名}.png`（预建书封库，20 本）
  - 存在 → 继续
  - 不存在 → 🔴 blocked，提示用户先补充书封到书封库（见 `assets/book-covers/README.md`）
- 展示 Top20 给用户审核
- **自检**：查 `step-checklists.md` Q1 项（书封库/bookId/章节精准/与前集去重）
- 🔴 **审核点 Q1**：用户确认要用的金句

### Step Q2：金句筛选 + 拼接

调 DeepSeek V4 Flash，输入 Top20 划线，system prompt 约束：
- 筛选 3-5 句（独立成句、情感冲击、口语化、15-35 字/句）
- 按情绪递进排序：扎心 → 深入 → 升华
- **开头加引入句**（固定模板）：`今天分享的书籍是：《{书名}》作者：{作者}。书中有这样一句话——`
- 加极少量过渡词，拼成 120-175 字朗读稿（含引入句）
- 输出 `quote-script.md` + `voiceover-text.txt`（voiceover-text.txt 第一行是引入句，后面是金句）

```bash
python3 scripts/deepseek-call.py templates/quote-selector-system.md \
  02-script/quotes-top20.json \
  02-script/quote-script.md --model deepseek-v4-flash
```

- **自检**：查 `step-checklists.md` Q2 项（字数120-175/单句≤35字/与前集去重/情绪递进）
- 🔴 **审核点 Q2**：用户确认金句稿

### Step Q3：配音

```bash
python3 scripts/tts-minimax.py 02-script/voiceover-text.txt \
  03-assets/audio/voiceover.wav --voice danya_xuejie --speed 1.0
```

- 1.0 倍速，适合金句的留白感
- **自检**：查 `step-checklists.md` Q3 项（倍速参数/样本用本集真实文本/时长记录）
- 🔴 **审核点 Q3**：用户确认配音

### Step Q4：搜索 + 下载实拍素材

用 ego-browser 从 Pixabay 搜索暖调实拍视频素材：

```bash
python3 scripts/pixabay-fetch.py --query "mountain lake reflection calm" \
  --count 5 --output-dir 03-assets/footage/
```

**素材硬性要求（2026-08 起强制执行，脚本自动过滤）：**

1. **素材方向：自然风光、山水**——搜索词围绕山水/森林/湖泊/日出/云雾等自然场景，
   不选城市街景、人群、室内静物。自然画面与金句的内省气质同构，且不过时。
2. **分辨率 720p-1080p**（竖边高度 720-1080px）。
3. **单文件体积 ≤10MB**——超限脚本自动换 `_medium`/`_small` 变体重试，仍超则丢弃换下一候选。

- 搜索词由金句情绪决定（见 `pixabay-keywords.md`，首选"自然风光·山水"分类）
- 下载 3-5 个 mp4，每个 5-15 秒
- 🔴 **审核点 Q4**：用户确认素材

### Step Q5：封面生成（素材截图 + 手写体排版，复刻「十二..」风格）

A 线封面从**下载的素材视频**截图做背景 + LXGW 霞鹜文楷手写体排版（A/B 线统一风格，见 SKILL.md Step 7b）。

**风格**（学抖音「十二..」）：空旷风景 + 白色手写体 + 无底条无描边 + 低饱和治愈调。

#### Q5a：截 6 张候选图 → 审核

1. 从 `03-assets/footage/` 下的**素材视频**（不是合成成片）各取一帧，共截 6 张候选图。
   - 选空旷、干净、上半部留白多的帧（天空/云海/田野/海面）
   - 避开有书封、有字幕、画面太满的帧
   - 编号 `cover-cand-01.jpg` ~ `cover-cand-06.jpg`，存到 `03-assets/cover/candidates/`
2. 拼成一张 6 宫格预览图展示给用户。
3. 🔴 **审核点 Q5a**：用户从 6 张中选定 1 张做封面背景。

```bash
# 从素材视频截 6 张候选（每条素材取一帧）
for f in 03-assets/footage/q*/*.mp4; do
  mid=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" | python3 -c "print(float(input())/2)")
  ffmpeg -y -v error -ss "$mid" -i "$f" -frames:v 1 -vf "scale=540:720:force_original_aspect_ratio=increase,crop=540:720" \
    "03-assets/cover/candidates/cover-cand-$(printf '%02d' $((++n))).jpg"
done
```

#### Q5b：排版生成封面

用户选定后，用选中的候选图 + `cover-shier.py` 排版：

```bash
python3 scripts/cover-shier.py \
  --image 03-assets/cover/candidates/cover-cand-XX.jpg \
  --book-title 影响力 \
  --author 罗伯特·西奥迪尼 \
  --out-dir 03-assets/cover
```

封面规格：
   - 背景：素材截图（空旷云海/天空/田野），饱和度 ×0.85、亮度 ×1.05
   - 字体：LXGW 霞鹜文楷 Regular（`~/Library/Fonts/LxgwWenKai-Regular.ttf`）
   - 文字：白色、上半部居中
     - 书名《书名》88px
     - 作者：XXX 42px
     - 底部标签 `#读书 #好书推荐 #情感共鸣` 30px
   - 无底条、无描边（文字直接印在风景上）
   - 上半部极淡白色渐变（alpha 0→40）柔和文字区
4. 产出 `cover-final.png`（3:4 小红书 1080×1440）+ `cover-final-9x16.png`（9:16 抖音 1080×1920）。
5. **自检**：查 `step-checklists.md` Q5 项（素材视频抽帧/6宫格/品牌卡logo/LXGW手写体/双尺寸/低饱和）
6. 🔴 **审核点 Q5b**：用户确认最终封面

### Step Q6：hyperframes 合成

写 `composition.html`：
- **开头书封快闪**（学抖音读书博主，让观众第一眼知道是读书账号）：
  1. **t=0-1.0s 品牌片头**：intro.mp4（保持不变）
  2. **t=1.0-2.0s 书封快闪**：从书封库随机取 10 本（排除本集书），每本 0.1s 快速翻飞。
     - 每本书封装进毛玻璃卡片（flex 包裹，backdrop-filter: blur(16px)，padding 288px，宽度自适应贴住书封）
     - 快闪段背景用静帧（从视频抽一帧 PNG），避免背景运动与书封快速切换产生边框错觉
     - 书封库图片需先去除白边（`assets/book-covers/trim_whitespace.py`，autocrop 阈值 235）
  3. **t=2.0-4.0s 本集书封落定**：本集书封从缩放入场（back.out 0.5s）→ 停留 1.5s → 放大淡出
     - 书名+作者 overlay 同步显示（画面上方 14%）
     - 背景恢复云海视频流动
     - 对应口播："今天分享的书籍是：《书名》作者：XXX"
     - t=3.7 放大淡出，t=4.0 引入金句段
- 完整书封快闪规格见 `templates/quote-subtitle-style.md` 的「书封快闪开头」节
- 每句金句对应一个 clip，嵌入 `<video>`（实拍素材，必须是 root 直接子元素，`data-media-start` 选窗口；慢放镜头先用 ffmpeg `setpts` 预处理，不靠渲染器）
- 配音用独立 `<audio>`（src=voiceover.wav，含引入句+过渡句+金句）
- **BGM 必配**（2026-08 起）：ego-browser 从 Pixabay 音乐下载 2-3 首候选（calm piano / ambient 优先），
  用户选定后 ffmpeg 裁到全片时长 + 淡入 1s 淡出 2s，`<audio data-volume="0.15">` 嵌入，不盖人声
- 字幕独立 `<div>` 图层（样式以 `templates/video-spec.md` 为准）
- 品牌角标 320×80px（`height: 80px; width: auto;`，以 SKILL.md Step 0 为准）
- 转场交叉淡入淡出 0.6s（GSAP opacity，首帧不淡入），金句之间呼吸停顿
- 片尾 outro.mp4（3.2s）
- 书封快闪开头的完整规格见 `templates/quote-subtitle-style.md` 的「书封快闪开头」节

时间轴：ffmpeg silencedetect 检测 voiceover.wav 的句子间隔 → 驱动字幕和素材切换。

```bash
npx hyperframes render composition.html --output 04-output/quote-video.mp4
```

- **自检**：查 `step-checklists.md` Q6 项（**无黑屏**/书封快闪10本/字幕无重叠/字幕领先旁白0.3s/品牌角标常驻/BGM 0.15/intro-outro静音/lint+check 0错/抽帧验证非黑帧/总时长≤60s）
- 🔴 **审核点 Q6**：用户确认成片

### Step Q7：字幕校准

- 检查字幕与配音对齐（字幕领先旁白 0.3-0.5 秒）
- 金句停留 ≥3 秒
- **自检**：查 `step-checklists.md` Q7 项（每条≥3s/SRT导出/断行可读）

### Step Q8：发布准备

- 标题统一格式：`今天分享《{书名}》——{最扎心金句前半句}…`
- 标签统一：`#读书 #好书推荐 #情感共鸣`
- **自检**：查 `step-checklists.md` Q8 项（标题≤20字/三大固定标签/合规检查全绿/封面图就位）
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
| 配音 | 1.0 倍速 | 1.1 倍速（正常） |

## 同书双发策略

同一本书可以先发 A 线金句流（引流），3 天后发 B 线方法论（深度），同书两波流量。
