# COVER-HANDOFF — 封面流程说明（Canva 已取消）

> ⚠️ **更新（本文件已不再指向 Canva）**：封面流程已改为「模板 + 本地排版合成」，
> 不依赖 Canva MCP。本文件保留作流程说明，后续会话**不要**再走 Canva 路线。

## 当前封面流程（无 Canva，零 API 文字层）

```
1. 模板（已验收，系列共用，勿覆盖）：
   /Users/luantai/Coding/video/assets/cover-image/cover-3x4.png（3:4）
   /Users/luantai/Coding/video/assets/cover-image/cover-9x16.png（9:16）
   规范：/Users/luantai/.agents/skills/book-video-pipeline/templates/cover-prompt.md
2. 每集合成（文字 100% 保真）：
   python3 /Users/luantai/.agents/skills/book-video-pipeline/scripts/cover-compose.py \
     --book-title <书名≤10字> --hook <钩子≤12字> --author <作者> --episode EPXX \
     --out-dir /Users/luantai/Coding/video/episodes/ep00X-书名/03-assets/cover
   → 产出 cover-final.png（1080×1440）+ cover-final-9x16.png（1080×1920）
3. 规格：/Users/luantai/.agents/skills/book-video-pipeline/templates/cover-design.md
```

## ep003 已落地

- `/Users/luantai/Coding/video/episodes/ep003-非暴力沟通/03-assets/cover/`
  - `cover-final.png`（3:4，左上 logo 透明直贴 + 右上好书推荐 + 书名黑体常规不加粗 + 钩子/作者仿宋描边加粗 + EP03）
  - `cover-final-9x16.png`（9:16）
  - `prompts/`（主视觉生成 prompt，可复现）

## 配置

- `pipeline.yaml` → `cover:` 节：`template_dir` / `logo` / `template_has_brand` / `series_name` / `corner_right` / `font_title` / `font_hook` / `font_body` / `out_3x4` / `out_9x16`
- 字体（均在 `~/Library/Fonts/`）：
  - 书名：NotoSansSC-Regular（思源黑体常规，**不加粗、不描边**）
  - 钩子/作者：FandolFang-Regular（仿宋，**描边加粗** `0.0014H`）
  - 系列/右上角：LxgwWenKai-Regular（霞鹜文楷，暖调手写感）
- logo：透明背景直贴原图 alpha（无底卡），左上角 30% 画布宽

## 不再使用（历史）

- Canva MCP 路径（master 模板 / edit 事务 / upload-asset）已废弃，勿回退。
- 若未来仍要用 Canva 出字，需新会话（工具注入机制），但当前流程已覆盖需求。
