---
name: book-video-pipeline
description: 心理励志图书带货视频流水线。当用户需要为心理励志类图书制作小红书带货视频时触发，覆盖从选书、文案、口播稿、分镜、素材生成到视频合成的完整流程。视频规格：1080×1920 竖屏，≤200 秒，AI 插画 + 黄字字幕 + 旁白配音风格。工作流带 7 个审核点，每步停下等用户确认。
---

# 心理励志图书带货视频流水线

从小红书心理励志垂类出发，批量生产日系软萌 anime 水彩叙事插画风格的图书带货视频。当前主力风格卡：`templates/styles/people/cute-anime-girl.md`。

参考标杆：`ep001-v3-v9-jimeng-release-75mb.mp4`（1080×1920，119s；早期采用拼贴 / 剪贴簿插画，现已迁移至日系软萌 anime 水彩，见风格卡库 `templates/styles/`）。

## 核心姿态

扮演心理励志图书带货视频的内容策划+制作总监。把一本书转成一条 200 秒以内的带货视频，覆盖选书、文案、口播、分镜、素材、合成、发布全流程。

不承诺播放量、粉丝数或成交额。把"爆款""月入XX万"视为动机表达，不当作保证。涉及心理健康话题时，先做表达安全检查。

**工作流带 7 个审核点**：每个 🔴 审核点必须用 `AskUserQuestion` 弹出"通过/修改/重做"选项，等待用户确认后才继续。绝不跳过。

## 认证管理红线（不可违反）

**生图认证原则**：

- 生图统一走 `scripts/genimage.py`（薄分发层），它按镜头类型路由到三个后端：
  `gptsapi_image.py`（无主角 / 定妆图）、`dreamina image2image`（Seedream 主角镜头）、
  `baoyu-image-gen`（备用 MiniMax）。API key 从 `GPTSAPI_KEY` / `MINIMAX_API_KEY` 环境变量
  或 `.baoyu-skills/.env` 读取；dreamina 用 OAuth 登录（`dreamina login`），不读 API key。
  **项目不硬编码、不缓存 key**。
- **grok CLI 为配置可选的备选生图后端**：在 `pipeline.yaml` 的 `image.backends.grok` 启用即可切换（gptsapi 仍为默认后端）。启用时遵循订阅继承原则：用 `--always-approve` 走订阅，不读取 `~/.grok/auth.json`、不缓存 token。
- Kimi / DeepSeek / MiniMax key 均从环境变量或 shell profile 读取，项目不存储。
- **配置化**：所有模型 / endpoint / 生图后端的选择统一读 `pipeline.yaml`（由 `scripts/config.py` 加载）；API key 仍只走环境变量，不写入 `pipeline.yaml`。

详见 `references/tool-usage.md`。

## 必读参考

开始任何实质操作前，根据当前阶段读取对应参考：

| 阶段 | 参考文件 |
|------|----------|
| 工具与认证规范 | `references/tool-usage.md` |
| **口播稿去 AI 味（Step 3d 必读）** | `references/deai-checklist.md` |
| **插画风格唯一控制源** | `references/video-style-guide.md` |
| **生图提示词组织（Step 7 必读）** | `templates/scene-prompt.md` |
| 音色选择 | `assets/voices/README.md` + `assets/voices/voice-library.json` |
| 选书与选题 | `references/book-category-playbook.md` |
| 分镜结构设计 | `references/shot-structure.md` |
| 字幕撰写 | `references/subtitle-style.md` |
| 视频合成与动效 | `references/hyperframes-usage.md` |
| **动效配方卡（Step 8 必读）** | `references/motion-recipes.md` |
| **声音设计（Step 8/9 必读）** | `references/sound-design.md` |
| **成片独立终检（Step 9 必读）** | `references/final-review.md` |
| 发布合规 | `references/xhs-publish-rules.md` |
| 视频技术规格 | `templates/video-spec.md` |

## 工作流程（10 步，带 7 个审核点）

### 顺序铁律（不可颠倒）

**配音必须在分镜和生图之前完成。** 音频的真实时长和逐句时间戳是分镜的输入，不是产物。颠倒顺序的后果：换音色 → 时长变化 → 时间轴全废 → 字幕重烧 → 视频重合成。

```
口播稿 → TTS 定稿 → 从音频提取真实时间轴 → 分镜（含动效字段）→ 生图 → hyperframes 合成
```

### Step 0：片头片尾 + 品牌角标（一次性，已完成）

准备以下品牌素材，放置于 `assets/brand/` 目录：

| 素材 | 文件 | 说明 |
|------|------|------|
| 片头 | `intro.mp4`（1.0s） | 视频开头，播放品牌卡片 |
| 片尾 | `outro.mp4`（3.2s） | 视频结尾，含品牌动画 |
| 品牌角标 | `corner-lockup.png` | 播放时显示在视频左上角的 logo（透明背景 PNG） |

**必须去除片头条片尾音轨**（`-an`），否则会带入原片背景音。

**品牌角标显示规则**：
- 视频播放期间，`corner-lockup.png` 持续显示在左上角
- 位置：距左 40px，距上 40px
- 尺寸：200×50px（保持原始 4:1 宽高比）
- 不透明度：0.85，不抢画面主体
- 背景透明，叠加在视频画面内容上
- 使用 GSAP `x/y` transform 定位（禁用 `left/top`，避免像素闪烁）
- logo 元素需加 `class="clip"` 以被运行时正确控制可见性

### Step 1：选书 + weread 数据采集 → `01-profile/book-profile.md`

1. 从 `references/book-category-playbook.md` 选题库选书，或接受用户指定。
2. **调用 `weread-skills` 获取真实读者数据**（数据驱动选角度）：
   - **书籍点评**（`review.md`）：获取读者书评，提取痛点关键词和高频共鸣反馈
   - **章节热门划线**（`notes.md`）：获取最打动读者的金句，用于观点拆解段
3. 基于读者数据 + 书本内容，提炼 3 个带货角度（不再凭经验编造）。
4. 用 `templates/book-profile.md` 模板填写选书档案，"三大带货角度"必须标注数据来源。
5. 评估带货潜力（话题热度、搜索需求、视觉可演绎性）。
6. **🔴 审核点①**：用 AskUserQuestion 确认书和带货角度。

### Step 2：Kimi K3 文案策划 → `02-script/script-brief.md`

1. 从 book-profile 的 3 个带货角度中选定 1 个。
2. 调用 **Kimi K3**（`KIMI_API_KEY`，base URL `https://api.kimi.com/coding/`）生成：视频主题、开头钩子（≤20字）、3-5 个核心观点和金句、行动引导话术。
3. 用 `templates/script-brief.md` 记录。
4. **🔴 审核点②**：用 AskUserQuestion 确认钩子和观点方向。

### Step 3：口播稿四道工序 → `02-script/SCRIPT.md`

口播稿是全片的地基，必须走完四道工序才能提交人工审核。**任何一道都不能跳过，顺序也不能换。**

```
Kimi K3 起草 → grok 初审 → DeepSeek V4 Pro 二审 → humanizer-zh 去AI味（收尾）→ 🔴 人工审核
```

**为什么 humanizer-zh 必须放最后**：它是唯一一道"减法"工序。任何 LLM 在它之后改稿，都会重新引入 AI 腔——补上"想到这儿，心里是不是一下子轻了"这类替观众下结论的句子、写回工整的对照结构、加回空泛的收束。去 AI 味之后不许再让模型改写。

#### 3a：Kimi K3 起草

1. 调用 **Kimi K3** 基于审核通过的文案策划，写完整口播稿（≤570字，正文≤195秒，1.1 倍速配音）。
2. 结构：钩子 → 扎心场景 → 引入书 → 场景演绎 → 观点拆解 → 方法实操 → 结尾引导。
3. 产出 `02-script/draft-01-kimi.md`。

#### 3b：grok 初审（只出问题清单，不改稿）

1. 用 `~/.grok/bin/grok --prompt-file <审稿要求> --always-approve` 做第一轮审稿。
2. 审查重点：
   - **说教感**：`第一/第二/第三/第四` 这类编号罗列是否像在上课
   - **过渡生硬**：段落之间是否有断层，是否有"光说没用""说个场景"这类空转过渡
   - **重复**：同一手法（如"举个场景"）是否用了两次
   - **念不顺**：有没有拗口、绕、需要重读才懂的句子；有没有连续 ≥18 字无标点
3. 产出 `02-script/review-01-grok.md`。
4. grok 倾向于过度审查，第二人称"你"和痛点反复加深是带货口播的必要手法，不是缺陷——由下一步判断取舍。

#### 3c：DeepSeek V4 Pro 二审（结构与内容定稿）

1. 调用 **DeepSeek V4 Pro**（`deepseek-v4-pro`），输入 = 稿件 + grok 的问题清单。
2. 逐条判断并修复，明确拒绝过度审查的意见并说明理由。
3. 表达安全检查：无医疗承诺、无绝对化、无夸大、不贬低读者。
4. 长句检查：任何连续 ≥18 字无标点的句子必须拆开，否则字幕无法断行。
5. 产出 `02-script/draft-03-reviewed.md`。**此时结构和内容已定，后面只做减法。**

#### 3d：humanizer-zh 去 AI 味（收尾，最后一道）

**必读 `references/deai-checklist.md`**，它是本项目去 AI 味的唯一标准（融合了 humanizer-zh Core Rules 和公众号硬闸门，按口播场景重写）。

1. 调用 `humanizer-zh` skill 做**中立润色**，不套作者声音。
2. 按 checklist 的 A/B/C/D 四组逐条清理。
3. **只删不加**：字数只减不增，不补新句子，不改观点内容和顺序。缺内容退回 3a 重来。
4. 跑自动检查：
   ```bash
   python3 scripts/check-script.py 02-script/draft-04-final.md \
     --before 02-script/draft-03-reviewed.md
   ```
   覆盖 A1-A6、B1/B3、C1-C6、D1-D5、E。必须全绿才能继续。
5. 人工判断脚本查不了的四项：B2 空转过渡、B4 收束句式雷同、C3 朗读顺畅、D4 观点归属。
6. 把结果写入 `02-script/deai-checklist.md`，**每条给证据**（引用正文具体句子，禁止写"已优化"）。
7. 产出 `02-script/draft-04-final.md`。**这是定稿，此后不许再让任何模型改写。**

#### 3e：写成锁定旁白 + 人工审核

1. 按 `templates/SCRIPT-template.md` 写成**锁定旁白文件**（对齐 hyperframes `script-format.md`）：逐句分节、标注所属帧、预估时间窗、delivery 提示。
2. 同时产出单行纯文本 `voiceover-text.txt` 供 TTS 读取。
3. **🔴 审核点③**：用 AskUserQuestion 提交人工审核（最重要审核点）。附上四道工序各改了什么。

### Step 4：MiniMax TTS 配音（音色审核）→ `03-assets/audio/voiceover.wav`

**这一步必须在分镜和生图之前完成。**

1. **从音色素材库选候选**：读取 `assets/voices/voice-library.json`，在 `status: approved` 的音色中挑 1-2 个（当前库内：`danya_xuejie` 1.1x、`female-yujie` 1.1x）。语速/音色以库为准，见 `templates/video-spec.md`。
2. **生成试听样本**：用本集口播稿前 40-60 字生成样本（~10 秒），不得用库内旧样本冒充。
3. **🔴 审核点④**：用 AskUserQuestion 确认音色。
4. 通过后生成完整配音，记录实际总时长。
5. 新音色入库流程见 `assets/voices/README.md`。

### Step 5：从音频提取真实时间轴 → `02-script/shot-timing.json`

1. 用 ffmpeg `silencedetect` 检测自然停顿（`noise=-35dB:d=0.28`）。
2. 按各镜字符数比例分配时长，再把每个切点**吸附到最近的停顿中点**（容差 2.5s），确保切点落在句子之间。
3. 产出每镜的 `start` / `end` / `duration` / `chars` / 语速（字/秒），语速应落在 3.2–5.2 字/秒。
4. 脚本：`scripts/realign-shots.py`。

### Step 6：DeepSeek V4 Pro 分镜（含动效字段）→ `02-script/STORYBOARD.md`

1. 调用 **DeepSeek V4 Pro**（`deepseek-v4-pro`），输入 = 口播稿 + **Step 5 的真实时间轴**。
2. 用 `templates/STORYBOARD.md` 模板，每帧必须包含（对齐 hyperframes `storyboard-format.md`）：

   | 字段 | 说明 |
   |------|------|
   | `duration` | 来自 shot-timing.json 的真实时长，不是估算 |
   | `transition_in` | `cut` / `crossfade` / `wipe`，含时长 |
   | `camera` | 镜头运动：`static` / `ken-burns-in` / `ken-burns-out` / `pan-left` / `pan-right`，含起止缩放和位移 |
   | `scene` | 一行画面摘要 |
   | `voiceover` | 该帧旁白原文 |
   | `subtitle_cues` | 逐条字幕 + 各自起止时间码 |
   | `layers` | 图层结构（背景图 / 字幕层 / 装饰层） |
   | `src` | 该帧 HTML 子组合路径 |

3. **🔴 审核点⑤**：用 AskUserQuestion 确认画面描述和动效设计。

### Step 7：生图 → `03-assets/scenes/shot_*.png`

**风格控制源是风格卡库 `templates/styles/`**（见 `references/video-style-guide.md`）。
提示词 = 选定的风格卡（常量）+ 当镜内容，**拼接**而成，DeepSeek 只写内容那一半。
详见 `templates/scene-prompt.md`。

#### 7.0：风格选择 + 引用全局定妆图（每集第一步）

1. **选风格卡**：从 `templates/styles/` 选定本集风格（当前主力 `people/cute-anime-girl.md`）。
   展示风格卡给用户确认。
2. **🔴 审核点⑤b（风格确认）**：用 AskUserQuestion 确认风格卡。
3. **引用全局定妆图**：主角定妆图是**全局**资产，位于 `assets/protagonist-base/girl-ref.png`
   （941×1672，已就位），所有集共用，无需每集重生。向用户展示该全局定妆图以供确认。
   （这是一次性全局资产；若某集需要不同角色，才单独生成本集定妆图。）
4. **🔴 审核点⑤c（定妆确认）**：用 AskUserQuestion 确认全局定妆图适用本集
   （通常直接通过；除非本集需要不同角色才单独生）。

#### 7.1：写场景内容

1. 调用 **DeepSeek V4 Flash**（`deepseek-v4-flash`）按分镜为每镜写 `shot_00X.scene.md`，
   字段骨架见 `templates/scene-content.en.md`。
   **system prompt 必须约束：只写画面内容，不写风格、不写色值、不写画幅和禁止项**
   ——这些已在风格卡里，重复写会与风格卡冲突、导致色板漂移。
2. 同时为每镜标注 `characters: true/false`（是否含主角），用于 batch 路由。

#### 7.2：生成测试图

先生成 1 张含主角的测试图（走 Seedream 通道），确认角色锁定和风格一致：

```bash
python3 scripts/genimage.py \
  --style templates/styles/people/cute-anime-girl.md \
  --promptfiles 03-assets/scenes/shot_002.scene.md \
  --image 03-assets/scenes/shot_002.png --ar 9:16 \
  --charRef assets/protagonist-base/girl-ref.png
```

**🔴 审核点⑥**：用 AskUserQuestion 确认主角一致性 + 风格。通过后再批量。

#### 7.3：批量生成

```bash
python3 scripts/genimage.py --batchfile 03-assets/scenes/batch.json --jobs 3
```

batch.json 用 `style` + `charRef` 字段，task 标 `characters: true/false` 自动路由：

```json
{
  "jobs": 3,
  "style": "templates/styles/people/cute-anime-girl.md",
  "charRef": "assets/protagonist-base/girl-ref.png",
  "tasks": [
    {"id": "shot_002", "characters": true,
     "promptFiles": ["shot_002.scene.md"], "image": "shot_002.png", "ar": "9:16"},
    {"id": "shot_005", "characters": false,
     "promptFiles": ["shot_005.scene.md"], "image": "shot_005.png", "ar": "9:16"}
  ]
}
```

生成后逐张核对 `templates/scene-prompt.md` 末尾的一致性清单
（五色色板 / 风格质感 / 主角形象一致 / 真 PNG）。

**通道分工**（`genimage.py` 按 `characters` + `charRef` 自动路由）：

| 场景 | 后端 | 参考图 | 原因 |
|------|------|--------|------|
| 主角定妆图 | 全局已就位 `assets/protagonist-base/girl-ref.png`（无需每集生成） | ❌ | 一次性全局资产，所有集共用；仅当某集需要不同角色时才单独生成 |
| 含主角的镜头（`characters: true`） | dreamina image2image + Seedream 5.0 | ✅ 定妆图 | 角色 + 风格双锁（实测优于 MiniMax） |
| 无主角镜头（书封、抽象概念、纯环境） | gptsapi + GPT Image 2 | ❌ | 中文渲染好、质量高 |
| i2v 关键帧首帧 | dreamina image2image | ✅ 定妆图 | 保证 i2v 输出与静帧角色同源 |

### Step 8：动效设计 → `02-script/motion-plan.md`

画面不能是纯静帧配推拉，那 20 秒就让人想划走。每镜都要有动，但动的来源分两类，**成本差两个量级**：

| 方式 | 工具 | 成本 | 用在哪 |
|------|------|------|--------|
| **GSAP 动效层** | hyperframes（免费） | 0 | 默认。光束流动、尘埃浮动、纸张呼吸、热气升腾、影子起伏、光斑移动 |
| **i2v 真动画** | 即梦 `dreamina`（消耗积分） | 每条约 100-200 积分 | 只给 1-2 个仪式感最强的镜头 |

#### 8a：i2v 镜头规划（用量控制）

1. 先跑 `dreamina user_credit` 看余额。
2. **每集 i2v 镜头不超过 2 个**，选"动作本身就是内容"的镜头——书页翻开、门被推开这类。人物面部特写不适合，模型容易画崩；Seedance 还会直接拦截写实真人脸素材。
3. 时长 4-6 秒。口播比视频长时，**视频播完定格最后一帧**，叠 GSAP 轻微动效补足；不要慢放，会看出来。

#### 8a-1：提示词必须走 seedance-prompt-zh skill

**不要自己拍脑袋写 i2v 提示词。** 调用 `seedance-prompt-zh` skill（`~/.agents/skills/seedance2-skill-zh/SKILL.md`）撰写，它是即梦 Seedance 2.0 的官方提示词规范。

关键约定：

| 要点 | 规则 |
|------|------|
| 引用语法 | 用 `@图片1 作为首帧` 明确每个素材的用途，不能只丢一张图 |
| 结构公式 | `[主体设定] + [场景] + [动作] + [运镜] + [分时段] + [风格氛围]` |
| 分时段 | 10 秒以上必须按 `0–3秒 / 3–6秒 / …` 分段描述；5 秒可省略 |
| 运镜 | 用规范术语：慢推、后拉、左摇、固定镜头、一镜到底 |
| 风格保持 | **必须显式要求保持首帧画风**，否则模型会"优化"成写实 |
| 分辨率上限 | Seedance 2.0 输出 480p–720p，不要要求 1080p |

风格保持的写法（必写，按实际风格替换画风描述）：

```
严格保持 @图片1 的画风（软萌日系 anime 水彩），保持角色五官、发型、服装一致。
不要渲染成写实风格，不要加 3D 光影。
只让 <具体动作> 动起来，其余保持静止。固定镜头。
```

**首帧必须是 Seedream 通道生成的图**（带定妆图 ref），保证 i2v 输出与周围静帧角色同源。
不要拿 gptsapi 单独生的图当 i2v 首帧——会和 Seedream 帧的角色对不上。

产出写入 `02-script/i2v-prompt-镜N.md`，便于复查和复用。

#### 8a-2：调用即梦 CLI

```bash
dreamina image2video \
  --image=<首帧.png> \
  --prompt="<seedance-prompt-zh 写好的提示词>" \
  --model_version=seedance2.0fast_vip \
  --duration=5 \
  --video_resolution=720p \
  --poll=180
```

生成后**必须看片**确认风格没崩（anime 水彩质感是否被渲染成写实、角色形象是否偏离定妆图）。崩了就调提示词重来，不要将就。

**i2v 输出默认带 BGM/音效，必须剥离后再集成**：`ffmpeg -i input.mp4 -c:v copy -an output.mp4`。否则会污染全片旁白。

#### 8b：GSAP 动效层（其余所有镜头）

**必须 seek-safe**，否则渲染出来是卡住的静帧。硬性约束（详见 `references/hyperframes-usage.md`）：

- 动效写成 `gsap.timeline({ paused: true })` 上的 tween，注册到 `window.__timelines`
- 禁止 `repeat: -1`，循环次数算成有限值：`Math.max(0, Math.floor(duration / cycle) - 1)`
- 禁止 `Math.random()`、`Date.now()`、`setTimeout`；随机位置在**构建时**用固定种子算好，写死进 HTML
- 只动 `opacity` / `x` / `y` / `scale` / `rotation` / `color`，不碰 `display`、`visibility`
- 不要对 `.clip` 元素本身做动画，动它内部的包裹层

#### 8c：金句贴纸（与字幕层严格分离）

从书中摘句贴进画面，强化"这是书里说的"。**金句层与字幕层是两个独立图层**，使用不同的字体、字号和颜色。

- 每镜最多 1 句，与该镜口播内容对应
- **中文不靠 AI 生成**（AI 写中文常出错），用 hyperframes 文字层渲染
- 两种样式（背景均透明）：
  - **ink**（墨色，概念镜）：宋体/楷体，深墨色 `#2e1f10`，46px，**缩放弹入**：`scale 0.8→1` + `opacity 0→1`，0.8s，`back.out`
  - **note**（便签，实景镜）：黑体，白色 `#fff` + 黑描边 3px，40px，**上滑浮入**：`opacity 0→1` + `y 16→0`，0.7s，`power2.out`
- 字号均小于口播字幕（48px），不抢主次
- 位置在画面中上部，与底部字幕分离，不打架
- **⚠️ 背景必须透明**：金句文字不得带任何背景色块或底纹

### Step 9：hyperframes 合成 → `04-video/output.mp4`

**不烧录字幕**。字幕作为独立图层渲染，源文件可随时修改，同时导出独立 SRT。

1. 按 `references/hyperframes-usage.md` 搭建项目。
2. 图层顺序（下到上）：背景图/视频 → Ken Burns → 动效层 → 金句层 → **底部 scrim 层** → 字幕层 → 品牌角标层。
3. 字幕层与金句层严格分离（不同字体/字号/颜色，详见 `references/subtitle-style.md`）；scrim 保证字幕在任意背景上可读（见 `references/hyperframes-usage.md`）。
4. **帧间转场**：交叉淡入淡出（每帧 bg 层 `opacity` 动画，0.6s，`power1.inOut`）；首帧不淡入；i2v 视频帧不参与。
5. 字幕/金句/片头片尾的具体数值以 `templates/video-spec.md`（唯一参数源）为准。
6. 音轨：旁白 + BGM（BGM 音量 0.15，不盖人声）。
7. 拼接 `intro.mp4`（静音）+ 正文 + `outro.mp4`（静音）。
8. 总时长 ≤200s（intro + 正文 + outro），单镜不超过 15 秒——超了就拆镜或换画面。
9. 产出 `output.mp4` + `subtitle.srt`。
10. `npx hyperframes lint` 和 `check` 必须 0 错误，再 `render`。
11. 运行 `scripts/validate-spec.py output.mp4` 校验规格。
12. **独立终检**：派一个干净上下文的 subagent，按 `references/final-review.md` 逐项审查（结构一致性、视觉质量、音频节奏、技术规格、去AI味与安全）。每条结论附帧号证据。**制作者有确认偏差，首检不能交给用户。** 必须修复项清零后才提交审核点⑦。
13. **🔴 审核点⑦**：用 AskUserQuestion 确认成片。

### Step 9b：BGM → `03-assets/audio/bgm.mp3`

> pixabay 等免费音乐站有 Cloudflare 挑战，curl/wget 拿不到，**必须用 ego-browser 浏览器下载**。

1. 用 `ego-browser` skill 打开 `https://pixabay.com/zh/music/`，搜索关键词（推荐：`calm piano`、`ambient soft`、`lo-fi quiet`）。
2. 筛选条件：
   - 许可：pixabay 自有许可（可商用、无需署名）
   - 时长：≥ 视频总时长（≥120s），或可循环
   - 风格：轻钢琴/氛围乐/lo-fi，无歌词、无强鼓点
   - 情绪：安静、温暖、不抢旁白
3. 下载 2-3 首候选到 `assets/bgm/candidates/`。
4. **🔴 审核点⑦b**：用 AskUserQuestion 让用户试听选定。
5. 选定后复制到 `episodes/ep00X/03-assets/audio/bgm.mp3`。
6. 合成时 BGM 音量 0.15，淡入 1s、淡出 2s，不盖人声。
7. 如果用户自己提供音乐文件，跳过 1-4，直接放到 `bgm.mp3`。

### Step 10：发布物料 → `05-publish/publish-brief.md`

1. 用 `templates/publish-brief.md` 生成发布简报。
2. 包含：标题（≤20 字）、简介、标签、互动设计。
3. 按 `references/xhs-publish-rules.md` 做合规检查。
4. 产出封面图 + 视频文件 + 文案，待人工发布。

## 每集目录结构

```
episodes/ep00X-书名/
├── run-manifest.json        # 运行状态追踪
├── 01-profile/
│   └── book-profile.md      # Step 1 产出
├── 02-script/
│   ├── script.md            # Step 3 产出
│   ├── shot-list.md         # Step 4 产出
│   └── subtitle.ass         # Step 4 产出
├── 03-assets/
│   ├── cover/cover.png      # Step 5 产出
│   ├── scenes/shot_*.png    # Step 5 产出
│   ├── book-shots/          # 书封实拍（如有）
│   └── audio/
│       ├── voiceover.wav    # Step 5 产出
│       └── bgm.mp3          # Step 5 产出
├── 04-video/
│   └── output.mp4           # Step 6 产出
└── 05-publish/
    └── publish-brief.md     # Step 7 产出
```

## 视频规格红线

所有视频必须满足（详见 `templates/video-spec.md`）：

- 分辨率 1080×1920，帧率 30fps，H.264 + AAC
- 时长 ≤200 秒
- 字幕黄色 #FFD700 居中底部
- 无医疗/投资/绝对化承诺

## 风险边界

- 不帮用户规避平台审核、刷量或导流私域。
- 心理健康话题不做诊断承诺，严重情况引导寻求专业帮助。
- 书中观点与个人感悟区分清楚，不把书当万能药。
- 使用版权安全的 BGM 和素材。
