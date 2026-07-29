# SCRIPT — {{书名}}·{{带货角度}}

> 锁定旁白文件。Step 3 审核通过后写入，Step 4 的 TTS 直接读取各节的缩进块。
> 格式对齐 hyperframes `hyperframes-core/references/script-format.md`。
> **7 段结构遵循 `references/shot-structure.md`（唯一控制源）。**

**Voice:** {{voice_id}}（MiniMax，从 `assets/voices/voice-library.json` 选）
**Voice settings:** speed 1.2 · vol 1.0 · pitch 0 · model speech-02-hd
**Voice direction:** {{整体语气，例：清冷克制，像朋友深夜聊天，不煽情不说教}}

**Total chars:** {{字数}}（≤570 字）
**Estimated duration:** {{预估秒数}}s（正文 ≤195s + intro 1.0s + outro 3.2s ≤200s）

---

## Line 1 — 钩子 (Frame 1)

**Time:** 0.0 – {{x}}s（预估，Step 5 用静音检测替换为真实值）
**Delivery:** {{例：直接、平静，不要质问语气}}

    {{第一句旁白原文，≤18 字}}

## Line 2 — 扎心场景 (Frame 2)

**Time:** {{x}} – {{y}}s
**Delivery:** {{例：语速略快，堆叠焦虑感}}

    {{扎心场景旁白原文}}

## Line 3 — 引入书 (Frame 3)

**Time:** {{y}} – {{z}}s
**Delivery:** {{例：转暖，放慢，像递过来一本书}}
**必须包含**：作者姓名/国籍/领域地位 + 书籍领域地位/销量

    {{引入书旁白原文，含作者介绍和书籍介绍}}

## Line 4 — 场景演绎 (Frame 4)

**Time:** {{z}} – {{w}}s
**Delivery:** {{例：叙事感，有画面}}

    {{场景演绎旁白原文}}

## Line 5 — 观点拆解 (Frame 5+)

**Time:** {{w}} – {{v}}s
**Delivery:** {{例：每个金句放慢加重，展开部分恢复正常语速}}

    {{观点拆解旁白原文，3-5 个金句 + 展开}}

## Line 6 — 方法实操 (Frame N)

**Time:** {{v}} – {{u}}s
**Delivery:** {{例：干脆利落，有步骤感}}

    {{方法实操旁白原文}}

## Line 7 — 结尾引导 (Frame N+1)

**Time:** {{u}} – {{t}}s
**Delivery:** {{例：温暖、真诚，像朋友告别}}

    {{结尾引导旁白原文，≤30 字}}

---

## 写作约束

| 约束 | 要求 |
|------|------|
| 总字数 | ≤570 字（1.2 倍速下正文 ≤195 秒） |
| 结构 | 钩子 → 扎心场景 → 引入书 → 场景演绎 → 观点拆解 → 方法实操 → 结尾引导（详见 `references/shot-structure.md`） |
| 引入书 | 必须含作者姓名/国籍/领域地位 + 书籍领域地位/销量 |
| 单句长度 | ≤20 字，口语化，可断句 |
| 安全 | 无医疗承诺、无"治好/一定/必须"等绝对化用词、不贬低读者 |
| 结尾 | 给一个具体可执行的小动作 + 一句互动提问 |

## 与分镜的关系

- 每个 `## Line N` 对应 STORYBOARD.md 的一个或多个 `## Frame N`。
- 缩进块里的文本是**唯一喂给 TTS 的内容**，其余都是给人看的注释。
- `**Time:**` 只是预估参考，Step 5 会用音频静音检测算出真实时间轴，覆盖这里的值。
- 另需产出一份单行纯文本 `voiceover-text.txt` 供 TTS 脚本读取（去掉所有 markdown 标记）。
