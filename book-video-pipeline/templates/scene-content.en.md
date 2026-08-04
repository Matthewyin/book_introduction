# 单镜场景内容字段骨架（DeepSeek 填这个）

> 本文件是 DeepSeek 写 `shot_00X.scene.md` 的模板。**只填画面内容，不写风格/色值/画幅/禁止项**
> （那些已在风格卡里）。重点：画面忠实翻译口播内容是第一优先；主角按需出镜（三锚点）；
> 抽象概念不靠生图。

---

## 填写字段

```
Scene: {{环境 + 时间 + 光源。例：Night interior. A small apartment living room, dim, lit by a warm desk lamp and the cool glow of a phone screen.}}

Subject: {{主体的姿态与动作。例：A young woman curls up on a sofa, knees drawn to chest, one hand clutching the hem of her cardigan, head turned away from the light.}}

Props: {{2-4 件可辨识的道具。例：a phone on the floor, a torn notebook page, a mug with a cold tea stain.}}

Emotion: {{一到两个词。例：quiet panic, loneliness}}

Tone: {{cool / neutral / warm 三选一，对应 video-style-guide.md 的配比表}}

characters: {{true / false。true = 该镜含主角（按规则 1 判断口播主体是否为主角），
    生图时挂全局定妆图 ref 走 dreamina image2image；false = 无主角镜（他人/环境/概念/道具），
    走 dreamina text2image。默认 false——只有口播主体明确是主角时才标 true。}}
```

### 细节密度字段（`characters: false` 的镜头必须填，含主角镜头可选）

> 只对 **openrouter 通道（无主角镜）** 强制。该通道是 GPT Image 2，吃细节密度——
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

### 规则 1：内容优先，主角按需出镜（最重要）

**画面忠实翻译口播内容是第一优先级。主角是否出镜，取决于口播这一段的"主体是谁"——
而不是"每帧都必须有主角"。**

主角只在真正的情绪锚点出场（见下方"三锚点"），其余帧让画面本身去讲故事。
强行让主角在每帧出现，会绑架画面、削弱表现力、并导致审美疲劳。

#### 判断流程：先问"口播的主体是谁"

每一帧的口播内容，主体只有三种可能，对应三种画面处理：

| 口播主体 | 画面画什么 | characters | 举例 |
|---------|-----------|------------|------|
| **主角自己**（"我也曾这样""后来我懂了"） | 主角的回忆/独白/讲解 | `true` | 主角深夜刷手机、主角对镜头讲观点 |
| **他人/客观场景**（"很多人每天""妈妈在厨房"） | 那个场景本身（他人/环境） | `false` | 妈妈辅导孩子、雨夜空街道、加班的格子间 |
| **抽象概念/情绪**（"精神熵""内耗"） | 概念的视觉隐喻（道具/氛围/空镜） | `false` | 乱成一团的毛线、模糊的城市灯光、一堆药盒 |

**一句话判断**：这一帧口播的"主语"是谁？主语是主角→出镜；主语是他人/现象/概念→主角退场。

#### 主角出镜的"三锚点"原则

主角不必每帧在场，但要在三个关键情绪锚点出现，保证叙事视角不丢：

1. **开篇扎心帧**（前 1-2 帧）：主角出现在痛点场景，建立"这是她的故事"的代入感
2. **高潮转折帧**（中段 1 帧）：主角在"顿悟/转变"时刻出镜，情绪最浓
3. **结尾共鸣帧**（末帧）：主角与观众对话/共情，收束叙事

其余帧（通常占 60-75%）按口播内容自由画面——主角退场。

#### 反面 vs 正面

旧规则要求"主角见证他人故事"，新规则直接画他人故事本身：

口播："妈妈辅导孩子作业，崩溃到大吼。"
```
❌ Subject: A mother scolds her son; the young woman (protagonist) stands
   in the doorway watching with a pained expression.   ← 主角绑架画面，
   本该是妈妈的情绪戏，被稀释成主角的旁观日记
✅ Subject: A mother slams the homework book on the table, mouth open mid-shout,
   finger jabbing at the page; the child shrinks back, eyes reddening.
   characters: false                                     ← 直接呈现口播内容，
   妈妈的情绪完整传达，主角不在场（这是妈妈的故事，不是主角的）
```

口播："后来我也成了那样。刷手机到凌晨两点，停不下来。"
```
✅ Subject: The young woman (protagonist) lies on her side in bed, face lit
   blue by the phone screen, thumb scrolling, eyes half-open and exhausted.
   characters: true                                      ← 主语是"我"，
   主角出镜，这是她的自述
```

### 规则 2：抽象概念不靠生图

**方法论、概念对比、数字列举等抽象内容，生图只画"画面主体对概念的承载/反应"，
概念本身不画。**

抽象概念无法被画出来——让模型画"举起四根手指代表四步法""画两个气泡代表评判vs事实"，
出来的图会和口播内容毫无关系。这些概念交给 hyperframes 的文字图层/金句层表达。

| 口播内容 | ❌ 错误写法（硬画概念） | ✅ 正确写法 |
|---------|----------------------|------------|
| "四个词：观察、感受、需要、请求" | 主角举四根手指+四张词卡 | 主角坐书桌前认真讲解姿态（有主角）；**或** 一本翻开的书旁排好四支不同颜色的铅笔（无主角，概念隐喻） |
| "精神熵——你的注意力被撕碎" | 画大脑结构示意图 | **一团乱麻般的彩色毛线缠在椅背上，窗外光透进来**（无主角，视觉隐喻） |
| "从来不在乎是评判，不是事实" | 两个气泡写评判vs事实 | 妈妈指着孩子吼叫的场景（无主角，口播主体的情绪） |
| "气死你的是你对它的翻译" | 画翻译过程示意图 | 主角恍然大悟的表情（有主角，主语是"你"指主角） |

**原则**：生图负责"情绪场景 + 视觉隐喻"，文字层负责"概念表达 + 信息密度"。
如果该帧有主角，画主角对概念的反应；如果无主角，画概念的视觉隐喻（道具/氛围）。

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

- [ ] 口播的主体是谁？（主角自己 / 他人 / 概念）→ 决定 `characters: true/false`
- [ ] 主角出镜帧是否落在三锚点（开篇/高潮/结尾）？避免无意义出场
- [ ] 无主角帧的画面是否忠实呈现了口播内容（而非硬塞主角旁观）？
- [ ] 口播核心是抽象概念吗？是 → 画视觉隐喻或主体反应，不画概念图解
- [ ] 有重复出现的非主角角色吗？有 → 外貌描述是否和前文一致？
- [ ] `characters: false` 的镜头：Lighting / Detail 是否填了（3-5 条具体铺陈）？
- [ ] 没写风格/色值/画幅/禁止项（那些在风格卡里）
