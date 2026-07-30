# 场景插画提示词组织方式

> **风格控制源是 `references/video-style-guide.md` 定义的风格卡库 `templates/styles/`。**
> 本文件说明提示词怎么拼、谁写哪部分，不重复定义风格。

## 核心原则：风格是常量，不是每次生成的内容

提示词由两个文件**拼接**而成，用 `--style` / `--promptfiles` 按顺序传入：

```
templates/styles/people/cute-anime-girl.md  ← 风格卡常量。逐字节相同，跨镜跨集不变
03-assets/scenes/shot_00X.scene.md          ← 当镜内容。DeepSeek 只写这部分
```

**为什么这么做**：早期让 DeepSeek 每镜连风格带内容一起写，风格描述每次都被重新
"翻译"一遍，措辞和色值会漂。ep001 实测——试验版提示词用的是 style guide 里那
五个 hex，正式版却出现了 `#8B6F52` `#7A93A8` `#D4E4EC` 三个表外色值，五个里
变了三个。改成风格卡常量拼接后，风格段落物理上不可能漂。

## 风格卡库

风格卡放在 `templates/styles/`，按角色类型分目录：

```
templates/styles/
├── README.md                          # 风格库使用规则与审核流程
├── people/                            # 人物线
│   ├── cute-anime-girl.md             # 当前主力：日系软萌少女
│   └── cute-anime-girl.minimax.md     # MiniMax 专用精简版（备用通道，≤700 字符）
└── pets/                              # 萌宠线
    └── watercolor-cat.md              # 备用：水彩拟人猫
```

每张风格卡字段统一：媒介/笔触、五色色板、人物造型、构图（无强制留白）、禁止项。

## 分工

| 部分 | 谁产出 | 内容 |
|------|--------|------|
| 风格卡（`styles/*.md`） | 人工，从 `video-style-guide.md` 派生 | 媒介、笔触、色板五色、人物造型、构图、禁止项 |
| `shot_00X.scene.md` | DeepSeek V4 Flash 按分镜写 | Scene / Subject / Props / Emotion / Tone |

DeepSeek 的 system prompt 必须明确：**只写画面内容，不要写风格、不要写色值、
不要写画幅和禁止项**——那些已经在风格卡里了，重复写反而可能与风格卡冲突。

单镜内容文件的字段骨架见 `templates/scene-content.en.md`。

## 生成

统一入口 `scripts/genimage.py`，按镜头类型（`characters` + `charRef`）自动路由后端：

```bash
# 主角定妆图（gptsapi，无 ref）
python3 scripts/genimage.py \
  --style templates/styles/people/cute-anime-girl.md \
  --promptfiles 03-assets/scenes/_protagonist.scene.md \
  --image 03-assets/protagonist-ref.png --ar 9:16

# 含主角的镜头（dreamina Seedream，带定妆图 ref）
python3 scripts/genimage.py \
  --style templates/styles/people/cute-anime-girl.md \
  --promptfiles 03-assets/scenes/shot_002.scene.md \
  --image 03-assets/scenes/shot_002.png --ar 9:16 \
  --charRef 03-assets/protagonist-ref.png

# 无主角镜头（gptsapi，无 ref）
python3 scripts/genimage.py \
  --style templates/styles/people/cute-anime-girl.md \
  --promptfiles 03-assets/scenes/shot_005.scene.md \
  --image 03-assets/scenes/shot_005.png --ar 9:16

# 批量并发（charRef 自动挂到 characters:true 的 task）
python3 scripts/genimage.py --batchfile 03-assets/scenes/batch.json --jobs 3
```

`batch.json` 的 `style` 和 `charRef` 字段会自动插到对应位置，task 标 `characters` 控制
是否走 Seedream 通道（路径相对 batch.json 所在目录解析）：

```json
{
  "jobs": 3,
  "style": "templates/styles/people/cute-anime-girl.md",
  "charRef": "03-assets/protagonist-ref.png",
  "tasks": [
    {"id": "shot_002", "characters": true,
     "promptFiles": ["shot_002.scene.md"],
     "image": "shot_002.png", "ar": "9:16"},
    {"id": "shot_005", "characters": false,
     "promptFiles": ["shot_005.scene.md"],
     "image": "shot_005.png", "ar": "9:16"}
  ]
}
```

## 后端路由规则

`genimage.py` 三档路由：

| 条件 | 后端 | 原因 |
|------|------|------|
| `characters: true` + 有 `charRef` | dreamina image2image (Seedream 5.0) | 角色 + 风格双锁，实测优于 MiniMax |
| 有 `--ref`（无 charRef） | baoyu-image-gen + MiniMax | 备用通道，对 anime 锁定弱 |
| 无 characters / 无 ref | gptsapi + GPT Image 2 | 风格质量最高，中文渲染好 |

> ⚠️ MiniMax prompt 上限 1500 字符。若用 baoyu/MiniMax 备用通道，换 `*.minimax.md` 精简版风格卡。
> dreamina 通道无此限制。

## 跨镜角色一致性

`video-style-guide.md` 要求"同一角色出现多次时形象一致"，通过**定妆图 + Seedream ref** 实现：

1. **定妆图先行**：每集先用 gptsapi 生 1 张主角标准像（`protagonist-ref.png`），定义角色锚点。
2. **主角镜头全程挂 ref**：所有含主角的镜头走 dreamina image2image，挂定妆图当参考图，
   Seedream 锁定角色身份 + 风格。
3. **纪律**（来自 baoyu-image-gen 实践）：
   - ref 只用定妆图，**不拿生成图当 ref**（漂移累积）
   - 提示词写「Use the person in the reference image as the same identity. Do not redesign」
   - **不写长篇外貌描述**——长描述会让模型照描述新造一个相似的人，而不是保持参考图里那个

## i2v 关键帧一致性

i2v（dreamina image2video）的首帧就是静帧。为保证 i2v 输出与周围静帧角色同源：

- **首帧必须是 Seedream 通道生成的图**（带定妆图 ref），不要用 gptsapi 单独生的图
- seedance 提示词里写「参考 @图片1 的人物形象，严格保持角色五官、发型、服装一致」

## 构图：无强制留白

生图不要求底部留白。主体可充满整个 9:16 画面。字幕可读性由 hyperframes 合成层的
底部渐变 scrim 保证（详见 `references/hyperframes-usage.md`），不依赖生图留空。

## 风格一致性检查

批量生成后逐张过：

- [ ] 五色色板内，无表外 hex
- [ ] 风格质感在（按风格卡描述），非写实、非 3D
- [ ] 主角形象跨镜一致（五官/发型/服装跟随定妆图）
- [ ] 无可读文字、无水印、无 UI
- [ ] 真 PNG（用 `file` 查，MiniMax 会回 JPEG；genimage.py 已自动 sips 转换）
