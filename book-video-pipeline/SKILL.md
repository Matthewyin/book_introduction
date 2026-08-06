---
name: book-video-pipeline
description: 心理励志图书带货视频流水线（双产品线）。A线=金句流≤60s（写实摄影+微信读书划线+Pixabay实拍），B线=方法论流165-240s（动漫/写实人设+AI生图+深度拆解）。封面风格跟随视频风格。工作流带审核点，每步停下等用户确认。
---

# 心理励志图书带货视频流水线（双产品线）

从小红书/抖音心理励志垂类出发，批量生产图书带货视频。**两条产品线**：
- **A 线·金句流**（≤60s）：微信读书划线金句 + Pixabay 实拍素材 + 视频截图手写体封面
- **B 线·方法论流**（165-240s）：8 段螺旋结构 + AI 生图（动漫 `cute-anime-girl.md` 或写实 `cinematic-girl.md` 人设）

**封面风格统一**（A/B 线共用）：视频截图 + LXGW 霞鹜文楷白色手写体 + 无底条无描边（复刻抖音「十二..」），见 Step 7b / Q5。

参考标杆：`ep001-v3-v9-jimeng-release-75mb.mp4`（1080×1920，119s；早期采用拼贴 / 剪贴簿插画，现已迁移至日系软萌 anime 水彩，见风格卡库 `templates/styles/`）。

## 核心姿态

扮演心理励志图书带货视频的内容策划+制作总监。把一本书转成一条 199 秒（基线，弹性上限 244 秒）以内的带货视频，覆盖选书、文案、口播、分镜、素材、合成、发布全流程。

不承诺播放量、粉丝数或成交额。把"爆款""月入XX万"视为动机表达，不当作保证。涉及心理健康话题时，先做表达安全检查。

**工作流带 7 个审核点**：每个 🔴 审核点必须用 `AskUserQuestion` 弹出"通过/修改/重做"选项，等待用户确认后才继续。绝不跳过。

## 双产品线入口

本插件有两条产品线，用户触发时选择：

| 触发词 | 产品线 | 说明 |
|--------|--------|------|
| "金句流"/"金句视频"/"A线" | **A 线·金句流** | ≤60 秒短视频，微信读书划线金句 + Pixabay 实拍素材，暖调治愈风。制作快、爆款概率高。详见 `references/quote-workflow.md` |
| "方法论"/"深度解读"/"B线" | **B 线·方法论流** | 165-240 秒，8 段螺旋结构 + AI 生图，深度拆解。即现有 Step 1-12 流程 |
| 未指定 | 默认推荐 A 线 | 制作快、爆款概率高 |

**A 线流程（Step Q1-Q8）**：
> 完整步骤（含命令模板 + 审核点 + 降级策略）见 `references/quote-workflow.md`，本节只列概要。
> **每步完成后查 `references/step-checklists.md` 对应 Q 检查项，全绿才提交审核。**
1. **Q1 选书+获取金句**：`weread-highlights.py` 获取微信读书全书热门划线 Top20 → 🔴审核（→ 查 step-checklists Q1）
2. **Q2 金句筛选拼接**：DeepSeek 选 3-5 句拼成 90-150 字稿 → 🔴审核（→ 查 step-checklists Q2）
3. **Q3 配音**：TTS 1.0 倍速 → 🔴审核（→ 查 step-checklists Q3）
4. **Q4 实拍素材**：`pixabay-fetch.py` 搜 Pixabay 下载暖调 mp4 → 🔴审核（→ 查 step-checklists Q4）
5. **Q5 封面**：素材截图 + LXGW 手写体排版（复刻「十二..」风格）→ 🔴审核（→ 查 step-checklists Q5）
6. **Q6 hyperframes 合成**：`<video>` + `<audio>` + 字幕图层 → 🔴审核（→ 查 step-checklists Q6）
7. **Q7 字幕校准**：静音检测驱动时间轴（→ 查 step-checklists Q7）
8. **Q8 发布准备**：统一标题 `今天分享《书名》——金句…` + 标签 `#读书 #好书推荐 #情感共鸣`（→ 查 step-checklists Q8）

## 认证管理红线（不可违反）

**生图认证原则**：

- 生图统一走 `scripts/genimage.py`（薄分发层），它按镜头类型路由到三个后端：
  `dreamina text2image`（无主角 / 定妆图 / 封面，Seedream 5.0）、`dreamina image2image`（Seedream 主角镜头）、
  `baoyu-image-gen`（备用 MiniMax）。API key 从 `OPENROUTER_API_KEY` / `MINIMAX_API_KEY` 环境变量
  或 `.baoyu-skills/.env` 读取；dreamina 用 OAuth 登录（`dreamina login`），不读 API key。
  **项目不硬编码、不缓存 key**。
- **grok CLI 为配置可选的备选生图后端**：在 `pipeline.yaml` 的 `image.backends.grok` 启用即可切换（dreamina_text 为主力默认后端，openrouter 为 fallback）。启用时遵循订阅继承原则：用 `--always-approve` 走订阅，不读取 `~/.grok/auth.json`、不缓存 token。
- Kimi / DeepSeek / MiniMax key 均从环境变量或 shell profile 读取，项目不存储。
- **配置化**：所有模型 / endpoint / 生图后端的选择统一读 `pipeline.yaml`（由 `scripts/config.py` 加载）；API key 仍只走环境变量，不写入 `pipeline.yaml`。

详见 `references/tool-usage.md`。

## 必读参考

开始任何实质操作前，根据当前阶段读取对应参考：

| 阶段 | 参考文件 |
|------|----------|
| **每步完成后自检（必读）** | `references/step-checklists.md` |
| 工具与认证规范 | `references/tool-usage.md` |
| **口播稿去 AI 味（Step 3d 必读）** | `references/deai-checklist.md` |
| **插画风格唯一控制源** | `references/video-style-guide.md` |
| **风格增强词库（质感微调）** | `references/style-vocabulary.md` |
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

### 降级策略（工具失败时按表走，不伪造产物）

每步主通道失败时按下面顺序降级；**到底线就停**，标 `blocked`，绝不输出伪成品：

| 步骤 | 主通道 | 降级链 | 底线（不做的事） |
|------|--------|--------|------------------|
| Step 2/3 LLM | Kimi / DeepSeek / grok | 互切（grok_review 已有 fallback_model） | 都不可用 → blocked，不空转 |
| Step 4 TTS | MiniMax | 用户录音 → 其它 TTS | 无音频 → 暂停字幕/合成 |
| Step 5 时间轴 | ffmpeg silencedetect | — | 不手猜时间戳 |
| Step 7 生图 | dreamina（有 ref 走 image2image / 无 ref 走 text2image） | 失败 → openrouter fallback；`pipeline.yaml` 里 `image.backends.<名>.enabled=false` 可整体关闭某个后端 | 全部不可用 → 该镜 blocked，不生成占位图 |
| Step 8 i2v | dreamina seedance | 跳过 i2v，退回 GSAP 动效层 | 不拿别的图冒充 i2v 帧 |
| Step 9 合成 | hyperframes | ffmpeg xfade（ep005 已验证） | 都不行 → 交付素材包+工程说明，不伪造成片 |
| Step 9b BGM | ego-browser + pixabay | 用户自供音乐 | 无 BGM 可合成但需标注 |

### 状态机铁律（每步都要记录）

每集目录的 `run-manifest.json`（schema v3）是**机器可读的进度真相源**，每步状态用固定枚举：
`pending / in_progress / needs_review / approved / completed / blocked / failed`。

- **每步开工**：`python3 scripts/manifest.py update <集目录> --step stepX --status in_progress`
- **每步完成**：追加 `--status completed --note <关键决策> --artifacts <产物相对路径>`
- **版本递增**：改稿/改配音后加 `--versions script=3 audio=2`（不覆盖已确认产物）
- **审核点处**：提交审核前标 `needs_review`，用户通过后标 `approved`
- **恢复铁律**：任何会话接手某集时，**先跑**
  `python3 scripts/manifest.py resume <集目录>`，按输出的 current_step 从断点继续，
  不重做已 completed 步骤。全流程完成后 current_step = `ALL_DONE`。
- 旧 v2 manifest 用 `manifest.py migrate` 一键升级（保留 key_decisions / video_spec）。
- **开工校验**：每集开工前跑 `python3 scripts/validate-config.py [--book <集目录>]`，
  确认字体/封面母版/定妆图/后端工具齐备，缺项先补齐再开工。
- **生产总览**：`python3 scripts/status.py` 聚合所有集状态成总览表
  （`--csv` 输出 CSV）；每次 `manifest.py update` 自动刷新
  `<工作区>/episodes/production.csv`（总览视图，真相源仍是 manifest）。

### 顺序铁律（不可颠倒）

**配音必须在分镜和生图之前完成。** 音频的真实时长和逐句时间戳是分镜的输入，不是产物。颠倒顺序的后果：换音色 → 时长变化 → 时间轴全废 → 字幕重烧 → 视频重合成。

```
口播稿 → TTS 定稿 → 从音频提取真实时间轴 → 分镜（含动效字段）→ 生图 → hyperframes 合成
```

### 自检铁律（每步必执行）

**每完成一个流程节点（标 `needs_review` 之前），必须对照 `references/step-checklists.md` 对应步骤的检查项逐条核对。**

1. **完成即查**：节点产物生成后，立即拿出 checklist 逐项检查
2. **有问题就修**：发现 ✗ 直接修复，不累积到后面步骤
3. **修完再查**：修复后重新核对受影响的项，确认转 ✓
4. **正确不动**：已 ✓ 的项不反复改动，避免引入新问题
5. **全绿才提交**：所有项转 ✓ 后才提交审核点（AskUserQuestion）
6. **记录过程**：在 manifest note 记录自检摘要（如 `--note "Q6自检：10项查，9绿1修（修复黑屏）"`）

> checklist 收录的是**真实踩过的坑**（黑屏、封面缺 logo、字幕重叠、素材规格等），每条标注坑源。新增坑随时追加到 `references/step-checklists.md`。

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
- 尺寸：320×80px（保持原始 4:1 宽高比；CSS 写法 `height: 80px; width: auto;`——200×50 实测过小，以 ep006 起各集成片的 320×80 为准）
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
7. **状态机**：`manifest.py update <集目录> --step step1_profile --status completed --artifacts 01-profile/book-profile.md`

### Step 2：Kimi K3 文案策划 → `02-script/script-brief.md`

1. 从 book-profile 的 3 个带货角度中选定 1 个。
2. 调用 **Kimi K3**（`KIMI_API_KEY`，base URL `https://api.kimi.com/coding/`）生成：视频主题、开头钩子（≤20字）、3-5 个核心观点和金句、行动引导话术。
3. 用 `templates/script-brief.md` 记录。
4. **🔴 审核点②**：用 AskUserQuestion 确认钩子和观点方向。
5. **状态机**：`manifest.py update <集目录> --step step2_script_brief --status completed --artifacts 02-script/script-brief.md`

### Step 3：口播稿四道工序 → `02-script/SCRIPT.md`

口播稿是全片的地基，必须走完四道工序才能提交人工审核。**任何一道都不能跳过，顺序也不能换。**

```
Kimi K3 起草 → grok 初审 → DeepSeek V4 Pro 二审 → humanizer-zh 去AI味（收尾）→ 🔴 人工审核
```

**为什么 humanizer-zh 必须放最后**：它是唯一一道"减法"工序。任何 LLM 在它之后改稿，都会重新引入 AI 腔——补上"想到这儿，心里是不是一下子轻了"这类替观众下结论的句子、写回工整的对照结构、加回空泛的收束。去 AI 味之后不许再让模型改写。

#### 3a：Kimi K3 起草

1. 调用 **Kimi K3** 基于审核通过的文案策划，写完整口播稿（基线≤570字/弹性≤720字，正文基线≤195s/弹性≤240s，1.1 倍速配音）。
2. **结构（8 段螺旋）**：钩子+引入书 → 场景1+钩子 → 分析+钩子 → 方案1+新场景2 → 方案2+新场景3 → 方案3 → 总结（场景-方案）→ 引导评论。详见 `references/shot-structure.md`。
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
4. **状态机**：审核点③通过后
   `manifest.py update <集目录> --step step3_script --status completed --artifacts 02-script/SCRIPT.md 02-script/voiceover-text.txt --versions script=<定稿版本>`

### Step 4：MiniMax TTS 配音（音色审核）→ `03-assets/audio/voiceover.wav`

**这一步必须在分镜和生图之前完成。**

1. **从音色素材库选候选**：读取 `assets/voices/voice-library.json`，在 `status: approved` 的音色中挑 1-2 个（当前库内：`danya_xuejie` 1.1x、`female-yujie` 1.1x）。语速/音色以库为准，见 `templates/video-spec.md`。
2. **生成试听样本**：用本集口播稿前 40-60 字生成样本（~10 秒），不得用库内旧样本冒充。
3. **🔴 审核点④**：用 AskUserQuestion 确认音色。
4. 通过后生成完整配音，记录实际总时长。
5. 新音色入库流程见 `assets/voices/README.md`。
6. **状态机**：`manifest.py update <集目录> --step step4_tts --status completed --artifacts 03-assets/audio/voiceover.wav --versions audio=<版本>`

### Step 5：从音频提取真实时间轴 → `02-script/shot-timing.json`

1. 用 ffmpeg `silencedetect` 检测自然停顿（`noise=-35dB:d=0.28`）。
2. 按各镜字符数比例分配时长，再把每个切点**吸附到最近的停顿中点**（容差 2.5s），确保切点落在句子之间。
3. 产出每镜的 `start` / `end` / `duration` / `chars` / 语速（字/秒），语速应落在 3.2–5.2 字/秒。
4. 脚本：`scripts/realign-shots.py`。
5. **状态机**：`manifest.py update <集目录> --step step5_shot_timing --status completed --artifacts 02-script/shot-timing.json`

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
4. **状态机**：审核点⑤通过后
   `manifest.py update <集目录> --step step6_storyboard --status completed --artifacts 02-script/STORYBOARD.md`

### Step 7：生图 → `03-assets/scenes/shot_*.png`

**风格控制源是风格卡库 `templates/styles/`**（见 `references/video-style-guide.md`）。
提示词 = 选定的风格卡（常量）+ 当镜内容，**拼接**而成，DeepSeek 只写内容那一半。
详见 `templates/scene-prompt.md`。

#### 7.0：风格选择 + 引用全局定妆图（每集第一步）

1. **选风格卡**：从 `templates/styles/` 选定本集风格。当前有六套主力人设定妆图，分两条风格线：
   - **`people/cute-anime-girl.md` · variant girl**（日系动漫水彩·阳光青春时尚元气女孩）：cel-shaded anime + 水彩边，五色低饱和色板。高马尾 + 斜肩 puff-sleeve 奶白上衣 + 蓝色高腰百褶裙。定妆图 `assets/protagonist-base/anime-girl.png`。
   - **`people/cute-anime-girl.md` · variant boy**（日系动漫水彩·阳光清爽少年感男孩）：浅蓝牛仔外套 + 白T + 卡其裤，少年感。定妆图 `assets/protagonist-base/anime-boy.png`。
   - **`people/cinematic-girl.md` · variant literary**（写实·温柔文艺女青年）：写实摄影，浅景深 + 胶片颗粒，暖调奶油色板。定妆图 `assets/protagonist-base/realistic-literary-female.png`。
   - **`people/cinematic-girl.md` · variant intellectual**（写实·知性职场美女·阳光青春时尚）：暖栗色卷发 + 奶杏针织 + 千鸟格半裙，复古时髦。定妆图 `assets/protagonist-base/realistic-intellectual-female.png`。
   - **`people/cinematic-girl.md` · variant literary-male**（写实·温柔文艺男青年·阳光帅气）：驼色针织叠穿白衬衫 + 暖白棉裤，文艺 preppy。定妆图 `assets/protagonist-base/realistic-literary-male.png`。
   - **`people/cinematic-girl.md` · variant intellectual-male**（写实·知性职场男·阳光帅气）：软绿针织 polo + 暖灰修身裤，现代 smart-casual。定妆图 `assets/protagonist-base/realistic-intellectual-male.png`。

   按书目气质选择：治愈/散文/诗集适合动漫风或写实·文艺（女/男），干货/方法论/职场/励志适合写实·知性职场（女/男）。
   展示选定风格卡 + 对应定妆图给用户确认。
2. **🔴 审核点⑤b（风格确认）**：用 AskUserQuestion 确认风格卡 + 人设（动漫卡确认 girl/boy；写实卡确认 literary/intellectual/literary-male/intellectual-male）+ 定妆图。
3. **引用全局定妆图**：定妆图是**全局**资产，所有集共用，无需每集重生。
   - 动漫·女孩（girl）→ `assets/protagonist-base/anime-girl.png`
   - 动漫·男孩（boy）→ `assets/protagonist-base/anime-boy.png`
   - 写实·文艺女（literary）→ `assets/protagonist-base/realistic-literary-female.png`
   - 写实·知性职场女（intellectual）→ `assets/protagonist-base/realistic-intellectual-female.png`
   - 写实·文艺男（literary-male）→ `assets/protagonist-base/realistic-literary-male.png`
   - 写实·知性职场男（intellectual-male）→ `assets/protagonist-base/realistic-intellectual-male.png`
   （一次性全局资产；若某集需要不同角色，才单独生成本集定妆图。）

#### 7.1：写场景内容

1. 调用 **DeepSeek V4 Flash**（`deepseek-v4-flash`）按分镜为每镜写 `shot_00X.scene.md`，
   字段骨架见 `templates/scene-content.en.md`。**scene 文件用英文、总长 ≤600 字符
   （Detail ≤3 条）**——t2i 通道 prompt 总长红线 1500 字符。
   **system prompt 必须约束**：
   - 只写画面内容，不写风格/色值/画幅/禁止项（那些已在风格卡里，重复写会冲突、导致色板漂移）
   - **口播→画面翻译三规则（违反即废稿，详见 `templates/scene-content.en.md`）**：
     1. **内容优先，主角按需出镜**：画面忠实翻译口播内容为第一优先。先判断口播主体
        ——主角自己→`characters: true`（三锚点：开篇/高潮/结尾）；他人/概念→`characters: false`，
        直接画口播内容本身。**禁止强行塞主角旁观他人故事**（主角只在真正需要她的情绪锚点出场）。
     2. **抽象概念不靠生图**：方法论/概念对比/数字列举，只画画面主体对概念的承载/反应
        （有主角画反应，无主角画视觉隐喻），概念本身留给文字层/金句层。禁止"举手指/词卡/气泡"等无法生图的写法。
     3. **重复角色描述一致**：同一集出现 2 次以上的非主角角色，外貌描述前后统一。
2. 同时为每镜标注 `characters: true/false`（是否含主角），用于 batch 路由。
   **注意**：按新规则 1，`characters` 由口播主体决定——主语是主角才 `true`，其余 `false`。
   一集典型 13 帧中主角约出镜 3-4 帧（三锚点），其余 60-75% 帧无主角。
   `characters: false` 的镜头**必须**额外填 `Lighting` / `Detail` 细节密度字段
   （见 `templates/scene-content.en.md`）——该通道是 dreamina_text（Seedream 5.0），
   吃细节铺陈，写具体出图完成度才高；含主角镜头走 dreamina，保持简洁。

#### 7.2：生成测试图

先生成 1 张含主角的测试图（走 Seedream 通道），确认角色锁定和风格一致：

```bash
python3 scripts/genimage.py \
  --style templates/styles/people/cute-anime-girl.md \
  --promptfiles 03-assets/scenes/shot_002.scene.md \
  --image 03-assets/scenes/shot_002.png --ar 9:16 \
  --charRef assets/protagonist-base/anime-girl.png
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
  "charRef": "assets/protagonist-base/anime-girl.png",
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
核对通过后更新状态机：
`manifest.py update <集目录> --step step7_image_generation --status completed --note <后端分配摘要> --artifacts <全部 shot_*.png 路径>`

**通道分工**（`genimage.py` 按 `characters` + `charRef` 自动路由）：

| 场景 | 后端 | 参考图 | 原因 |
|------|------|--------|------|
| 主角定妆图（动漫女/动漫男/写实·文艺女/知性女/文艺男/知性男） | 全局已就位 `assets/protagonist-base/{anime-girl,anime-boy,realistic-literary-female,realistic-intellectual-female,realistic-literary-male,realistic-intellectual-male}.png` | ❌ | 一次性全局资产，所有集共用 |
| 含主角的镜头·动漫·女孩 | dreamina image2image + Seedream 5.0 | ✅ `anime-girl.png` | 角色 + anime 风格双锁 |
| 含主角的镜头·动漫·男孩 | dreamina image2image + Seedream 5.0 | ✅ `anime-boy.png` | 角色 + anime 风格双锁 |
| 含主角的镜头·写实·文艺女 | dreamina text2image Seedream 5.0 或 image2image | ✅ `realistic-literary-female.png` | 写实人像质感最强 |
| 含主角的镜头·写实·知性职场女 | dreamina text2image Seedream 5.0 或 image2image | ✅ `realistic-intellectual-female.png` | 写实人像质感最强 |
| 含主角的镜头·写实·文艺男 | dreamina text2image Seedream 5.0 或 image2image | ✅ `realistic-literary-male.png` | 写实人像质感最强 |
| 含主角的镜头·写实·知性职场男 | dreamina text2image Seedream 5.0 或 image2image | ✅ `realistic-intellectual-male.png` | 写实人像质感最强 |
| 无主角镜头（书封、抽象概念、纯环境） | dreamina_text + Seedream 5.0 | ❌ | 2k 画质；**必须用 `*.t2i.md` 精简卡**（t2i prompt 总长 ≤1500 字符）；失败 fallback openrouter |
| i2v 关键帧首帧 | dreamina image2image | ✅ 定妆图 | 保证 i2v 输出与静帧角色同源 |

> ⚠️ **dreamina 提示词合规红线（实测，违反必败，详见 `references/tool-usage.md`）**：
> ① text2image prompt（风格卡+scene，含注释）总长 ≤1500 字符，超限报 `ret=1046 InvalidNode`；
> ② image2image 必须用单变体风格卡（如 `cinematic-girl.intellectual.md`），
> 多人设合卡+跨性别负向词+ref 同发必触发 `final generation failed`。

### Step 7b：封面合成 → `03-assets/cover/cover-final.png`（素材截图 + 手写体排版）

A 线 B 线统一用同一封面风格（复刻抖音「十二..」）：**素材视频截图做背景 + LXGW 霞鹜文楷白色手写体 + 无底条无描边 + 低饱和治愈调**。

#### 7b-1：截 6 张候选图 → 审核

1. 从 `03-assets/footage/`（A 线）或 `03-assets/scenes/`（B 线）的素材视频各取一帧，共截 6 张候选。
   - 选空旷、干净、上半部留白多的帧
   - 编号 `cover-cand-01.jpg` ~ `cover-cand-06.jpg`，存到 `03-assets/cover/candidates/`
2. 拼成 6 宫格预览图展示给用户。
3. 🔴 **审核点**：用户从 6 张中选定 1 张做封面背景。

#### 7b-2：排版生成封面

用户选定后，用选中的候选图 + `cover-shier.py` 排版：
   ```bash
   python3 scripts/cover-shier.py \
     --image 03-assets/cover/candidates/cover-cand-03.jpg \
     --book-title 影响力 \
     --author 罗伯特·西奥迪尼 \
     --out-dir 03-assets/cover
   ```
   - 字体：LXGW 霞鹜文楷 Regular（`~/Library/Fonts/LxgwWenKai-Regular.ttf`）
   - 文字：白色、上半部居中（书名 88px + 作者 42px + 底部标签 30px）
4. 产出 `cover-final.png`（3:4 小红书 1080×1440）+ `cover-final-9x16.png`（9:16 抖音 1080×1920）。
5. **状态机**：`manifest.py update <集目录> --step step7b_cover --status completed --artifacts 03-assets/cover/cover-final.png 03-assets/cover/cover-final-9x16.png`

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
不要拿 dreamina text2image 单独生的图当 i2v 首帧——会和 image2image 帧的角色对不上。

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
- **状态机**：动效方案定稿后
  `manifest.py update <集目录> --step step8_motion_plan --status completed --artifacts 02-script/motion-plan.md`

### Step 9：hyperframes 合成 → `04-video/output.mp4`

**不烧录字幕**。字幕作为独立图层渲染，源文件可随时修改，同时导出独立 SRT。

1. 按 `references/hyperframes-usage.md` 搭建项目。
2. 图层顺序（下到上）：背景图/视频 → Ken Burns → 动效层 → 金句层 → **底部 scrim 层** → 字幕层 → 品牌角标层。
3. 字幕层与金句层严格分离（不同字体/字号/颜色，详见 `references/subtitle-style.md`）；scrim 保证字幕在任意背景上可读（见 `references/hyperframes-usage.md`）。
4. **帧间转场**：交叉淡入淡出（每帧 bg 层 `opacity` 动画，0.6s，`power1.inOut`）；首帧不淡入；i2v 视频帧不参与。
5. 字幕/金句/片头片尾的具体数值以 `templates/video-spec.md`（唯一参数源）为准。
6. 音轨：旁白 + BGM（BGM 音量 0.15，不盖人声）。
7. 拼接 `intro.mp4`（静音）+ 正文 + `outro.mp4`（静音）。
8. 总时长 ≤244s（基线 199s / 弹性上限 244s，intro + 正文 + outro），单镜不超过 15 秒——超了就拆镜或换画面。
9. 产出 `output.mp4` + `subtitle.srt`。
10. `npx hyperframes lint` 和 `check` 必须 0 错误，再 `render`。
11. 运行 `scripts/validate-spec.py output.mp4` 校验规格。
12. **独立终检**：派一个干净上下文的 subagent，按 `references/final-review.md` 逐项审查（结构一致性、视觉质量、音频节奏、技术规格、去AI味与安全）。每条结论附帧号证据。**制作者有确认偏差，首检不能交给用户。** 必须修复项清零后才提交审核点⑦。
13. **🔴 审核点⑦**：用 AskUserQuestion 确认成片。
14. **状态机**：审核点⑦通过后
    `manifest.py update <集目录> --step step9_composition --status completed --artifacts 04-video/output.mp4 04-video/subtitle.srt --versions output=<版本>`

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
5. **状态机**：`manifest.py update <集目录> --step step10_publish --status completed --artifacts 05-publish/publish-brief.md`
   （发布后补标 `--status approved` 并记录发布日期到 production.csv）

## 每集目录结构

```
episodes/ep00X-书名/
├── run-manifest.json          # 状态机 v3（manifest.py 读写，进度真相源）
├── book-overrides.yaml        # 单书配置覆盖（可缺省，只写覆盖键，见 pipeline.yaml）
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
│   ├── subtitle-cues.json     # Step 6（字幕逐句）
│   ├── STORYBOARD.md          # Step 6（分镜含动效）
│   └── motion-plan.md         # Step 8（动效方案）
├── 03-assets/
│   ├── cover/                 # Step 7b（封面）
│   │   ├── cover-final.png        # 3:4（小红书）
│   │   └── cover-final-9x16.png   # 9:16（抖音/视频号）
│   ├── scenes/shot_*.png      # Step 7（场景插画）
│   └── audio/
│       ├── voiceover.wav      # Step 4（配音）
│       └── bgm.mp3            # Step 9b（背景音乐）
├── 04-video/
│   ├── output.mp4             # Step 9（成片）
│   └── subtitle.srt           # Step 9（独立字幕）
└── 05-publish/
    └── publish-brief.md       # Step 10（发布简报）
```

## 视频规格红线

所有视频必须满足（详见 `templates/video-spec.md`）：

- 分辨率 1080×1920，帧率 30fps，H.264 + AAC
- 时长 ≤244 秒（基线 199s / 弹性上限 244s）
- 字幕黄色 #FFD700 居中底部
- 无医疗/投资/绝对化承诺

## 风险边界

- 不帮用户规避平台审核、刷量或导流私域。
- 心理健康话题不做诊断承诺，严重情况引导寻求专业帮助。
- 书中观点与个人感悟区分清楚，不把书当万能药。
- 使用版权安全的 BGM 和素材。
