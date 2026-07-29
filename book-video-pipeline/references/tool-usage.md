# 工具使用与认证管理原则

> 本文件定义项目对所有外部工具的调用规范和认证管理红线。

## 一、认证管理红线（不可违反）

### 1. gptsapi 生图认证原则

项目通过 **baoyu ai-content-pipeline 的 `gptsapi_image.py`** 调用 gptsapi（底层 GPT Image 2）生图，**绝不**：

- 在项目中硬编码 `GPTSAPI_KEY`
- 将 gptsapi API key 缓存到项目配置文件
- 绕过 `gptsapi_image.py` 直接调用其他未经验证的 gptsapi 接口

**正确做法**：
```bash
python3 ~/.agents/skills/ai-content-pipeline/scripts/gptsapi_image.py \
  --prompt-file <prompt.md> --aspect-ratio 9:16 --image <out.png>
```

API key 读取优先级：
1. 环境变量 `GPTSAPI_KEY`
2. `<cwd>/.baoyu-skills/.env` 中的 `GPTSAPI_KEY=...`
3. `~/.baoyu-skills/.env` 中的 `GPTSAPI_KEY=...`
4. `--api-key` 参数（仅调试/一次性使用，不推荐写入脚本）

### 2. grok CLI 账户继承原则（已退出本流程，保留备用）

如未来重新启用 grok CLI 生图，仍遵循：
- 不读取 `~/.grok/auth.json` 或任何 grok 认证文件
- 不缓存 grok API key / token / refresh_token 到项目文件
- 不独立调用 xAI API
- 在项目配置、代码、环境文件中不存储 grok 认证信息

### 3. 其他工具的认证来源

| 工具 | 认证来源 | 存储位置 |
|------|----------|----------|
| Kimi K3 | `KIMI_API_KEY` | `~/.zshrc`（env），项目不存储 |
| DeepSeek | `DEEPSEEK_API_KEY` | `~/.zshrc`（env），项目不存储 |
| MiniMax TTS | `MINIMAX_API_KEY` | `~/.zshrc`（env），项目不存储 |
| gptsapi 生图 | `GPTSAPI_KEY` | `~/.zshrc` / `.baoyu-skills/.env`，项目不存储 |
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
| 插画提示词 | DeepSeek V4 Flash | `deepseek-v4-flash` | gptsapi 生图提示词 |
| 场景插画生成 | baoyu ai-content-pipeline `gptsapi_image.py` | gptsapi / GPT Image 2 | 场景图（中文标签/书名用 gptsapi，中文渲染好） |
| i2v 提示词 | seedance-prompt-zh skill | — | 即梦 Seedance 2.0 规范化提示词（@引用 + 结构公式 + 风格锁定） |
| i2v 视频生成 | dreamina CLI | `seedance2.0fast_vip` | 图生视频 / 首尾帧视频 |
| 封面/信息图提示词 | baoyu-cover-image / baoyu-infographic | — | 分析→提示词文件 |
| BGM 下载 | ego-browser skill | — | 用浏览器从 pixabay 下载（绕过 Cloudflare） |
| 发布物料 | GLM-5.2（当前会话） | — | 标题、简介、标签 |

### API 调用注意

- **Kimi**：endpoint 参考 Moonshot 官方文档，兼容 OpenAI 格式
- **DeepSeek**：endpoint `https://api.deepseek.com`，OpenAI 兼容格式
  - 模型 `deepseek-v4-pro`（思考模式，适合分镜分析）
  - 模型 `deepseek-v4-flash`（非思考模式，适合提示词撰写）
  - 已弃用：`deepseek-chat`、`deepseek-reasoner`（2026/07/24 起）

## 三、生图工具调用规范（主流程）

### gptsapi 生图（baoyu ai-content-pipeline）

```bash
python3 ~/.agents/skills/ai-content-pipeline/scripts/gptsapi_image.py \
  --prompt-file <prompt.md> --aspect-ratio 9:16 --image <out.png>
```

- 固定 1K 分辨率
- 需要 `GPTSAPI_KEY` 从环境或 `.baoyu-skills/.env` 读取
- 项目脚本不硬编码 key，只负责拼装 prompt 和调用脚本

### grok CLI 生图（已退出主流程，保留备用）

```bash
# 已退出主流程；如未来启用，仍遵循账户继承原则
~/.grok/bin/grok -p "<DeepSeek写的英文提示词>, 9:16 portrait, save to <path>" -d <workdir>
```

- 比例通过提示词自然语言指定（如 "9:16 portrait"），无 CLI flag
- 输出路径在提示词中指定
- 项目脚本只负责拼装 prompt 字符串和调用 grok 二进制

### 封面/信息图（baoyu skill）

先用 baoyu skill 分析生成提示词文件，再用 gptsapi 生图。

## 四、TTS 调用规范

### MiniMax T2A v2

```python
POST https://api.minimaxi.com/v1/t2a_v2
Authorization: Bearer <MINIMAX_API_KEY>
```

- **音色必须从音色素材库中选择，并经用户审核确认后再生成完整配音**（审核点⑥）
- 音色库位置：`assets/voices/voice-library.json`（元数据）+ `assets/voices/samples/`（试听样本）
- 当前已审核通过：`danya_xuejie`（1.2x，清冷克制）、`female-yujie`（1.2x，沉稳有力量感）
- 每次必须用**本集口播稿**的前 40-60 字生成新样本供用户试听，不得用库内旧样本冒充
- 新音色入库流程见 `assets/voices/README.md`

## 五、视频合成规范

- 片头片尾使用固定素材 `assets/brand/intro.mp4` 和 `outro.mp4`
- 每次合成时自动拼接到视频头尾
- 总时长 ≤180s（intro 2.5s + 正文 ≤175s + outro 2s）

## 六、审核点执行规范

每个 🔴 审核点必须用 `AskUserQuestion` 弹出选项，等待用户选择"通过/修改/重做"后才能继续。**绝不跳过任何审核点。**
