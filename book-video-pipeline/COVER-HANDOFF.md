# COVER-HANDOFF — 封面流程说明（Canva 已取消 · 双风格轨）

> ⚠️ **更新（本文件已不再指向 Canva）**：封面流程已改为「模板 + 本地排版合成」，
> 不依赖 Canva MCP。本文件保留作流程说明，后续会话**不要**再走 Canva 路线。

## 双风格轨：封面跟随视频风格

**视频写实→封面写实摄影；视频动漫→封面动漫插画。** 根据本集视频选定的风格卡决定 `--art` 参数。

| `--art` | 视频风格卡 | 底图文件 |
|---------|-----------|---------|
| `realistic`（默认） | `cinematic-girl.md`（写实人设） | `cover-3x4-realistic.png` / `cover-9x16-realistic.png` |
| `anime` | `cute-anime-girl.md`（动漫人设） | `cover-3x4-anime.png` / `cover-9x16-anime.png` |

两套风格共用相同的三分区布局 + 暖调色板 + 严禁人物 + 无字约束，只在表现手法上区分。

## 当前封面流程（无 Canva，零 API 文字层）

```
1. 模板（已验收，系列共用，勿覆盖）：
   /Users/luantai/Coding/video/assets/cover-image/
     cover-3x4-realistic.png（写实 3:4）
     cover-9x16-realistic.png（写实 9:16）
     cover-3x4-anime.png（动漫 3:4）
     cover-9x16-anime.png（动漫 9:16）
   规范：/Users/luantai/.agents/skills/book-video-pipeline/templates/cover-prompt.md
2. 每集合成（文字 100% 保真）：
   python3 /Users/luantai/.agents/skills/book-video-pipeline/scripts/cover-compose.py \
     --book-title <书名≤10字> --hook <钩子≤12字> --author <作者> --episode EPXX \
     --art realistic \  # 或 anime，跟随视频风格
     --palette warm \
     --out-dir /Users/luantai/Coding/video/episodes/ep00X-书名/03-assets/cover
   → 产出 cover-final.png（1080×1440）+ cover-final-9x16.png（1080×1920）
3. 规格：/Users/luantai/.agents/skills/book-video-pipeline/templates/cover-design.md
```

## 配置

- `pipeline.yaml` → `cover:` 节：`template_dir` / `default_art` / `logo` / `template_has_brand` / `series_name` / `corner_right` / `font_title` / `font_hook` / `font_body` / `out_3x4` / `out_9x16`
- 字体（均在 `~/Library/Fonts/`）：
  - 书名：NotoSansSC-Regular（思源黑体常规，**不加粗、不描边**）
  - 钩子/作者：FandolFang-Regular（仿宋，**描边加粗** `0.0014H`）
  - 系列/右上角：LxgwWenKai-Regular（霞鹜文楷，暖调手写感）
- logo：透明背景直贴原图 alpha（无底卡），左上角 30% 画布宽

## 四轴参数速查

| 参数 | 作用 | 取值 |
|------|------|------|
| `--art` | 画面风格（跟随视频） | `realistic` 写实摄影 / `anime` 动漫插画 |
| `--style` | 字体样式 | `quiet` 暖棕安静体 / `viral` 病毒标题体 |
| `--palette` | 配色 | `sunny` 阳光暖棕 / `warm` 秋冬暖橙 / `calm` 冷静蓝灰 |
| `--template` | 布局版式 | `ambient` 氛围静物 / `bookshot` 书封特写 |

## 不再使用（历史）

- Canva MCP 路径（master 模板 / edit 事务 / upload-asset）已废弃，勿回退。
- 旧裸名底图 `cover-3x4.png` / `cover-9x16.png` 已归档到 `_archive/`，不再被脚本引用。
