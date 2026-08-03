# 工具使用与认证管理原则

> 本文件定义项目对所有外部工具的调用规范和认证管理红线。

## 一、认证管理红线（不可违反）

### 1. 生图认证原则

生图统一走 `scripts/genimage.py`，它按有无参考图路由到两个后端，**绝不**：

- 在项目中硬编码 `OPENROUTER_API_KEY` / `MINIMAX_API_KEY`
- 将 API key 缓存到项目配置文件
- 绕过分发层直接调用未经验证的生图接口

**正确做法**：
```bash
python3 scripts/genimage.py \
  --style templates/styles/people/cute-anime-girl.md \
  --promptfiles 03-assets/scenes/shot_002.scene.md \
  --image 03-assets/scenes/shot_002.png --ar 9:16 \
  --charRef assets/protagonist-base/girl-ref.png
```

API key 读取优先级：
1. 环境变量 `OPENROUTER_API_KEY` / `MINIMAX_API_KEY`
2. `<cwd>/.baoyu-skills/.env`
3. `~/.baoyu-skills/.env`
4. `--api-key` 参数（仅调试/一次性使用，不推荐写入脚本）

### 2. grok CLI 账户继承原则（备选生图后端，配置可选）

grok CLI 现为**配置可选的备选生图后端**：在 `pipeline.yaml` 的 `image.backends.grok` 启用后，由 `genimage.py` 自动路由调用（openrouter 仍为默认后端）。启用时遵循：
- 不读取 `~/.grok/auth.json` 或任何 grok 认证文件
- 不缓存 grok API key / token / refresh_token 到项目文件
- 用 `--always-approve` 走订阅，不独立调用 xAI API
- 在项目配置、代码、环境文件中不存储 grok 认证信息

### 3. 其他工具的认证来源

| 工具 | 认证来源 | 存储位置 |
|------|----------|----------|
| Kimi K3 | `KIMI_API_KEY` | `~/.zshrc`（env），项目不存储 |
| DeepSeek | `DEEPSEEK_API_KEY` | `~/.zshrc`（env），项目不存储 |
| MiniMax TTS | `MINIMAX_API_KEY` | `~/.zshrc`（env），项目不存储 |
| openrouter 生图 | `OPENROUTER_API_KEY` | `~/.zshrc` / `.baoyu-skills/.env`，项目不存储 |
| MiniMax 生图（参考图通道） | `MINIMAX_API_KEY` | 同上，与 TTS 共用同一个 key |
| grok CLI | xAI 订阅（OIDC） | 已退出本流程；如需启用，仍由 `~/.grok/` 自管理 |

**项目脚本读取方式**：从环境变量或 shell profile 动态读取，不写死到项目文件中。

## 二、LLM 分工与调用规范

| 步骤 | LLM | 模型 | 用途 |
|------|-----|------|------|
| 选书 | GLM-5.2（当前会话） | — | 选书档案、逻辑编排 |
| 文案策划 | Kimi K3 | `kimi-k3` | 视频主题、钩子、观点、引导话术 |
| 口播稿起草 | Kimi K3 | `kimi-k3` | 完整口播稿初稿（Step 3a） |
| 口播稿初审 | grok CLI | grok 4.5（xAI 订阅） | 口语自然度、过渡、重复、说教感（只出问题清单，不改稿）（Step 3b） |
| 口播稿二审 | DeepSeek V4 Pro | `deepseek-v4-pro` | 按 grok 清单逐条修复 + 安全检查 + 长句拆分（Step 3c） |
| 口播稿去AI味 | humanizer-zh skill | — | **最后一道**，只删不加，清理前序工序留下的 AI 腔（Step 3d） |
| 去AI味检查 | `check-script.py` | — | 自动检查 A-D 共 20 项，必须全绿 |
| 分镜画面描述 | DeepSeek V4 Pro | `deepseek-v4-pro` | 每镜画面描述（含 camera/transition/cues/layers） |
| 插画提示词（**仅内容**） | DeepSeek V4 Flash | `deepseek-v4-flash` | 每镜 `shot_00X.scene.md`；风格段落是风格卡常量，不由模型生成 |
| 定妆图 + 无主角镜头 | `scripts/genimage.py` | openrouter / GPT Image 2 | 分发层，无 characters/ref 时走此通道 |
| 含主角镜头（角色锁定） | `scripts/genimage.py` | dreamina image2image / Seedream 5.0 | `characters: true` + `charRef` 时走此通道，角色+风格双锁 |
| 备用参考图生图 | `scripts/genimage.py` | baoyu-image-gen / MiniMax image-01 | 显式 `--ref` 时走此通道（备用，对 anime 锁定弱） |
| i2v 提示词 | seedance-prompt-zh skill | — | 即梦 Seedance 2.0 规范化提示词（@引用 + 结构公式 + 风格锁定） |
| i2v 视频生成 | dreamina CLI | `seedance2.0fast_vip` | 图生视频 / 首尾帧视频 |
| 封面提示词 | baoyu-cover-image | — | 分析→提示词文件 |
| BGM 下载 | ego-browser skill | — | 用浏览器从 pixabay 下载（绕过 Cloudflare） |
| 发布物料 | GLM-5.2（当前会话） | — | 标题、简介、标签 |

### API 调用注意

- **Kimi**：endpoint 参考 Moonshot 官方文档，兼容 OpenAI 格式
- **DeepSeek**：endpoint `https://api.deepseek.com`，OpenAI 兼容格式
  - 模型 `deepseek-v4-pro`（思考模式，适合分镜分析）
  - 模型 `deepseek-v4-flash`（非思考模式，适合提示词撰写）
  - 已弃用：`deepseek-chat`、`deepseek-reasoner`（2026/07/24 起）

## 三、生图工具调用规范（主流程）

### 统一入口：`scripts/genimage.py`

**所有生图都走这个入口，不直接调后端。** 它按镜头类型（`characters` + `charRef`）自动路由三档后端：

```bash
# 主角定妆图（openrouter，无 ref）
python3 scripts/genimage.py \
  --style templates/styles/people/cute-anime-girl.md \
  --promptfiles 03-assets/scenes/_protagonist.scene.md \
  --image assets/protagonist-base/girl-ref.png --ar 9:16

# 含主角镜头（dreamina Seedream，带定妆图 ref）
python3 scripts/genimage.py \
  --style templates/styles/people/cute-anime-girl.md \
  --promptfiles 03-assets/scenes/shot_002.scene.md \
  --image 03-assets/scenes/shot_002.png --ar 9:16 \
  --charRef assets/protagonist-base/girl-ref.png

# 无主角镜头（openrouter，无 ref）
python3 scripts/genimage.py \
  --style templates/styles/people/cute-anime-girl.md \
  --promptfiles 03-assets/scenes/shot_005.scene.md \
  --image 03-assets/scenes/shot_005.png --ar 9:16

# 批量并发
python3 scripts/genimage.py --batchfile 03-assets/scenes/batch.json --jobs 3
```

分发层职责：风格卡 + 场景内容多文件提示词拼接、并发调度、失败重试、
输出格式归一（JPEG→PNG）、画幅与 provider 显式钉死。
提示词组织规则见 `templates/scene-prompt.md`。

| 通道 | 触发条件 | 后端 | 特性 |
|------|---------|------|------|
| openrouter | 无 `characters` / 无 `ref`（定妆图 + 无主角镜头） | `ai-content-pipeline/scripts/openrouter_image.py` | GPT Image 2，固定 1K，风格质量最高 |
| dreamina | `characters: true` + 有 `charRef` | `dreamina image2image`（Seedream 5.0） | 角色 + 风格双锁，原生 2k，实测优于 MiniMax |
| baoyu | 有 `--ref`（无 charRef，备用） | `baoyu-image-gen/scripts/main.ts` | MiniMax image-01 subject_reference，对 anime 锁定弱 |
| grok (备选) | `--backend grok` 或 `task.backend=grok` | grok CLI image_gen | agent 式生图，走订阅，非确定性 |

**两个实测坑（已在 `genimage.py` 内处理，手工调后端时要自己注意）**：

1. **画幅**：MiniMax 的 body 是 `if(aspect_ratio) else if(size)`，两个都给时
   `size` 被忽略，只出 720×1280。要 1080×1920 必须**只给 `--size`，不给 `--ar`**。
2. **格式**：MiniMax 不管扩展名一律回 JPEG，落成 `.png` 是假 PNG，需 `sips` 转换。

另有项目级 `.baoyu-skills/baoyu-image-gen/EXTEND.md` 覆盖用户级默认值
（用户级是 `zai` + `16:9`，在本项目会静默出横图且不支持 `ref`）。

**dreamina 通道注意事项**：
- 用 OAuth 登录（`dreamina login`），登录态存 `~/.dreamina/`，项目不读认证
- image2image 强制 ≥2k（不支持 1k），素材保留原生分辨率，最终 1080×1920 由 hyperframes 渲染处理
- 余额查询：`dreamina user_credit`

### grok CLI 生图（备选后端，已集成进 genimage.py）

```bash
# 通过 pipeline.yaml 的 image.backends.grok 启用后，genimage.py 自动调用，无需手动执行
~/.grok/bin/grok --cwd <workdir> --always-approve --output-format json --tools image_gen \
  -p "<DeepSeek写的英文提示词>, 9:16 portrait, save to <path>"
```

- 已集成进 `genimage.py`：在 `pipeline.yaml` 配置 `image.backends.grok` 即可，无需手动调用
- 比例通过提示词自然语言指定（如 "9:16 portrait"），无 CLI flag
- 输出路径在提示词中指定
- 调用必带 `--always-approve --output-format json --tools image_gen`（订阅继承、结构化输出）
- 项目脚本只负责拼装 prompt 字符串和调用 grok 二进制

### 封面/信息图（baoyu skill）

先用 `baoyu-cover-image` 分析并产出提示词文件，
再交给 `scripts/genimage.py` 生图（封面比例 `--ar 3:4`，小红书首图）。

## 四、TTS 调用规范

### MiniMax T2A v2

```python
POST https://api.minimaxi.com/v1/t2a_v2
Authorization: Bearer <MINIMAX_API_KEY>
```

- **音色必须从音色素材库中选择，并经用户审核确认后再生成完整配音**（审核点⑥）
- 音色库位置：`assets/voices/voice-library.json`（元数据）+ `assets/voices/samples/`（试听样本）
- 当前已审核通过：`danya_xuejie`（1.1x，清冷克制）、`female-yujie`（1.1x，沉稳有力量感）
- 每次必须用**本集口播稿**的前 40-60 字生成新样本供用户试听，不得用库内旧样本冒充
- 新音色入库流程见 `assets/voices/README.md`

## 五、视频合成规范

- 片头片尾使用固定素材 `assets/brand/intro.mp4` 和 `outro.mp4`
- 每次合成时自动拼接到视频头尾
- 总时长 ≤200s（intro 1.0s + 正文 ≤195s + outro 3.2s）

## 六、审核点执行规范

每个 🔴 审核点必须用 `AskUserQuestion` 弹出选项，等待用户选择"通过/修改/重做"后才能继续。**绝不跳过任何审核点。**
