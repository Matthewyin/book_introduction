# A 线·金句流字幕样式规范

> 金句流的核心视觉是**金句大字字幕**——金句本身就是画面主体，实拍素材只做氛围烘托。

## 字幕样式

| 项目 | 值 | 说明 |
|------|-----|------|
| 位置 | **垂直居中偏上**（画面上 1/3 处） | 与 B 线底部字幕区分，金句占视觉 C 位 |
| 字号 | **72px**（≥3.7% 帧高） | 比 B 线 48px 大一档，突出金句冲击力 |
| 颜色 | **暖白 #FFF8F0** | 暖调，不刺眼 |
| 描边 | 暖棕 #8B6F47，四方向 text-shadow 各 2px | 温润边框，不用黑色硬描边，靠描边保证可读性 |
| 对齐 | 水平居中（Alignment=2 垂直方向上移到 1/3 处） | — |
| 背景 | **透明**（无底条、无 scrim、无色块） | 金句直接浮在实拍素材上，画面通透；可读性由描边保证 |
| 行宽 | 每行 ≤14 字，超长换行 | 金句短，通常 1-2 行 |
| 显示时长 | 每句 ≥3 秒 | 金句要让人读完、记住 |
| 字幕领先 | 领先旁白 0.3-0.5 秒 | 观众先看到再听到 |

## 字幕与画面的关系

```
┌──────────────────────┐
│                      │ ← 顶部留白（实拍素材暖光区）
│   金句第一行           │ ← 透明背景 + 暖白大字 + 暖棕描边（上 1/3）
│   金句第二行           │
│                      │ ← 中部（实拍主体：山水/自然）
│                      │
│                      │
│                      │ ← 底部（实拍近景/光斑）
└──────────────────────┘
```

## hyperframes 实现

字幕写在 composition.html 的独立 `<div>` 图层（**背景透明**，靠描边保证可读性）：

```html
<div class="quote-subtitle" data-hf-track="subtitle"
     style="position:absolute; top:22%; left:6%; right:6%; text-align:center;
            font-size:72px; font-weight:700; color:#FFF8F0; line-height:1.4;
            text-shadow:-2px -2px 0 #8B6F47, 2px 2px 0 #8B6F47,
                       -2px 2px 0 #8B6F47, 2px -2px 0 #8B6F47;">
  {{金句文本}}
</div>
```

## 书封快闪开头（t=1.0-4.0s，品牌片头之后）

品牌片头（1s）结束后，先快闪 10 本书封（每本 0.1s），再落定到本集书封，让观众第一眼知道这是读书账号、今天要讲哪本书。

### 快闪段（t=1.0-2.0s）

| 项目 | 值 |
|------|-----|
| 书封来源 | 书封库 `assets/book-covers/` 随机 10 本（排除本集书），**先去白边**（`trim_whitespace.py`） |
| 每本时长 | **0.1s**（快闪翻飞节奏） |
| 书封尺寸 | height 520px，width auto，max-width 520px |
| 书封容器 | **毛玻璃卡片**（flex 包裹，宽度自适应贴住书封）：`backdrop-filter: blur(16px)` + `background: rgba(255,255,255,0.12)` + `border-radius: 16px` + `box-shadow: 0 8px 32px rgba(0,0,0,0.3)` + `padding: 288px` |
| 快闪段背景 | **静帧**（从视频抽一帧 PNG，避免背景运动与快速切换产生边框错觉） |
| 动效 | 每本 `opacity 0→1` + `scale 0.9→1` + `x 偏移→0`，0.06s，`power2.out`；0.1s 后 `opacity→0` |

```html
<div id="flash-N" class="glass-card clip" data-start="1.0" data-duration="0.1" data-track-index="N">
  <img class="flash-cover" src="03-assets/book-书名.png" />
</div>
```

```css
.glass-card {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  z-index: 5; pointer-events: none;
  display: flex; justify-content: center; align-items: center;
  padding: 288px;
  -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px);
  background: rgba(255,255,255,0.12);
  border-radius: 16px; border: 1px solid rgba(255,255,255,0.2);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  opacity: 0;
}
.flash-cover { display: block; height: 520px; width: auto; max-width: 520px; object-fit: contain; }
```

```js
const xOff = [40, -35, 50, -45, 30, -50, 45, -30, 55, -40]; // 固定种子
for (let i = 0; i < 10; i++) {
  const t = 1.0 + i * 0.1;
  const sel = `#flash-${i}`;
  tl.set(sel, {opacity: 1, scale: 0.9, x: xOff[i]}, t);
  tl.to(sel, {scale: 1.0, x: 0, duration: 0.06, ease: "power2.out"}, t);
  tl.set(sel, {opacity: 0}, t + 0.1);
}
```

### 本集书封落定（t=2.0-4.0s）

| 项目 | 值 |
|------|-----|
| 书封高度 | 画面 44% |
| 入场 | `scale 0.7→1 + opacity 0→1`，0.5s，`back.out(1.3)` |
| 停留 | 1.5s |
| 书名 overlay | 画面上方 14%，书名 72px 加粗 + 作者 38px |
| 退场 | `scale→1.15 + opacity→0`，0.3s，`power2.in` |
| 背景 | 恢复云海视频流动 |

```js
tl.fromTo("#final-cover", {opacity: 0, scale: 0.7},
  {opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.3)"}, 2.0);
tl.fromTo("#title-overlay", {opacity: 0, y: -20},
  {opacity: 1, y: 0, duration: 0.4, ease: "power2.out"}, 2.3);
tl.to("#final-cover", {scale: 1.15, opacity: 0, duration: 0.3, ease: "power2.in"}, 3.7);
tl.to("#title-overlay", {opacity: 0, duration: 0.3, ease: "power2.in"}, 3.7);
tl.set("#final-cover", {opacity: 0}, 4.0);
tl.set("#title-overlay", {opacity: 0}, 4.0);
```

## 字幕时间轴

时间轴由配音音频的静音检测驱动（ffmpeg silencedetect）：
1. TTS 生成 voiceover.wav（含引入句"今天分享的书籍是..."）
2. ffmpeg silencedetect 检测每句之间的停顿
3. 每句金句的起止时间 = 停顿间隔
4. 字幕出现时间 = 金句开始 - 0.3s（领先）
5. 字幕消失时间 = 金句结束 + 0.5s（尾音留白）
6. **引入句不配字幕**（书封落定段的书名+作者 overlay 已提供文字信息）
