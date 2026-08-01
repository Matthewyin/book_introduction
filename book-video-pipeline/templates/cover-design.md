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
- `cover-3x4.png` + `cover-9x16.png`：**底图 = 无字主视觉 + logo 品牌卡**，
  规范见 `cover-prompt.md`（无人物 · 一体式留白 · 清爽阳光向上 · 书/手机小号英文圆体字）
- 每集封面 = 底图（已含 logo，`template_has_brand: true` 跳过画 logo）+ 文字层，
  输出到本书 cover 目录。
- **重新生成主视觉后必须重跑底图**：`python3 scripts/cover-compose.py --base \
  --out-dir assets/cover-image`（把 logo 贴回新艺术图）。

## 版式分区（按高度比例，3:4 / 9:16 通用）

```
┌────────────────────────────────────┐
│ 顶部品牌区 (~4%)     左上：系列名 · EP03（小字，暖棕） │
│ 书名区 (~16–45%)     居中：书名（粗体，≤10字，自动缩字号） │
│                     钩子（≤12字，≤2行）            │
│                     作者（小字，暖棕）             │
│ 主视觉区 (45–100%)   场景：热茶/手机/半开的书/暖黄台灯（模板原图，不遮挡）│
└────────────────────────────────────┘
```

- 文字全部落在顶部一体式留白区，不遮挡下方主视觉。
- 配色：暖深棕文字（书名 #4A2E1B + 柔和投影）压在浅暖留白上，对比清晰。
- 字体：书名黑体常规不加粗不描边（`cover.font_title`，默认 NotoSansSC-Regular）；
  钩子/作者仿宋描边加粗（`cover.font_hook`，默认 FandolFang，stroke_width ≈ `0.0014H`）；
  系列/右上角 LxgwWenKai（`cover.font_body`，暖调手写感）。
- logo：透明背景直贴原图 alpha（无浅暖底卡），左上角，宽 = 30% 画布宽。

## 文案规则（每集）

- **书名**：≤10 字，不加《》；超长截断 + 省略号。
- **钩子**：≤12 字；优先取 `01-profile/book-profile.md` 选定带货角度的钩子。
- **作者**：作者名。
- 全部文案填充前过 ≤N 字校验（脚本自动缩字号兜底超宽）。

## 每集流程

```
1. 确认模板在 assets/cover-image/（缺失按 cover-prompt.md 用 gptsapi 重新生成）
2. 取文案：书名 / 钩子 / 作者 / 集数（book-profile + video-spec）
3. python3 scripts/cover-compose.py --book-title ... --hook ... --author ... \
     --episode EPXX --out-dir episodes/ep00X-书名/03-assets/cover
4. 核对：无错字、无溢出、留白区干净、主视觉未被遮挡
5. 产出 cover-final.png (3:4) + cover-final-9x16.png (9:16)
```

## 回退方案

- 模板缺失且不愿重生成 → 直接用旧 AI 带字封面（`cover-prompt.md` 旧版），
  在 run-manifest 标注 `cover_source: ai`。
- 字体缺失 → `cover-compose.py` 自动回退系统字体（Hiragino Sans GB 等）。
