# 动效配方卡

> 来源：从 video-shotcraft 的 104 张镜头配方卡中，挑选适合图书带货视频（日系软萌 anime 水彩插画 + hyperframes GSAP）的动效，移植为 GSAP seek-safe 实现。
>
> 每张卡 = 意图 + 动效核心 + 参数表（含调校值）+ GSAP 实现 + 已知坑。
>
> **使用方式**：Step 8（动效设计）时按场景查卡，复制 GSAP 代码到 `build.mjs` 的 tweens 数组。参数是调校过的起点值，按镜头时长微调。

## 目录

- [背景运镜](#背景运镜)
- [金句入场](#金句入场)
- [转场](#转场)
- [环境动效](#环境动效)
- [品牌角标](#品牌角标)

---

## 背景运镜

### Ken Burns 推拉（基础）

**意图**：给静态插画注入呼吸感，避免纯静帧。

**动效核心**：整层 `scale` 缓慢变化，`transformOrigin` 锚定视觉重心。

| 参数 | 值 | 手感 |
|------|-----|------|
| scale 范围 | `[1.0, 1.06]` 或 `[1.06, 1.0]` | 推入或拉出，相邻帧反向 |
| origin | `"50% 50%"` 或偏移（如 `"55% 42%"`） | 锚定主体 |
| duration | = 镜头时长 | 全程缓慢 |
| ease | `"none"` | 匀速推拉（Ken Burns 的匀速是预期行为，不违反 R2） |

```js
// build.mjs
tweens.push(`  tl.set("#scene-N .scene-media", { transformOrigin: "50% 45%" }, ${start});`);
tweens.push(`  tl.fromTo("#scene-N .scene-media", { scale: 1 }, { scale: 1.04, duration: ${duration}, ease: "none" }, ${start});`);
```

**已知坑**：scale 过大会暴露边缘 → 给 scene 容器加 `data-layout-allow-overflow`；相邻帧推拉方向必须交替（不能连续推入）。

### Ken Burns 平移

**意图**：横向移动视线，适合宽幅画面。

| 参数 | 值 |
|------|-----|
| xPercent | `[0, 5]` 或 `[0, -5]` |
| scale | `[1, 1.05]`（配合平移轻微放大避免露边） |

```js
tweens.push(`  tl.fromTo("#scene-N .scene-media", { scale: 1, xPercent: 0 }, { scale: 1.05, xPercent: 5, duration: ${duration}, ease: "none" }, ${start});`);
```

---

## 金句入场

### ink 缩放弹入（概念镜/书页）

**意图**：金句像墨水渗透纸面，有重量感地浮现。

**来源**：改编自 video-shotcraft `paper-title-card`（凸版印刷标题）。

| 参数 | 值 | 手感 |
|------|-----|------|
| scale | `[0.8, 1.0]` | 从小到大，有弹性 |
| opacity | `[0, 1]` | 渐显 |
| duration | `0.8s` | 不拖沓 |
| ease | `"back.out"` | 轻微回弹，模拟纸张弹性 |

```js
tl.fromTo("#quote-N .quote-inner",
  { opacity: 0, scale: 0.8 },
  { opacity: 1, scale: 1, duration: 0.8, ease: "back.out" },
  quoteStart
);
```

### note 上滑浮入（实景镜/便签）

**意图**：金句像便签贴上来，轻盈。

| 参数 | 值 | 手感 |
|------|-----|------|
| y | `[16, 0]` | 从下方 16px 上移 |
| opacity | `[0, 1]` | 渐显 |
| duration | `0.7s` | 利落 |
| ease | `"power2.out"` | 自然减速 |

```js
tl.fromTo("#quote-N .quote-inner",
  { opacity: 0, y: 16 },
  { opacity: 1, y: 0, duration: 0.7, ease: "power2.out" },
  quoteStart
);
```

**已知坑**：ink 的 `back.out` 回弹不能太大（scale 起始不低于 0.8），否则文字晃眼。

---

## 转场

### 交叉淡入淡出（默认转场）

**意图**：相邻帧平滑过渡，不硬切。

| 参数 | 值 |
|------|-----|
| opacity | 新帧 `0→1` + 旧帧 `1→0` |
| duration | `0.6s` |
| ease | `"power1.inOut"` |

```js
// 非首帧场景淡入（build.mjs）
tweens.push(`  tl.fromTo("#scene-N", { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "power1.inOut" }, ${start});`);
```

**规则**：首帧不淡入（直接显示）；i2v 视频帧不参与交叉淡入（视频有自己的播放过渡）。

### 光束扫过（情绪转折）

**意图**：用一束光划过画面，标记情绪转折（如从扎心场景转入引入书）。

**来源**：改编自 video-shotcraft `mirror-sweep`（镜面扫光）。

| 参数 | 值 |
|------|-----|
| 元素 | `.beam` 或 `.mirror-sweep`（linear-gradient 条带） |
| xPercent | `[-40, 130]`（从左外到右外） |
| opacity | `[0.55, 0]`（进入时渐显，划过后渐隐） |
| duration | `4–5s` |
| ease | `"sine.inOut"` |

```js
tl.fromTo("#scene-N .mirror-sweep", { xPercent: -40, opacity: 0 },
  { xPercent: 130, opacity: 0.55, duration: 4.5, ease: "sine.inOut" }, start);
tl.to("#scene-N .mirror-sweep", { opacity: 0, duration: 3, ease: "sine.in" }, start + 1.5);
```

---

## 环境动效

### 尘埃浮动

**意图**：光束中的细小尘埃，营造氛围。

| 参数 | 值 | 手感 |
|------|-----|------|
| 元素 | N 个 `.mote`（纯色圆 + box-shadow） |
| yPercent | `[0, -46]`（上飘） |
| opacity | `[0, 0.55–0.85]`（渐显渐隐） |
| duration | `4–7s`（每个不同） |
| 相位错开 | 起始时间各偏移 `0.1–0.4s` | 关键，同步动显得机械 |

**已知坑**：**禁用 `radial-gradient`**，大量 gradient 触发黑帧缺陷。用纯色 `background` + `box-shadow`。

### 光束呼吸

**意图**：暖光忽明忽暗，像自然光线变化。

| 参数 | 值 |
|------|-----|
| opacity | `[0.55, 0.85]` |
| yoyo | `true` |
| repeat | `Math.max(0, Math.floor(duration / cycle) - 1)`（有限次，禁 `-1`） |
| ease | `"sine.inOut"` |

### 纸张呼吸

**意图**：整层极缓的缩放，模拟纸张的细微起伏。

| 参数 | 值 |
|------|-----|
| scale | `[1.0, 1.008]` | 极微小，不喧宾夺主 |
| ease | `"sine.inOut"` |
| yoyo + repeat | 同上（有限次） |

---

## 品牌角标

### 角标持续显示

**意图**：品牌 logo 在左上角全程显示，建立品牌记忆。

| 参数 | 值 |
|------|-----|
| 位置 | `x: 40, y: 40` |
| 尺寸 | `200 × 50px` |
| opacity | `0.85` |
| 实现 | `class="clip"` + GSAP `x/y` transform |

详见 `SKILL.md` Step 0 品牌角标显示规则。

---

## seek-safe 硬约束

所有动效必须遵守（详见 `references/hyperframes-usage.md`）：

| 禁止 | 替代 |
|------|------|
| `repeat: -1` | `Math.max(0, Math.floor(dur / cycle) - 1)` |
| `Math.random()` | 构建时用固定种子算好，写死 |
| `Date.now()` / `setTimeout` | 改写成 tween |
| CSS `animation: infinite` | 改用 GSAP tween |
| 动 `left` / `top` | 用 `x` / `y` transform |
| 动 `display` / `visibility` | 用 `opacity` |

可动属性：`opacity`、`x`、`y`、`scale`、`rotation`、`color`、`backgroundColor`、`transforms`。
