# A 线·金句流字幕样式规范

> 金句流的核心视觉是**金句大字字幕**——金句本身就是画面主体，实拍素材只做氛围烘托。

## 字幕样式

| 项目 | 值 | 说明 |
|------|-----|------|
| 位置 | **垂直居中偏上**（画面上 1/3 处） | 与 B 线底部字幕区分，金句占视觉 C 位 |
| 字号 | **72px**（≥3.7% 帧高） | 比 B 线 48px 大一档，突出金句冲击力 |
| 颜色 | **暖白 #FFF8F0** | 暖调，不刺眼 |
| 描边 | 暖棕 #8B6F47，**4px** | 温润边框，不用黑色硬描边 |
| 阴影 | 暖棕 1px，偏移 2px，模糊 3px | 柔和投影增加层次 |
| 对齐 | 水平居中（Alignment=2 垂直方向上移到 1/3 处） | — |
| 底条 | 半透明暖色矩形（rgba(139,111,71,0.35)），圆角 8px | 不用黑色 scrim，用暖色底条 |
| 行宽 | 每行 ≤14 字，超长换行 | 金句短，通常 1-2 行 |
| 显示时长 | 每句 ≥3 秒 | 金句要让人读完、记住 |
| 字幕领先 | 领先旁白 0.3-0.5 秒 | 观众先看到再听到 |

## 字幕与画面的关系

```
┌──────────────────────┐
│                      │ ← 顶部留白（实拍素材暖光区）
│   ┌───────────────┐  │
│   │ 金句第一行      │  │ ← 字幕底条 + 暖白大字（上 1/3）
│   │ 金句第二行      │  │
│   └───────────────┘  │
│                      │ ← 中部（实拍主体：书/台灯/茶杯）
│                      │
│                      │
│                      │ ← 底部（实拍近景/光斑）
└──────────────────────┘
```

## hyperframes 实现

字幕写在 composition.html 的独立 `<div>` 图层：

```html
<div class="quote-subtitle" data-hf-track="subtitle"
     style="position:absolute; top:25%; left:8%; right:8%; text-align:center;
            background:rgba(139,111,71,0.35); border-radius:8px; padding:20px;
            font-size:72px; color:#FFF8F0; -webkit-text-stroke:4px #8B6F47;
            text-shadow:2px 2px 3px rgba(139,111,71,0.5);">
  {{金句文本}}
</div>
```

## 开头定位帧（t=1.0-3.0s，品牌片头之后）

视频开头品牌片头（1s）结束后，显示**大字书名+作者**定位帧，让观众第一眼知道这是什么书。

### 书名 overlay

| 项目 | 值 |
|------|-----|
| 位置 | 画面上方 18% 处，水平居中 |
| 书名字号 | **68px** 加粗 |
| 书名颜色 | 暖白 #FFF8F0 |
| 书名描边 | 黑色 rgba(0,0,0,0.8) 四方向 text-shadow |
| 作者字号 | **38px** 不加粗 |
| 作者颜色 | 暖白 #FFF8F0 opacity 0.9 |
| 背景遮罩 | 上半部渐变黑色 rgba(0,0,0,0.35→0) |
| 显示时长 | t=1.0-3.0s，t=2.4 开始淡出（0.6s） |

```html
<div id="title-overlay" class="title-overlay clip"
     data-start="1.0" data-duration="2.0" data-track-index="80">
  <h1 class="book-title">《书名》</h1>
  <p class="book-author">作者/著</p>
</div>
```

```css
.title-overlay {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  display: flex; flex-direction: column; justify-content: flex-start;
  align-items: center; padding-top: 18%; z-index: 7; pointer-events: none;
  background: linear-gradient(to bottom, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.15) 40%, transparent 70%);
}
.book-title { font-weight: 700; font-size: 68px; color: #FFF8F0; letter-spacing: 4px; margin: 0;
  text-shadow: -2px -2px 0 rgba(0,0,0,0.8), 2px 2px 0 rgba(0,0,0,0.8), 0 0 16px rgba(0,0,0,0.6); }
.book-author { font-weight: 400; font-size: 38px; color: #FFF8F0; opacity: 0.9; margin-top: 12px;
  text-shadow: -1px -1px 0 rgba(0,0,0,0.8), 1px 1px 0 rgba(0,0,0,0.8); }
```

```js
// GSAP: t=2.4 书名+作者淡出
tl.to("#title-overlay", {opacity: 0, duration: 0.6, ease: "power1.inOut"}, 2.4);
```

## 书封特写叠入（t=3.0-5.0s）

定位帧淡出的同时，真实书封图片从右侧滑入，停留后淡出。

### 书封 overlay

| 项目 | 值 |
|------|-----|
| 来源 | `assets/book-covers/{书名}.png`（预建书封库，600×600） |
| 位置 | 画面居中 |
| 书封高度 | 画面高度 52%，宽度自适应 |
| 圆角 | 8px |
| 投影 | 0 8px 32px rgba(0,0,0,0.5) |
| 动画 | t=3.0 从右侧滑入(x:120→0)+淡入，t=4.4 淡出 |

```html
<div id="book-cover-overlay" class="book-cover-overlay clip"
     data-start="3.0" data-duration="2.0" data-track-index="81">
  <img src="../../../assets/book-covers/书名.png" alt="书封" />
</div>
```

```css
.book-cover-overlay {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  display: flex; justify-content: center; align-items: center;
  z-index: 8; pointer-events: none; opacity: 0;
}
.book-cover-overlay img {
  height: 52%; width: auto; max-width: 70%; object-fit: contain;
  border-radius: 8px; box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}
```

```js
// GSAP: 滑入+淡入 → 停留 → 淡出
tl.fromTo("#book-cover-overlay", {opacity: 0, x: 120},
  {opacity: 1, x: 0, duration: 0.6, ease: "power2.out"}, 3.0);
tl.to("#book-cover-overlay", {opacity: 0, duration: 0.6, ease: "power1.inOut"}, 4.4);
```

## 字幕时间轴

时间轴由配音音频的静音检测驱动（ffmpeg silencedetect）：
1. TTS 生成 voiceover.wav（含引入句"今天分享的书籍是..."）
2. ffmpeg silencedetect 检测每句之间的停顿
3. 每句金句的起止时间 = 停顿间隔
4. 字幕出现时间 = 金句开始 - 0.3s（领先）
5. 字幕消失时间 = 金句结束 + 0.5s（尾音留白）
6. **引入句不配字幕**（定位帧的书名+作者 overlay 已提供文字信息）
