# 通用封面设计规格（本地排版合成 · 无 Canva）

> 封面职责分离：**AI 出画（无字主视觉），本地排版出字（PIL）**。
> AI 负责画面（见 `cover-prompt.md`），文字用 `scripts/cover-compose.py`
> 确定性排版——文字 100% 保真、零 API 成本、每集只换文案秒出图。
> 本文件是封面的唯一规格源。

## 尺寸矩阵

| 渠道 | 尺寸 | 文件 |
|------|------|------|
| 小红书（主） | 1080×1440 (3:4) | `03-assets/cover/cover-final.png` |
| 抖音/视频号 | 1080×1920 (9:16) | `03-assets/cover/cover-final-9x16.png` |

## 模板（已验收 · 系列共用 · 两段式）

- 位置：`assets/cover-image/`（模板目录可在 `pipeline.yaml` `cover.template_dir` 改）
- **ambient 版**（默认）：`cover-3x4.png` + `cover-9x16.png`
  = **底图 = 无字主视觉 + logo 品牌卡**，规范见 `cover-prompt.md`
  （无人物 · 一体式留白 · 清爽阳光向上 · 书/手机小号英文圆体字）
- **bookshot 版**（书封特写）：`cover-3x4-bookshot.png` + `cover-9x16-bookshot.png`
  = 书封占 60-70%，文字落顶部窄带。prompt 见 `prompts/cover-examples.md` 范文 3。
- 每集封面 = 底图（已含 logo，`template_has_brand: true` 跳过画 logo）+ 文字层，
  输出到本书 cover 目录。
- **重新生成主视觉后必须重跑底图**：`python3 scripts/cover-compose.py --base \
  --out-dir assets/cover-image`（把 logo 贴回新艺术图）。

## 样式系统（`--style`）

| 样式 | 适用 | 书名 | 钩子 | 配色 |
|------|------|------|------|------|
| **quiet**（默认） | 治愈/散文/诗集 | 黑体常规不加粗，柔和投影 | 仿宋描边加粗 | 暖棕系 |
| **viral** | 干货/方法论/冲击力 | 超粗黑体（Bold+加重描边），白字投影 | 亮黄圆角标签底 + 黑字 | 同 palette |

## 配色系统（`--palette`）

| 配色 | 书名 | 钩子 | 次级文字 | 适用 |
|------|------|------|----------|------|
| **sunny**（默认） | #4A2E1B 暖深棕 | #5A3A20 | #7A5C3E | 阳光治愈 |
| **warm** | #7B3F00 暖橙棕 | #A0522D 赭石 | #8B5E3C | 秋冬/温暖系 |
| **calm** | #2C3E50 深蓝灰 | #34495E | #5D6D7E | 理性/方法论 |

## 版式分区（按高度比例，3:4 / 9:16 通用）

### ambient 版（默认）

```
┌────────────────────────────────────┐
│ 顶部品牌区 (~4%)     左上：logo 卡  右上：好书推荐/EP03 │
│ 书名区 (~16–45%)     居中：书名（≤10字，自动缩字号） │
│                     钩子（≤12字，≤2行）            │
│                     作者（小字）                  │
│ 主视觉区 (45–100%)   场景：窗边书桌/柠檬水/绿植（模板原图，不遮挡）│
└────────────────────────────────────┘
```

### bookshot 版（书封特写）

```
┌────────────────────────────────────┐
│ 顶部文字窄带 (~20%)  左上：logo  右上：好书推荐/EP   │
│                     书名（~8%，缩字号）             │
│                     钩子（~15%）                  │
│                     作者（~20%）                  │
│ 书封主体 (20–100%)   书封俯拍 45°，占画面 60-70%    │
└────────────────────────────────────┘
```

- 文字全部落在顶部留白区，不遮挡下方主视觉/书封。
- **安全区红线**：所有关键元素（logo/书名/钩子/作者）距画布四边 **≥10%**。
  `cover-compose.py --safe-margin 0.10` 会自动检测并打印越界警告。
- logo：透明背景直贴原图 alpha（无底卡），左上角，宽 = 30% 画布宽。

## 字体

| 字体键 | 用途 | 默认 | 样式 |
|--------|------|------|------|
| `font_title` | 书名（quiet 样式） | NotoSansSC-Regular | 常规不加粗不描边 |
| `font_title_viral` | 书名+钩子（viral 样式） | NotoSansSC-Bold | 粗体 + 加重描边 `0.003H` |
| `font_hook` | 钩子/作者（quiet 样式） | FandolFang-Regular | 仿宋描边加粗 `0.0014H` |
| `font_body` | 系列/右上角/EP | LxgwWenKai-Regular | 暖调手写感 |

## 文案规则（每集）

- **书名**：≤10 字，不加《》；超长截断 + 省略号。
- **钩子**：≤12 字；优先取 `01-profile/book-profile.md` 选定带货角度的钩子。
- **作者**：作者名。
- 全部文案填充前过 ≤N 字校验（脚本自动缩字号兜底超宽）。

## 每集流程

```
1. 确认模板在 assets/cover-image/（缺失按 cover-prompt.md + cover-examples.md 重新生成）
2. 取文案：书名 / 钩子 / 作者 / 集数（book-profile + video-spec）
3. python3 scripts/cover-compose.py --book-title ... --hook ... --author ... \
     --episode EPXX --out-dir episodes/ep00X-书名/03-assets/cover \
     [--style viral] [--palette calm] [--template bookshot]
4. 核对：无错字、无溢出、留白区干净、安全区无越界警告
5. 产出 cover-final.png (3:4) + cover-final-9x16.png (9:16)
```

## 回退方案

- 模板缺失且不愿重生成 → 直接用旧 AI 带字封面（`cover-prompt.md` 旧版），
  在 run-manifest 标注 `cover_source: ai`。
- 字体缺失 → `cover-compose.py` 自动回退系统字体（Hiragino Sans GB 等）。
