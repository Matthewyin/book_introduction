---
format: 1080x1920
message: "{{一句话主旨，例：把别人的情绪还给别人}}"
arc: 钩子 → 扎心场景 → 引入书 → 场景演绎 → 观点拆解 → 方法实操 → 结尾引导
audience: {{目标受众，例：20-35 岁讨好型人格女性}}
book: "{{书名}}"
voice: {{voice_id}}
audio: 03-assets/audio/voiceover.wav
audio_duration: {{真实总时长}}s
style: {{视觉风格，例：日系软萌 anime 水彩}}
---

> Step 6 产出。格式对齐 hyperframes `hyperframes-core/references/storyboard-format.md`。
> **所有 `duration` 必须来自 `02-script/shot-timing.json` 的真实值，不得估算。**

## Frame 1 — {{帧标题}}

- duration: {{4.878}}s
- transition_in: cut
- camera: static
- scene: {{一行画面摘要}}
- voiceover: "{{该帧旁白原文}}"
- subtitle_cues:
    - { text: "{{字幕第一条}}", start: 0.0, end: 2.4 }
    - { text: "{{字幕第二条}}", start: 2.4, end: 4.878 }
- layers: [bg:shot_001.png, subtitle, grain]
- src: compositions/frames/01-hook.html
- status: outline

{{自由描述：这一帧要传达什么情绪，为什么这么设计}}

## Frame 2 — {{帧标题}}

- duration: {{9.344}}s
- transition_in: crossfade 0.6s
- camera: ken-burns-in（scale 1.0 → 1.08，锚点中心偏上）
- scene: {{一行画面摘要}}
- voiceover: "{{该帧旁白原文}}"
- subtitle_cues:
    - { text: "{{字幕}}", start: 0.0, end: 4.5 }
    - { text: "{{字幕}}", start: 4.5, end: 9.344 }
- layers: [bg:shot_002.png, subtitle, grain]
- src: compositions/frames/02-scene.html
- status: outline

{{自由描述}}

<!-- 按镜头数量继续 -->

---

## 字段说明

| 字段 | 取值 | 说明 |
|------|------|------|
| `duration` | 秒（三位小数） | **必须来自 shot-timing.json**，与音频严格对齐 |
| `transition_in` | `cut` / `crossfade Xs` / `wipe Xs` | 首帧固定 `cut`；默认 `crossfade 0.6s`；不用花哨特效 |
| `camera` | `static` / `ken-burns-in` / `ken-burns-out` / `pan-left` / `pan-right` | 需注明起止缩放比和锚点 |
| `scene` | 一行 | 联系表缩略图的说明文字 |
| `voiceover` | 该帧旁白原文 | 与 SCRIPT.md 对应行一致 |
| `subtitle_cues` | 数组 | 逐条字幕 + 帧内相对时间码；每条字数/每行字数以 `templates/video-spec.md` 为准，最少 1.2s |
| `layers` | 数组 | 从下到上的图层顺序 |
| `src` | 路径 | 该帧的 HTML 子组合 |
| `status` | `outline` → `built` → `animated` | 制作进度 |

## 镜头运动规范

| 段落 | 推荐运动 | 理由 |
|------|----------|------|
| 钩子 | `static` 或极缓 `ken-burns-in`（1.0→1.03） | 留白，让文字先落地 |
| 扎心场景 | `ken-burns-in`（1.0→1.08） | 缓慢推进，加压迫感 |
| 引入书 | `ken-burns-out`（1.08→1.0） | 拉开，情绪转暖 |
| 观点拆解 | `static` 或 `pan` | 稳住，让观点被听清 |
| 方法实操 | `ken-burns-in` 轻推 | 聚焦动作细节 |
| 结尾 | `ken-burns-out` 缓拉 | 放开，收束 |

**约束**：单帧运动幅度 ≤8%，速度恒定不加速；相邻两帧不用同向运动，避免晕眩。

## 转场规范

| 类型 | 用法 | 时长 |
|------|------|------|
| `cut` | 仅首帧 | 0 |
| `crossfade` | 默认转场 | 0.6-1.0s |
| `wipe` | 段落切换（如从痛点转到方法） | 0.8s |

不用缩放、旋转、滑动等花哨特效，保持沉稳叙事感。
