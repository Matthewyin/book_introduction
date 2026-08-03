# 单镜场景内容字段骨架（DeepSeek 填这个）

> 本文件是 DeepSeek 写 `shot_00X.scene.md` 的模板。**只填画面内容，不写风格/色值/画幅/禁止项**
> （那些已在风格卡里）。重点：画面必须忠实翻译口播内容，主角必须在场，抽象概念不靠生图。

---

## 填写字段

```
Scene: {{环境 + 时间 + 光源。例：Night interior. A small apartment living room, dim, lit by a warm desk lamp and the cool glow of a phone screen.}}

Subject: {{主体的姿态与动作。例：A young woman curls up on a sofa, knees drawn to chest, one hand clutching the hem of her cardigan, head turned away from the light.}}

Props: {{2-4 件可辨识的道具。例：a phone on the floor, a torn notebook page, a mug with a cold tea stain.}}

Emotion: {{一到两个词。例：quiet panic, loneliness}}

Tone: {{cool / neutral / warm 三选一，对应 video-style-guide.md 的配比表}}

characters: {{true / false。true = 该镜含主角，生图时挂全局定妆图 ref}}
```

### 细节密度字段（`characters: false` 的镜头必须填，含主角镜头可选）

> 只对 **gptsapi 通道（无主角镜）** 强制。该通道是 GPT Image 2，吃细节密度——
> 写得越具体，出图完成度越高。含主角镜头走 dreamina Seedream，写简洁反而更稳。

```
Lighting: {{光源 + 方向 + 质感。例：warm morning sunlight from the left window,
  long soft shadows across the desk, dust motes floating in the light beam}}

Detail: {{环境/物件分项铺陈，3-5 条，每条一个可辨识特征。例：
  - a worn leather armchair with a folded knit blanket draped over one arm
  - a stack of books with coffee ring stains on the top cover
  - thin curtains billowing softly in the breeze
  - dust particles glowing in the sunbeam}}
```

**Detail 写法三原则**（借鉴 GPT Image 2 提示词库的"可见 N 个部件"式列举）：
1. **每件物品写到材质/状态/动态**，不写笼统的"a chair"——写"a worn leather armchair
   with a folded knit blanket draped over one arm"
2. **3-5 条即可**，不追求堆砌；每条服务画面氛围或口播内容，不写无关杂物
3. **空间关系交代**：谁在谁旁边/谁被谁遮住，写清遮挡关系

**反面 vs 正面**：

```
❌ Props: a book, a lamp, a cup
✅ Props: a closed book with a torn paper bookmark, a brass desk lamp tilted
   toward the page, a cup of tea with steam rising
✅ Lighting: warm evening light from a single desk lamp, deep shadows in the corners,
   a soft pool of light on the book only
```

---

## 口播→画面翻译三规则（必读，违反即废稿）

### 规则 1：主角全程在场（最重要）

**所有含人物的镜头，主角必须出现，标 `characters: true`。**

主角是叙事视角——口播全程是她的声音，画面里她也必须在场。绝不能出现观众不认识
的匿名角色独自承担情绪戏。

两种处理方式（按场景选）：

| 场景类型 | 主角的角色 | 写法 |
|---------|-----------|------|
| **重演场景**（口播在讲别人的故事：妈妈训孩子、夫妻争吵） | **见证者/旁观者**——在画面一角目睹这一切 | Subject 里先写场景中的人，再写主角在背景/侧边见证，带共情表情 |
| **讲解场景**（口播在讲书、讲方法、讲观点） | **主讲人**——直接面对观众讲解 | Subject 就是主角本人，温柔认真的姿态 |

**反面案例**（禁止这样写）：
```
❌ Subject: A mother points finger at her son.  ← 匿名陌生人演情绪戏，主角消失
✅ Subject: A mother scolds her son at the dinner table; the young woman
   (protagonist) stands in the doorway watching with a pained expression.  ← 主角见证
```

### 规则 2：抽象概念不靠生图

**方法论、概念对比、数字列举等抽象内容，生图只画"主角讲解的场景"，概念本身不画。**

抽象概念无法被画出来——让模型画"举起四根手指代表四步法""画两个气泡代表评判vs事实"，
出来的图会和口播内容毫无关系。这些概念交给 hyperframes 的文字图层/金句层表达。

| 口播内容 | ❌ 错误写法（硬画概念） | ✅ 正确写法（画讲解姿态） |
|---------|----------------------|------------------------|
| "四个词：观察、感受、需要、请求" | "主角举起四根手指，旁边四张词卡" | "主角坐在书桌前，温柔认真地讲解姿态，手势自然"（四步法留给文字层） |
| "从来不在乎是评判，不是事实" | "两个气泡，一个写评判一个写事实" | "主角见证夫妻争吵，表情若有所思"（概念留给金句层） |
| "气死你的是你对它的翻译" | "画一个翻译过程的示意图" | "主角看着争吵的夫妻，恍然大悟的表情"（洞察留给金句层） |

**原则**：生图负责"情绪场景 + 人物姿态"，文字层负责"概念表达 + 信息密度"。
如果一句口播的核心是抽象概念，scene.md 画主角对这个概念的**反应/情绪**，不画概念本身。

### 规则 3：重复角色保持一致

同一集内出现 2 次以上的非主角角色（如"妻子""丈夫"），用**简洁一致的外貌描述**锁定，
不要每次换不同描述。如果该角色出现 ≥3 次，考虑建单独定妆图 ref（见 `scene-prompt.md`）。

```
❌ shot_011: "a wife in a white blouse"
   shot_015: "a woman in a nightgown"        ← 同一个人，两个描述
✅ shot_011: "the wife (young woman, white blouse, long dark hair)"
   shot_015: "the wife (same woman, now in a nightgown)"  ← 明确是同一个人
```

---

## 检查清单（写完每个 scene.md 自查）

- [ ] 该镜含人物吗？含 → 主角是否在场（见证者或主讲人）？→ `characters: true`
- [ ] 口播这一句的核心是抽象概念吗？是 → 画主角的反应/讲解姿态，不画概念本身
- [ ] 有重复出现的非主角角色吗？有 → 外貌描述是否和前文一致？
- [ ] `characters: false` 的镜头：Lighting / Detail 是否填了（3-5 条具体铺陈）？
- [ ] 没写风格/色值/画幅/禁止项（那些在风格卡里）
