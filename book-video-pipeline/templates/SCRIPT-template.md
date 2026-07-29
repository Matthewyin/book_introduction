# SCRIPT — {{书名}}·{{带货角度}}

> 锁定旁白文件。Step 3 审核通过后写入，Step 4 的 TTS 直接读取各节的缩进块。
> 格式对齐 hyperframes `hyperframes-core/references/script-format.md`。

**Voice:** {{voice_id}}（MiniMax，从 `assets/voices/voice-library.json` 选）
**Voice settings:** speed 1.2 · vol 1.0 · pitch 0 · model speech-02-hd
**Voice direction:** {{整体语气，例：清冷克制，像朋友深夜聊天，不煽情不说教}}

**Total chars:** {{字数}}
**Estimated duration:** {{预估秒数}}s（真实时长以 Step 4 生成的音频为准）

---

## Line 1 — 钩子 (Frame 1)

**Time:** 0.0 – {{x}}s（预估，Step 5 用静音检测替换为真实值）
**Delivery:** {{例：直接、平静，不要质问语气}}

    {{第一句旁白原文}}

## Line 2 — 扎心场景 (Frame 2)

**Time:** {{x}} – {{y}}s
**Delivery:** {{例：语速略快，堆叠焦虑感}}

    {{第二句旁白原文}}

## Line 3 — 引入书 (Frame 3)

**Time:** {{y}} – {{z}}s
**Delivery:** {{例：转暖，放慢，像递过来一本书}}

    {{第三句旁白原文，含书名和作者头衔}}

<!-- 按分镜数量继续，每帧一节 -->

---

## 写作约束

| 约束 | 要求 |
|------|------|
| 总字数 | ≤540 字（1.2 倍速下约 150-180 秒） |
| 单句长度 | ≤20 字，口语化，可断句 |
| 结构 | 钩子 → 扎心场景 → 引入书 → 场景演绎 → 观点拆解 → 方法实操 → 结尾引导 |
| 引入书的过渡 | 必须有承接句（"如果你也想摆脱……这本书会帮到你"），不能硬转 |
| 安全 | 无医疗承诺、无"治好/一定/必须"等绝对化用词、不贬低读者 |
| 结尾 | 给一个具体可执行的小动作 + 一句互动提问 |

## 与分镜的关系

- 每个 `## Line N` 对应 STORYBOARD.md 的一个 `## Frame N`。
- 缩进块里的文本是**唯一喂给 TTS 的内容**，其余都是给人看的注释。
- `**Time:**` 只是预估参考，Step 5 会用音频静音检测算出真实时间轴，覆盖这里的值。
- 另需产出一份单行纯文本 `voiceover-text.txt` 供 TTS 脚本读取（去掉所有 markdown 标记）。
