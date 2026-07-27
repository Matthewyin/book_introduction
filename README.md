# 心理励志图书带货视频流水线

把一本书变成一条 1080×1920、≤180 秒的竖屏带货视频。

从小红书心理励志垂类出发，用 **AI 拼贴插画 + 配音 + 字幕 + 动效** 的方式，按确定性流程批量生产图书带货视频。流水线带 **7 个人工审核点**，每步停下等你确认。

视觉风格：**拼贴 / 剪贴簿叙事插画**（layered paper, torn edges, washi tape, watercolor washes）。

> 完整的安装、使用、组件、架构与调用关系文档见 **[`book-video-pipeline/README.md`](book-video-pipeline/README.md)**。

## 目录结构

```
video/
├── README.md                          本文件（项目入口）
├── config.yaml                        全局配置（账号、视频规格、视觉风格）
│
├── book-video-pipeline/               视频流水线（ZCode Skill）
│   ├── README.md                      ← 详细文档（安装/使用/架构）
│   ├── SKILL.md                       Skill 入口与 10 步工作流
│   ├── scripts/                       7 个 Python 脚本（LLM 调用 / 时间轴 / 校验）
│   ├── templates/                     8 个产出模板
│   └── references/                    9 份规范（去 AI 味 / 风格 / 合规等）
│
├── assets/                            全局素材
│   ├── brand/{intro,outro}.mp4        品牌片头片尾（已去音轨）
│   ├── voices/                        音色素材库
│   └── bgm/candidates/                BGM 候选
│
└── episodes/                          每集视频工作目录
    └── ep001-被讨厌的勇气/
        ├── run-manifest.json          运行状态
        ├── 01-profile/                选书档案
        ├── 02-script/                 口播稿 + 分镜 + 时间轴
        ├── 03-assets/                 场景插画 + 配音 + BGM
        ├── 04-video/                  成片 + 字幕
        ├── 05-publish/                封面 + 发布简报
        └── video/                     hyperframes 渲染工作目录
```

## 视频规格

| 项目 | 规格 |
|------|------|
| 分辨率 | 1080×1920（竖屏 9:16） |
| 帧率 | 30fps CFR |
| 编码 | H.264 视频 + AAC 音频 |
| 时长 | ≤180 秒 |
| 画面 | AI 拼贴插画演绎书中场景 |
| 字幕 | 金黄 #FFD700、黑描边、底部 1/3、独立图层（不烧录） |
| 音频 | 旁白配音（MiniMax TTS）+ 背景音乐（音量 0.15） |
| 渲染 | hyperframes（HTML/CSS + GSAP 逐帧 seek 渲染） |

## 工作流（10 步，带 7 个审核点）

| 步骤 | 产出 | 负责 | 审核点 |
|------|------|------|--------|
| 0. 片头片尾 | `brand/{intro,outro}.mp4` | ffmpeg（一次性） | — |
| 1. 选书 | `book-profile.md` | GLM-5.2 | 🔴 ① |
| 2. 文案策划 | `script-brief.md` | Kimi K3 | 🔴 ② |
| 3. 口播稿四道工序 | `SCRIPT.md` | Kimi→grok→DeepSeek→humanizer-zh | 🔴 ③ |
| 4. TTS 配音 | `voiceover.wav` | MiniMax T2A v2 | 🔴 ④ |
| 5. 真实时间轴 | `shot-timing.json` | `realign-shots.py` | — |
| 6. 分镜 | `STORYBOARD.md` | DeepSeek V4 Pro | 🔴 ⑤ |
| 7. 生图 | `scenes/shot_*.png` | gptsapi（GPT Image 2） | 🔴 ⑥ |
| 8. 动效设计 | `motion-plan.md` | GSAP / 即梦 i2v | — |
| 9. 合成 | `output.mp4` + `subtitle.srt` | hyperframes | 🔴 ⑦ |
| 9b. BGM | `bgm.mp3` | ego-browser → pixabay | 🔴 ⑦b |
| 10. 发布物料 | `publish-brief.md` + `cover.png` | GLM-5.2 | — |

**顺序铁律**：配音必须在分镜和生图之前定稿——音频的真实时长是分镜的输入，不是产物。

## 技术依赖

| 能力 | 工具 |
|------|------|
| 流程编排 + 审核 | ZCode CLI（加载 `book-video-pipeline` Skill） |
| 文案 / 审稿 / 分镜 | Kimi K3、DeepSeek V4 Pro/Flash、grok CLI |
| 口播去 AI 味 | `humanizer-zh` skill + `check-script.py` |
| AI 图片生成 | gptsapi / GPT Image 2（via `ai-content-pipeline`，中文渲染优） |
| i2v 真动画 | 即梦 `dreamina` CLI（Seedance 2.0，每集 ≤2 镜） |
| 配音 | MiniMax T2A v2 |
| 视频渲染 | hyperframes（HTML/CSS + GSAP） |
| 音频处理 / 规格校验 | ffmpeg / ffprobe |

安装与 API 密钥配置详见 [`book-video-pipeline/README.md`](book-video-pipeline/README.md#安装)。
