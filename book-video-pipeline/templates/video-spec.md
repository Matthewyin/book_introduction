# 视频技术规格（唯一参数源）

> **本文件是所有可变技术参数的唯一控制源。** 其它文档（subtitle-style.md /
> shot-structure.md / hyperframes-usage.md / SKILL.md / 脚本默认值）描述参数时
> 必须**引用本文件**，不得重述具体数值——改参数 = 改本文件一处。
>
> 改本文件后，逐项检查「引用登记表」里的下游文件是否需要同步。

## 强制规格

| 项目 | 规格 | 容差 |
|------|------|------|
| 容器格式 | MP4 | — |
| 视频编码 | H.264 (libx264) | — |
| 音频编码 | AAC | — |
| 宽度 | 1080 px | ±0 |
| 高度 | 1920 px | ±0 |
| 帧率 | 30 fps | ±0 |
| 像素长宽比 | 1:1 (SAR 1:1) | — |
| 色彩空间 | yuv420p | — |
| 视频码率 | 5000 kbps | ±500 |
| 音频采样率 | 48000 Hz | — |
| 音频码率 | 192 kbps | — |
| 声道 | 立体声（stereo） | — |
| 最大时长 | 245 秒 | 硬上限（intro + 正文弹性上限 + outro） |
| 目标时长 | 199-244 秒 | 基线 ~199s / 弹性上限 ~244s |

## 时长结构

| 段落 | 基线 | 弹性上限 |
|------|------|----------|
| 片头 `intro.mp4` | **1.0s** | 1.0s |
| 正文 | ~195s | ~240s |
| 片尾 `outro.mp4` | **3.2s** | 3.2s |
| **合计** | **~199s** | **~244s** |

> 片头片尾时长来自 `assets/brand/intro.mp4` / `outro.mp4` 的真实时长（ffprobe 实测）。
> 正文段内结构（8 段螺旋：钩子+引入书/场景/分析/方案/总结/引导）的时长分配见 `references/shot-structure.md`。
> **弹性档**需段间钩子全部通过审核点③后才解锁，否则按基线 ~195s。

### 正文内部分配建议（8 段螺旋结构）

```
钩子+引入书  12s   ( 6%)   段1
场景1+钩子   18s   ( 9%)   段2
分析+钩子    20s   (10%)   段3
方案1+新场景  40s   (21%)   段4
方案2+新场景  45s   (23%)   段5
方案3        30s   (15%)   段6
总结对照     20s   (10%)   段7
引导评论     10s   ( 5%)   段8
─────────────────────
合计        195s   (+ intro 1.0s + outro 3.2s = ~199s)

弹性上限     240s   (+ 4.2s = ~244s，需钩子审核通过）
```

## 字幕规格（唯一源）

> 字幕撰写规范见 `references/subtitle-style.md`，合成层 scrim 见
> `references/hyperframes-usage.md`——那些文件描述用法，**具体数值以本表为准**。

| 项目 | 值 | 说明 |
|------|-----|------|
| 格式 | ASS + hyperframes 独立图层 | 双轨：图层渲染 + 独立 SRT |
| 字体 | Noto Sans CJK SC Bold | 思源黑体 |
| 字号 | **48px** | 早期用 58/52 偏大，压缩画面，已收窄 |
| 颜色 | `#FFD700`（金黄） | ASS 编码 `&H0000D7FF`（BGR 倒序） |
| 描边 | 黑色，**3.5px** | `OutlineColour=&H00000000,Outline=3.5` |
| 阴影 | 黑色，1px，偏移 1px | |
| 对齐 | 底部居中（Alignment=2） | |
| 底部边距 | **190px**（约画面下 1/3） | ASS `MarginV=190` |
| 每行最大字数 | **≤16 字** | 超长换行 |
| 每条最长显示 | 4 秒 | |

### 字幕可读性：scrim 渐变层

生图不强制底部留白（见 `references/video-style-guide.md`）。字幕可读性由合成层
底部渐变 scrim 保证（320px 高，底部 0.55 不透明度渐变到透明）。
scrim spec 见 `references/hyperframes-usage.md`。

### 金句层（独立于字幕层）

| 层 | 字体 | 字号 | 颜色 | 位置 |
|----|------|------|------|------|
| 金句 ink（书页/概念镜） | 宋体/楷体 | 46px | 深墨 `#2e1f10` | 画面中上部 |
| 金句 note（实景镜） | 黑体 | 40px | 白 `#fff` + 黑描边 3px | 画面角落 |

金句字号均小于口播字幕（48px），不抢主次。详见 `references/subtitle-style.md`。

## 音频规格

| 项目 | 值 |
|------|-----|
| 旁白音量 | 1.0（基准） |
| BGM 音量 | 0.15（不盖人声） |
| BGM 淡入/淡出 | 1s / 2s |
| 片头片尾 | 静音（`-an` 去除原视频背景音） |

## 配音（TTS）规格

> 音色库：`assets/voices/voice-library.json`（仓库根 `assets/voices/`，非 skill 内）。
> 当前 approved 音色均为 **speed 1.1x**。

| 项目 | 值 |
|------|-----|
| provider | MiniMax T2A v2 |
| model | `speech-02-hd` |
| 音色语速 | **1.1x**（danya_xuejie / female-yujie 两个 approved 音色都是） |
| 采样率 | 32000 Hz（MiniMax 返回）→ 48000 Hz（合成时重采样） |

## ffmpeg 合成参数参考

> 本项目本机 ffmpeg 缺 libass/libfreetype，字幕实际由 hyperframes 渲染。
> 下方 filter_complex 仅供离线调试参考，**不是主合成路径**。

```bash
ffmpeg \
  -framerate 30 \
  -i "scenes/shot_%03d.png" \
  -i "audio/voiceover.wav" \
  -i "audio/bgm.mp3" \
  -filter_complex "
    [0:v]scale=1080:1920,setsar=1,
    subtitles='subtitle.ass':force_style='FontName=Noto Sans CJK SC,FontSize=48,PrimaryColour=&H0000D7FF,OutlineColour=&H00000000,BorderStyle=1,Outline=3.5,Shadow=1,Alignment=2,MarginV=190'[v];
    [2:a]volume=0.15[bgm];
    [1:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[a]
  " \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset medium -crf 18 \
  -profile:v high -level 4.0 \
  -pix_fmt yuv420p \
  -b:v 5000k -maxrate 5500k -bufsize 10000k \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart \
  -t 200 \
  "output.mp4"
```

## 引用登记表

以下文件引用了本文件的参数。**改本文件后，检查这些下游文件是否仍与之一致**
（它们应改为引用描述，不重述数值）：

| 参数 | 下游引用文件 |
|------|-------------|
| 字幕字号/描边/边距/字数 | `references/subtitle-style.md`、`references/hyperframes-usage.md`、`references/shot-structure.md`、`templates/STORYBOARD-template.md` |
| 片头片尾时长 | `references/hyperframes-usage.md`、`scripts/realign-shots.py`、`templates/SCRIPT-template.md` |
| 配音语速/音色 | `SKILL.md` Step 4、`references/tool-usage.md`、`scripts/tts-minimax.py` |
| 视频编码/分辨率/时长上限 | `scripts/validate-spec.py` |

## 校验清单

产出视频后用 `validate-spec.py` 自动检查：

- [ ] 时长 ≤ 245s（基线 ~199s / 弹性上限 ~244s）
- [ ] 分辨率 = 1080×1920
- [ ] 帧率 = 30fps
- [ ] 编码 = H.264
- [ ] 音频 = AAC 48kHz 立体声
- [ ] 文件 < 100MB（便于上传）
- [ ] faststart 已启用
