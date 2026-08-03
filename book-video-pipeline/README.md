# book-video-pipeline

心理励志图书带货短视频流水线 —— 把一本书变成一条 1080×1920、≤200 秒的竖屏带货视频。

本流水线是一个 **ZCode Skill**（也可作为独立的文档+脚本框架使用）。它不承诺播放量或成交额，只提供一套**带 7 个人工审核点**的确定性生产流程：从选书、文案、口播、分镜、素材生成、动效设计到最终合成，每一步都停下等你确认。

视觉风格采用**日系软萌 anime 水彩插画**（soft cel-shaded anime, watercolor edges, pastel palette），当前主力风格卡 `templates/styles/people/cute-anime-girl.md`。风格卡库支持人物线 / 萌宠线多套风格切换，每集先选风格并审核。

---

## 目录

- [功能特性](#功能特性)
- [安装](#安装)
- [使用说明](#使用说明)
- [组件清单](#组件清单)
- [架构](#架构)
- [调用关系](#调用关系)
- [规格红线](#规格红线)

---

## 功能特性

- **10 步确定性流程**：选书 → 文案策划 → 口播稿四道工序 → TTS 配音 → 真实时间轴提取 → 分镜 → 生图 → 动效设计 → hyperframes 合成 → 发布物料。
- **7 个人工审核点**：每个 🔴 节点用 `AskUserQuestion` 弹出「通过 / 修改 / 重做」，不跳过、不自动推进。
- **顺序铁律**：配音必须在分镜与生图之前定稿——音频真实时长是分镜的输入，不是产物。
- **去 AI 味闭环**：口播稿走 `Kimi 起草 → grok 初审 → DeepSeek 二审 → humanizer-zh 收尾` 四道工序，`check-script.py` 自动校验 20 项规则必须全绿。
- **字幕图层化**：字幕作为 hyperframes 独立 `<div>` 渲染，不烧进像素，改一句字幕只需重渲染无需重烧帧；同时导出独立 SRT。
- **动效分层**：免费 GSAP 动效层（尘埃、光束、纸张呼吸）+ 收费的 i2v 真动画（每集 ≤2 个镜头，用量可控）。
- **认证安全**：所有 API key 从环境变量或 shell profile 读取，项目内零硬编码、零缓存。

---

## 安装

### 1. 系统依赖

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| **Python 3.10+** | 运行 `scripts/` 下的脚本 | 系统自带或 `brew install python` |
| **Node.js 18+** | hyperframes 渲染引擎 | `brew install node` |
| **ffmpeg** | 音频时间轴检测、BGM 混音、i2v 去音轨 | `brew install ffmpeg` |
| **ZCode CLI** | 加载本 Skill、调用子 Skill、审核点交互 | 见 [ZCode 文档](https://zcode.dev) |

验证：

```bash
python3 --version    # ≥ 3.10
node --version       # ≥ 18
ffmpeg -version      # 任意版本，无需 libass（字幕由 hyperframes 渲染）
```

### 2. Python 脚本依赖

脚本仅用 Python 标准库（`json` / `os` / `sys` / `urllib` / `argparse` / `re` / `base64` / `subprocess`），**无需 `pip install`**。

### 3. 外部工具（可选，按需启用）

| 工具 | 触发阶段 | 安装 |
|------|----------|------|
| **hyperframes** | Step 9 合成 | `npx hyperframes@0.7.76`（首次自动下载） |
| **即梦 dreamina CLI** | Step 8a i2v 真动画 | 见即梦官方 CLI 文档 |
| **ego-browser** | Step 9b BGM 下载（绕过 pixabay Cloudflare） | ZCode Skill `ego-browser` |
| **humanizer-zh** | Step 3d 去 AI 味 | ZCode Skill `humanizer-zh` |
| **seedance-prompt-zh** | Step 8a i2v 提示词 | ZCode Skill `seedance-prompt-zh` |
| **baoyu ai-content-pipeline** | Step 7 生图（gptsapi 通道：定妆图 + 无主角镜头） | ZCode Skill `ai-content-pipeline`，脚本 `~/.agents/skills/ai-content-pipeline/scripts/gptsapi_image.py` |
| **dreamina CLI** | Step 7 主角镜头（Seedream 5.0 image2image）+ Step 8a i2v | `~/.local/bin/dreamina`，需 `dreamina login`（OAuth） |
| **baoyu-image-gen** | Step 7 备用参考图通道（MiniMax） | ZCode Skill `baoyu-image-gen`，需 `bun`（`brew install oven-sh/bun/bun`） |

### 4. API 密钥

所有密钥写入 `~/.zshrc`（或你的 shell profile），项目内不存储：

```bash
# ~/.zshrc
export KIMI_API_KEY="..."        # Kimi K3，文案策划 + 口播起草
export DEEPSEEK_API_KEY="..."    # DeepSeek V4 Pro/Flash，二审 + 分镜 + 提示词
export MINIMAX_API_KEY="..."     # MiniMax T2A v2 配音 + image-01 参考图生图（共用）
export GPTSAPI_KEY="..."         # gptsapi（GPT Image 2），定妆图 + 无主角镜头
```

dreamina CLI 用 OAuth 登录（不用 API key）：`dreamina login`，登录态存 `~/.dreamina/`。
项目不读取、不缓存 dreamina 认证。

生图 key 读取优先级：环境变量 → `<cwd>/.baoyu-skills/.env` → `~/.baoyu-skills/.env` → `--api-key` 参数（仅调试）。

⚠️ **项目级 EXTEND.md（安装时需手动拷一次）**：

```bash
mkdir -p .baoyu-skills/baoyu-image-gen
cp book-video-pipeline/templates/baoyu-image-gen-EXTEND.md \
   .baoyu-skills/baoyu-image-gen/EXTEND.md
```

用户级 EXTEND.md 通常是 `default_provider: zai` + `default_aspect_ratio: "16:9"`，在本项目下会静默出横图且不支持参考图。`.baoyu-skills/` 被 gitignore（防泄密兜底），所以模板放在插件里、安装时拷贝。

grok CLI **已退出主流程**（保留备用），如需重新启用仍遵循账户继承原则——不读 `~/.grok/auth.json`、不缓存 token。

### 5. 品牌素材（一次性）

```bash
assets/
├── brand/
│   ├── intro.mp4      # 品牌片头，已 -an 去音轨
│   └── outro.mp4      # 品牌片尾，已 -an 去音轨
├── voices/            # 音色素材库
│   ├── voice-library.json
│   └── samples/       # 试听样本
└── bgm/candidates/    # BGM 候选
```

---

## 使用说明

> 以下以 ZCode 为例。在 ZCode 会话中触发本 Skill 后，Agent 会按步骤推进并在每个审核点停下。

### 触发流水线

```
请用 book-video-pipeline 为《被讨厌的勇气》做一条带货视频，角度：讨好型人格自救。
```

Agent 会自动：选书 → 写档案 → 弹出**审核点①**等你确认。

### 10 步流程速览

| 步骤 | 产出 | 负责人 | 审核点 |
|------|------|--------|--------|
| **Step 0** 片头片尾 | `assets/brand/{intro,outro}.mp4` | ffmpeg（一次性，已完成） | — |
| **Step 1** 选书 | `01-profile/book-profile.md` | GLM-5.2 | 🔴 ① |
| **Step 2** 文案策划 | `02-script/script-brief.md` | Kimi K3 | 🔴 ② |
| **Step 3** 口播稿四道工序 | `02-script/SCRIPT.md` | Kimi→grok→DeepSeek→humanizer-zh | 🔴 ③ |
| **Step 4** TTS 配音 | `03-assets/audio/voiceover.wav` | MiniMax T2A v2 | 🔴 ④ |
| **Step 5** 真实时间轴 | `02-script/shot-timing.json` | `realign-shots.py` + ffmpeg | — |
| **Step 6** 分镜 | `02-script/STORYBOARD.md` | DeepSeek V4 Pro | 🔴 ⑤ |
| **Step 7** 生图 | `03-assets/scenes/shot_*.png` | `genimage.py` → gptsapi / dreamina Seedream | 🔴 ⑥ |
| **Step 8** 动效设计 | `02-script/motion-plan.md` | GSAP / 即梦 i2v | — |
| **Step 9** 合成 | `04-video/output.mp4` + `subtitle.srt` | hyperframes | 🔴 ⑦ |
| **Step 9b** BGM | `03-assets/audio/bgm.mp3` | ego-browser → pixabay | 🔴 ⑦b |
| **Step 10** 发布物料 | `05-publish/publish-brief.md` | GLM-5.2 | — |

### 顺序铁律

```
口播稿 → TTS 定稿 → 从音频提取真实时间轴 → 分镜（含动效字段）→ 生图 → hyperframes 合成
```

**颠倒顺序的后果**：换音色 → 时长变化 → 时间轴全废 → 字幕错位 → 视频重合成。

### 脚本单独使用

脚本可独立调用，无需 ZCode：

```bash
# 1. Kimi 文案（Step 2 / 3a）
python3 scripts/kimi-call.py system.md user.md out.md --model kimi-k3

# 2. DeepSeek 二审 / 分镜 / 提示词（Step 3c / 6 / 7）
python3 scripts/deepseek-call.py system.md user.md out.md --model deepseek-v4-pro

# 3. MiniMax 配音（Step 4）
python3 scripts/tts-minimax.py voiceover-text.txt voiceover.wav --voice danya_xuejie --speed 1.1

# 4. 从音频提取真实时间轴（Step 5）
python3 scripts/realign-shots.py voiceover.wav shots-input.json shot-timing.json

# 5. 字幕逐句切分（Step 6 辅助）
python3 scripts/make-cues.py shot-timing.json --out subtitle-cues.json

# 6. 去 AI 味自动校验（Step 3d，必须全绿）
python3 scripts/check-script.py 02-script/draft-04-final.md --before 02-script/draft-03-reviewed.md

# 7. 生图（Step 7）—— 统一入口，按 characters + charRef 自动路由后端
# 全局定妆图已就位：assets/protagonist-base/girl-ref.png（无需每集重生）
# 含主角镜头（dreamina Seedream，带全局定妆图 ref）
python3 scripts/genimage.py \
  --style templates/styles/people/cute-anime-girl.md \
  --promptfiles 03-assets/scenes/shot_002.scene.md \
  --image 03-assets/scenes/shot_002.png --ar 9:16 \
  --charRef assets/protagonist-base/girl-ref.png
python3 scripts/genimage.py --batchfile 03-assets/scenes/batch.json --jobs 3

# 8. 成片规格校验（Step 9 收尾）
python3 scripts/validate-spec.py 04-video/output.mp4
```

### hyperframes 合成（Step 9）

```bash
cd episodes/ep00X-书名/video
npx hyperframes lint       # 0 错误
npx hyperframes check      # 0 错误
npx hyperframes render     # 渲染成片 → 04-video/output.mp4
python3 ../../..//book-video-pipeline/scripts/validate-spec.py ../04-video/output.mp4
```

---

## 组件清单

### 脚本（`scripts/`，10 个）

| 脚本 | 作用 | 输入 → 输出 | 依赖密钥 |
|------|------|-------------|----------|
| `config.py` | 配置加载器（pipeline.yaml） | 读 pipeline.yaml，所有脚本共用 | — |
| `kimi-call.py` | 调 Kimi K3 生成文案 | `<system.md> <user.md> <out.md>` | `KIMI_API_KEY` |
| `deepseek-call.py` | 调 DeepSeek 生成/审查内容 | `<system.md> <user.md> <out.md> --model` | `DEEPSEEK_API_KEY` |
| `tts-minimax.py` | MiniMax T2A v2 配音 | `<text.txt> <out.wav> --voice --speed` | `MINIMAX_API_KEY` |
| `realign-shots.py` | 从配音提取真实时间轴 | `<voiceover.wav> <shots.json> <out.json>` | ffmpeg |
| `make-cues.py` | 逐句字幕切分（按标点不破词） | `<shot-timing.json> --out` | — |
| `check-script.py` | 去 AI 味自动校验（20 项规则） | `<script.md> [--before <early.md>]` | — |
| `validate-spec.py` | 成片规格校验 | `<video.mp4>` | ffmpeg/ffprobe |
| `genimage.py` | 生图统一入口（分发层：gptsapi / dreamina Seedream / MiniMax） | `--style ... --promptfiles ... --image` 或 `--batchfile` | `GPTSAPI_KEY` / `MINIMAX_API_KEY` / dreamina OAuth |
| `cover-compose.py` | 封面本地排版合成（无 Canva，零 API，支持 `--style viral`/`--palette`/`--template`） | `--book-title ... --hook ... --author ... --episode ... --out-dir [--style viral] [--palette calm]` | — |

### 模板（`templates/`，12 个 + `styles/` 风格卡库）

| 模板 | 步骤 | 产出文件 |
|------|------|----------|
| `pipeline.yaml` | 全流程 | 模型/端点/后端可配置参数（唯一源，密钥不入此文件） |
| `book-profile.md` | Step 1 | 选书档案 |
| `script-brief.md` | Step 2 | 文案策划简报 |
| `SCRIPT-template.md` | Step 3e | 锁定旁白（对齐 hyperframes `script-format.md`） |
| `STORYBOARD-template.md` | Step 6 | 分镜（对齐 hyperframes `storyboard-format.md`） |
| `video-spec.md` | 全流程 | 视频技术规格红线 |
| `scene-prompt.md` | Step 7 | 提示词组织方式（拼接规则、通道分工、一致性清单） |
| `style-prefix.en.md` | Step 7 | （旧版风格常量，已被 `styles/` 风格卡库取代，保留兼容） |
| `styles/` 风格卡库 | Step 7.0 | 风格卡（主力：`people/cute-anime-girl.md` 动漫水彩 + `people/cinematic-girl.md` 写实电影）+ README |
| `scene-content.en.md` | Step 7 | 单镜内容字段骨架（DeepSeek 填这个） |
| `cover-prompt.md` | Step 7b | 封面主视觉提示词（无字 · gptsapi） |
| `cover-design.md` | Step 7b | 封面本地排版规格（PIL 文字层 · 唯一规格源） |
| `publish-brief.md` | Step 10 | 发布物料简报 |
| `baoyu-image-gen-EXTEND.md` | 安装 | 拷到仓库根 `.baoyu-skills/baoyu-image-gen/EXTEND.md`，覆盖用户级默认值 |

### 参考（`references/`，11 个）

| 参考 | 内容 |
|------|------|
| `tool-usage.md` | 工具与认证管理红线、LLM 分工表、生图通道分工 |
| `deai-checklist.md` | 口播稿去 AI 味检查清单（A-D 共 20 项 + 人工判断 4 项） |
| `hyperframes-usage.md` | hyperframes 合成规范、seek-safe 动效规则、常见坑 |
| `video-style-guide.md` | **插画风格管理唯一控制源**（风格卡库 + 五色固定色板） |
| `shot-structure.md` | **结构唯一控制源**：7 段式 + 能量曲线 + 审美规则清单 |
| `subtitle-style.md` | 字幕层 / 金句层视觉规范 |
| `motion-recipes.md` | GSAP seek-safe 动效配方卡（5 类） |
| `sound-design.md` | BGM 选型、SFX 词汇表、钉帧方法 |
| `final-review.md` | 成片独立终检清单（干净上下文子 Agent 执行） |
| `book-category-playbook.md` | 心理励志垂类选题库与带货策略 |
| `xhs-publish-rules.md` | 小红书发布合规要点 |

---

## 架构

### 整体分层

```
┌─────────────────────────────────────────────────────────────────┐
│                    ZCode Agent（编排层）                          │
│   读 SKILL.md → 按步骤推进 → 7 个 AskUserQuestion 审核点          │
└──────────────┬───────────────────────┬──────────────────────────┘
               │                       │
   ┌───────────▼──────────┐ ┌──────────▼───────────────────────┐
   │   LLM 调用层          │ │      脚本 + 工具层                 │
   │  (scripts/*.py)       │ │  realign-shots / make-cues /     │
   │  kimi / deepseek /    │ │  check-script / validate-spec    │
   │  tts-minimax          │ │                                  │
   └───────┬──────────────┘ └──────────────┬───────────────────┘
           │                               │
   ┌───────▼──────────────────────────────▼───────────────────────┐
   │                    产 出 层（episodes/ep00X/）                 │
   │  01-profile/  02-script/  03-assets/  04-video/  05-publish/   │
   └───────────────────────────────┬──────────────────────────────┘
                                   │
                ┌──────────────────▼──────────────────┐
                │      渲染层（hyperframes）            │
                │   HTML/CSS + GSAP → 逐帧 seek 渲染    │
                │   → output.mp4 + subtitle.srt         │
                └───────────────────────────────────────┘
```

### 每集目录结构

```
episodes/ep00X-书名/
├── run-manifest.json          # 运行状态追踪
├── 01-profile/
│   └── book-profile.md        # Step 1
├── 02-script/
│   ├── script-brief.md        # Step 2
│   ├── draft-01-kimi.md       # Step 3a
│   ├── review-01-grok.md      # Step 3b
│   ├── draft-03-reviewed.md   # Step 3c
│   ├── draft-04-final.md      # Step 3d
│   ├── SCRIPT.md              # Step 3e（锁定旁白）
│   ├── voiceover-text.txt     # Step 3e（TTS 输入）
│   ├── deai-checklist.md      # Step 3d（证据）
│   ├── shot-timing.json       # Step 5（真实时间轴）
│   ├── shots-input.json       # Step 5 输入
│   ├── subtitle-cues.json     # Step 6（字幕逐句）
│   ├── STORYBOARD.md          # Step 6（分镜含动效）
│   ├── motion-plan.md         # Step 8（动效方案）
│   ├── i2v-prompt-镜N.md      # Step 8a（i2v 提示词）
│   └── shot-list.md           # 旧式分镜（兼容）
├── 03-assets/
│   ├── scenes/shot_*.png      # Step 7（场景插画）
│   ├── cover/                 # Step 7b（封面）
│   │   ├── cover-final.png        # 3:4（小红书）
│   │   └── cover-final-9x16.png   # 9:16（抖音/视频号）
│   ├── audio/
│   │   ├── voiceover.wav      # Step 4（配音）
│   │   └── bgm.mp3            # Step 9b（背景音乐）
│   └── video/                 # i2v 输出（去音轨后）
├── 04-video/
│   ├── output.mp4             # Step 9（成片）
│   └── subtitle.srt           # Step 9（独立字幕）
├── 05-publish/
│   └── publish-brief.md       # Step 10（发布简报）
└── video/                     # hyperframes 工作目录
    ├── build.mjs              # GSAP 动效构建脚本
    ├── compositions/          # HTML 逐帧组合
    │   ├── main.html
    │   └── frames/
    ├── assets/                # 引用的图片/音频
    ├── index.html
    ├── hyperframes.json
    └── package.json
```

---

## 调用关系

### 数据流（按步骤的输入输出）

```
Step 1 选书档案 ──────────────────────► (审核点①)
        │
        ▼
Step 2 Kimi 文案策划 ──► script-brief ─► (审核点②)
        │
        ▼
Step 3a Kimi 起草 ─► draft-01
Step 3b grok 初审 ─► review-01（问题清单，不改稿）
Step 3c DeepSeek 二审 ─► draft-03 ─────► (内容定稿)
Step 3d humanizer-zh ─► draft-04 ─► SCRIPT.md
        │   └─ check-script.py（20 项必须全绿）
        ▼
Step 3e 锁定旁白 + voiceover-text.txt ─► (审核点③)
        │
        ▼
Step 4 MiniMax TTS ─► voiceover.wav ───► (审核点④)
        │
        ▼
Step 5 ffmpeg silencedetect + realign-shots.py
        │   └─ 从音频真实时长反推每镜 start/end
        ▼
        shot-timing.json
        │
        ├─► make-cues.py ─► subtitle-cues.json（字幕逐句）
        │
        ▼
Step 6 DeepSeek 分镜 ─► STORYBOARD.md ─► (审核点⑤)
        │   └─ duration 字段必须来自 shot-timing.json，不可估算
        ▼
Step 7 DeepSeek Flash 写 shot_*.scene.md（仅内容）
        │   └─ 风格卡（styles/*.md）拼在前面，模型不碰风格
        └─ genimage.py 分发（characters+charRef→Seedream，否则→gptsapi）─► scenes/shot_*.png ─► (审核点⑥)
        │
        ▼
Step 7b 封面本地合成 ─► cover-final.png + cover-final-9x16.png
        │   └─ cover-compose.py（底图模板 + 文字层，零 API，文字 100% 保真）
        ▼
Step 8 动效设计
   ├─ 8a 即梦 i2v（≤2 镜，seedance-prompt-zh 写词 → dreamina CLI → 剥离 BGM）
   └─ 8b GSAP 动效层（其余所有镜头，seek-safe）
        │
        ▼
Step 9 hyperframes 合成 ─► output.mp4 + subtitle.srt ─► (审核点⑦)
        │   └─ validate-spec.py 校验规格
        ▼
Step 9b ego-browser 下 BGM ─► bgm.mp3 ──► (审核点⑦b)
        │
        ▼
Step 10 发布物料 ─► publish-brief.md
```

### LLM 分工表

| 步骤 | 模型 | 用途 |
|------|------|------|
| Step 1 / 10 | GLM-5.2 | 选书档案、发布物料、流程编排 |
| Step 2 / 3a | Kimi K3 (`kimi-k3`) | 文案策划、口播稿起草 |
| Step 3b | grok CLI | 口播稿初审（只出问题清单，不改稿） |
| Step 3c / 6 | DeepSeek V4 Pro (`deepseek-v4-pro`) | 二审修复、分镜（思考模式） |
| Step 7 | DeepSeek V4 Flash (`deepseek-v4-flash`) | 插画提示词（非思考模式） |
| Step 3d | humanizer-zh skill | 去 AI 味收尾（唯一减法工序，只删不加） |
| Step 7 | gptsapi (GPT Image 2) | 主角定妆图 + 无主角镜头（中文渲染好、风格质量最高） |
| Step 7 | dreamina Seedream 5.0 | 主角镜头（image2image，带定妆图 ref，角色+风格双锁） |
| Step 7 | MiniMax `image-01` | 备用参考图通道（baoyu-image-gen 触发，对 anime 锁定弱） |
| Step 7 | grok CLI (image_gen) | 备选生图后端（pipeline.yaml 可切，走订阅） |
| Step 4 | MiniMax T2A v2 (`speech-02-hd`) | 配音（音色库选 + 用户审核） |
| Step 8a | seedance-prompt-zh + dreamina CLI | i2v 真动画 |

### 外部 Skill 调用

本流水线在 ZCode 中会调用以下外部 Skill：

| Skill | 触发点 | 作用 |
|-------|--------|------|
| `humanizer-zh` | Step 3d | 口播稿去 AI 味收尾 |
| `ai-content-pipeline` | Step 7 | 通过 `gptsapi_image.py` 生图（默认通道） |
| `baoyu-image-gen` | Step 7 | 参考图生图（有 `ref` 时由 `genimage.py` 自动路由） |
| `seedance-prompt-zh` | Step 8a | 生成符合 Seedance 2.0 规范的 i2v 提示词 |
| `ego-browser` | Step 9b | 浏览器下载 pixabay BGM（绕过 Cloudflare） |

### 认证读取链

```
脚本 get_api_key()
   ├─ 1. 环境变量（$KIMI_API_KEY / $DEEPSEEK_API_KEY / ...）
   ├─ 2. ~/.zshrc 中的 export 行
   └─ 3. gptsapi 专属：<cwd>/.baoyu-skills/.env → ~/.baoyu-skills/.env

❌ 项目内任何文件都不存储 key
❌ 不读取 ~/.grok/auth.json（grok CLI 已退出主流程）
```

---

## 规格红线

所有成片必须满足：

| 项目 | 规格 |
|------|------|
| 分辨率 | 1080×1920（竖屏 9:16） |
| 帧率 | 30 fps CFR |
| 视频编码 | H.264 High@4.0 |
| 音频编码 | AAC 48kHz |
| 时长 | ≤ 200 秒（intro + 正文 + outro，单镜 ≤ 15 秒） |
| 字幕 | 金黄 #FFD700、黑描边、底部 1/3（数值见 `templates/video-spec.md`） |
| 音量 | 旁白 1.0、BGM 0.15（不盖人声） |
| 片头片尾 | 静音（`-an` 去除原视频背景音） |

**内容红线**：无医疗承诺、无绝对化、无投资收益承诺、不诱导导流私域。心理健康话题不诊断、不承诺治愈，严重情况引导寻求专业帮助。

---

## License

本项目为私有内容生产工具链。
