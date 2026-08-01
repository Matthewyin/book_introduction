# 封面主视觉 Prompt 范文（few-shot 校准）

> 本文件收录已验收封面的完整 prompt，供 gptsapi 重新生成母版时校准**具体程度**。
> 学的不是文案，是「场景细节写到什么粒度、约束怎么表达、空间关系怎么交代清楚」。
> 配合 `cover-prompt.md`（硬约束）使用。

---

## 范文 1：清爽阳光氛围版 3:4（已验收 · ep003 落地）

```
书评视频统一封面（小红书 3:4 竖版）。
【最高优先级】画面中严禁出现任何人形、人物、人影、剪影、手——绝对没有任何人物在场。
氛围：清爽、阳光、积极向上。明亮白天的窗边书桌，清晨阳光透过窗户洒进来，光线明亮温暖、干净通透；桌上一本摊开的书（书页在阳光下微微发亮）、一杯柠檬水（杯壁挂着水珠，清新明亮）、一部手机、一盆小绿植；窗外是蓝天、绿树与柔和的阳光。
【构图关键】整个画面是一幅完整连贯的空间，上下无缝衔接，不允许出现生硬的分界线或割裂的留白带：上方是明亮的浅色区——阳光漫射的浅蓝渐变天空/白色墙面自然向上延伸，色调统一、干净、没有多余物体，是场景中天然明亮安静的部分（书名排版将落在这里）；下方是窗边桌面场景，阳光、绿植、书桌物体与上方天空墙面属同一空间，延续一体。
【手机屏幕】手机屏幕不能是空白：屏幕上显示小号英文圆体字（如 "happy time"，柔和手写圆体，小字号），配一个简单的迷你图案（如小太阳或小绿芽），清新精致。
【书籍内页】摊开的书内页不能是空白：页面上有小号英文圆体字（如 "stay bright"、"good day"，柔和手写圆体，小字号）和简单的小插画（简笔画：小太阳、小花、小绿芽等，两三处点缀），书页在阳光下微微发亮。
【文字范围限制】除上述书内页与手机屏幕上的小号英文圆体字外，画面其余区域严禁出现任何文字、字母、数字、书名、标语、水印、图标、logo——顶部书名区必须保持无字干净。
情绪：清爽、积极、充满希望，不阴沉、不暧昧。
画风：日系可爱动漫插画，柔和圆润线条、扁平色块加轻渐变、非写实、非 3D。配色清爽明亮：天空蓝、薄荷绿、奶油白，阳光黄点缀。
```

### 拆解：为什么这个 prompt 有效

| 要点 | 写法 | 效果 |
|---|---|---|
| **人物禁止** | 用「最高优先级」+ 四个递进同义词（人形/人影/剪影/手） | gpt-image-2 对负面指令敏感，重复强调降低出错率 |
| **一体式留白** | 不写「留白」，写「场景自然延伸」「延续一体」「无缝衔接」 | 避免 AI 画出一条割裂的空白带 |
| **书/手机不空白** | 给具体英文范例（"happy time"/"stay bright"）+ 简笔画清单 | 空白书页会被 AI 当排版区乱写字，预填英文圆体字占位 |
| **文字范围锁定** | 「严禁任何文字…顶部书名区必须无字干净」 | 确保 PIL 排版区无干扰像素 |
| **具体程度** | 每个物体都写到「在阳光下微微发亮」「杯壁挂着水珠」 | 细节越具体，出图越可控 |

---

## 范文 2：清爽阳光氛围版 9:16（已验收 · ep003 落地）

与 3:4 版唯一差异在构图段：

```
（前半同范文 1）
【构图关键】……下方是窗边桌面场景，竖版构图：书、柠檬水、手机与绿植沿中轴上下分布，重心略偏下；阳光、绿植、书桌物体与上方天空墙面属同一空间，延续一体。
（后半同范文 1）
```

**竖版适配要点**：9:16 比 3:4 更窄更高，物体改为「沿中轴上下分布，重心偏下」，避免横向铺开被裁切。

---

## 范文 3：人物+书封特写版（已验收 · bookshot 模板）

> 用 `--template bookshot` 时需要此母版。**Q 版小美女 + 书封**，人物在右下做推荐手势，
> 书在左侧，顶部一体式留白区给文字层。完整 prompt 见 `prompts/cover-3x4-bookshot.md`。

```
3:4 vertical cover. Japanese anime illustration, soft watercolor style.

A cute anime girl (18-22) in the lower right, half-body, leaning forward with a warm
confident smile, right hand raised in a "presenting/recommending" gesture pointing toward
a book on the left. She has: soft oval face, big bright almond eyes, dark brown medium-long
wavy hair with a small pink hair clip, wearing a cream-white loose T-shirt, soft warm blush.

On the left-center: a psychology book standing upright, book cover has cream-white background
with abstract line decorations (NO text). Next to it: lemon water + small potted plant.

CRITICAL COMPOSITION — integrated top space (not a blank band):
The entire image is ONE continuous, seamless space. The top is NOT an empty whitespace belt
— it is the scene itself naturally extending upward: bright window wall and soft sky-gradient
continue upward, warm sunlight diffuses into cream-to-white gradient. NO dividing line.

Style: soft Japanese anime, non-realistic, non-3D. Palette: cream white, light wood, mint
green, soft pink blush, sunshine yellow. Low saturation.
No text anywhere. Book cover has only abstract patterns. Upper area must be text-free.
```

### 人物+书封特写版要点

- **允许 Q 版人物**（bookshot 专属例外，ambient 仍严禁人物）
- 人物在**右下角**做推荐手势，引导视线到左侧的书 → 带货感
- 书封**不写具体文字**（AI 写中文易错）→ PIL 排版层负责出字
- **一体式留白**：顶部是同一房间的墙面/窗光自然延伸，不是空出来的带子
- 人物和书在**下方 60%**，上方 35-40% 留给文字排版

---

## 新增 prompt 时的校准标准

写新 prompt 时对照范文自检：
1. **每个物体有没有具体描述**（材质/动态/光照），而非笼统的「一本书」
2. **空间关系有没有交代**（谁在前/谁在后/哪里延伸到哪里）
3. **负面约束有没有重复强调**（禁止人物至少写 3 个同义词）
4. **文字范围有没有锁定**（哪些区域可以有字、哪些绝对不能有）
5. **画幅适配有没有写**（3:4 横向铺开 vs 9:16 竖向中轴）
