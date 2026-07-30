# 场景插画提示词组织方式

> **风格唯一控制源是 `references/video-style-guide.md`。**
> 本文件说明提示词怎么拼、谁写哪部分，不重复定义风格。

## 核心原则：风格是常量，不是每次生成的内容

提示词由两个文件**拼接**而成，用 `--promptfiles` 按顺序传入：

```
templates/style-prefix.en.md        ← 风格常量。逐字节相同，跨镜跨集不变
03-assets/scenes/shot_00X.scene.md  ← 当镜内容。DeepSeek 只写这部分
```

**为什么这么做**：早期让 DeepSeek 每镜连风格带内容一起写，风格描述每次都被重新
"翻译"一遍，措辞和色值会漂。ep001 实测——试验版提示词用的是 style guide 里那
五个 hex，正式版却出现了 `#8B6F52` `#7A93A8` `#D4E4EC` 三个表外色值，五个里
变了三个。改成常量拼接后，风格段落物理上不可能漂。

## 分工

| 部分 | 谁产出 | 内容 |
|------|--------|------|
| `style-prefix.en.md` | 人工，从 `video-style-guide.md` 派生 | 媒介、笔触、色板五色、人物造型、构图留白、禁止项 |
| `shot_00X.scene.md` | DeepSeek V4 Flash 按分镜写 | Scene / Subject / Props / Emotion / Tone |

DeepSeek 的 system prompt 必须明确：**只写画面内容，不要写风格、不要写色值、
不要写画幅和禁止项**——那些已经在前缀里了，重复写反而可能与前缀冲突。

单镜内容文件的字段骨架见 `templates/scene-content.en.md`。

## 生成

统一入口 `scripts/genimage.py`，按有无 `--ref` 自动路由后端：

```bash
# 单张（先跑 1 张确认风格，再批量 —— 审核点⑥）
python3 scripts/genimage.py \
  --promptfiles templates/style-prefix.en.md 03-assets/scenes/shot_002.scene.md \
  --image 03-assets/scenes/shot_002.png --ar 9:16

# 批量并发
python3 scripts/genimage.py --batchfile 03-assets/scenes/batch.json --jobs 3
```

`batch.json` 的 `stylePrefix` 字段会自动插到每个 task 的 promptFiles 最前面，
不用每条都写（路径相对 batch.json 所在目录解析）：

```json
{
  "jobs": 3,
  "stylePrefix": "../../../book-video-pipeline/templates/style-prefix.en.md",
  "tasks": [
    {"id": "shot_002", "promptFiles": ["shot_002.scene.md"],
     "image": "shot_002.png", "ar": "9:16"},
    {"id": "shot_007", "promptFiles": ["shot_007.scene.md"],
     "image": "shot_007.png", "ar": "9:16", "ref": ["shot_002.png"]}
  ]
}
```

## 跨镜人物一致性

`video-style-guide.md` 要求"同一角色出现多次时形象一致"，但 gptsapi 接口
**不支持参考图**，靠文字描述压不住。需要一致性时给该镜加 `ref`，`genimage.py`
会自动切到 baoyu-image-gen + MiniMax 的 subject_reference 通道。

参考图纪律（摘自 baoyu-image-gen 的实践）：

- 参考图只用 2-4 张，太多会让流式后端不稳
- 提示词里要说明"参考图是同一个主体，保持其身份"，**不要**再写一长串外貌描述
  ——长描述会让模型照着描述**新造**一个相似的人，而不是保持参考图里那个
- 不要拿新生成的图当参考图（漂移会累积），除非明确需要

## 风格一致性检查

批量生成后逐张过：

- [ ] 五色色板内，无表外 hex
- [ ] 拼贴质感在（撕边/胶带/纸纹/水彩），非扁平矢量、非写实、非 3D
- [ ] 人物面部极简，靠姿态传情
- [ ] 底部 1/3 视觉安静，可叠字幕
- [ ] 无可读文字、无水印、无 UI
- [ ] 同一角色跨镜形象一致
- [ ] 尺寸 1080×1920，真 PNG（用 `file` 查，MiniMax 会回 JPEG）
