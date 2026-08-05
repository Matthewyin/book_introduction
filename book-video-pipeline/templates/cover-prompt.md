# 封面主视觉提示词模板（双轨 · 无字 · dreamina_text Seedream 5.0）

> 统一封面职责分离：**AI 出画（无字主视觉），本地 PIL 排版出字（书名/钩子）**。
> 本文件是主视觉的生成规范（已验收：ep003 落地 `03-assets/cover/`）。
> 后端固定 **dreamina_text（Seedream 5.0 text2image，9:16/2k）**：全风格覆盖，
> fallback 为 openrouter（GPT Image 2）。

## 双轨规则：封面风格跟随视频风格

**视频写实→封面写实摄影；视频动漫→封面动漫插画。** 根据本集视频选定的风格卡决定：

| `--art` | 视频风格卡 | 封面 prompt 文件 | 封面底图 |
|---------|-----------|-----------------|---------|
| `realistic`（默认） | `cinematic-girl.md`（写实人设） | `prompts/cover-3x4-realistic.md` | `cover-3x4-realistic.png` |
| `anime` | `cute-anime-girl.md`（动漫人设） | `prompts/cover-3x4-anime.md` | `cover-3x4-anime.png` |

两套风格共用相同的三分区布局 + 暖调色板 + 严禁人物 + 无字约束，
只在表现手法上区分（写实摄影质感 vs 动漫插画质感）。

## 输出规格

| 画幅 | 尺寸 | 用途 | 文件 |
|------|------|------|------|
| 3:4 | 1080×1440 | 小红书主图 | `03-assets/cover/cover-final.png` |
| 9:16 | 1080×1920 | 抖音/视频号 | `03-assets/cover/cover-final-9x16.png` |

统一封面存 `assets/cover-image/`（系列共用，可复现 prompt 同目录 `prompts/`）；
落地到单集时复制到 `03-assets/cover/`。

## 生成命令（dreamina_text 主力 · Seedream 5.0）

主力走 `scripts/genimage.py`（薄分发层，按 `pipeline.yaml` 路由到 dreamina text2image）：

```bash
# 写实版（视频用写实人设时）
python3 scripts/genimage.py \
  --promptfiles assets/cover-image/prompts/cover-3x4-realistic.md \
  --image assets/cover-image/cover-3x4-realistic.png --ar 3:4
python3 scripts/genimage.py \
  --promptfiles assets/cover-image/prompts/cover-9x16-realistic.md \
  --image assets/cover-image/cover-9x16-realistic.png --ar 9:16

# 动漫版（视频用动漫人设时）
python3 scripts/genimage.py \
  --promptfiles assets/cover-image/prompts/cover-3x4-anime.md \
  --image assets/cover-image/cover-3x4-anime.png --ar 3:4
python3 scripts/genimage.py \
  --promptfiles assets/cover-image/prompts/cover-9x16-anime.md \
  --image assets/cover-image/cover-9x16-anime.png --ar 9:16
```

生成后贴 logo 品牌卡（`cover-compose.py --base --art <style>`）。
dreamina CLI 已 OAuth 登录（`dreamina login`），不读 API key。

## 主视觉 prompt 硬约束（两风格共用）

### 结构：Z 轴三分区布局（两风格共用）

提示词用**三分区布局**组织：每区写清**高度占比 + 内容 + 光效**，元素用
"必须清晰可见"清单列举。模板见 `assets/cover-image/prompts/` 对应文件。

1. **顶部区（3:4 ≈38% / 9:16 ≈42% 高）· 书名排版留白区**：暖奶油色墙面 /
   暖橘色天空自然向上延伸，暖光漫射成柔金色光晕；**两缕半透明米白色
   薄纱窗帘垂落，暖光透过形成柔金色光晕**——让留白是场景自然的一部分，不是
   空出来的带子。色调统一、干净、无任何物体文字。
2. **中部区（≈35%）· 窗边桌面主场景**：暖橘色阳光透过窗户洒进来，光线
   温暖柔和如裹蜂蜜；摊开的书（左中/中上，暖白书页）+ 蜂蜜柠檬茶（杯壁水珠、
   杯口热气）+ 暖琥珀色小台灯（灯罩透柔金光晕）。9:16 时书/茶/灯沿中轴上下
   分布、重心略偏下。
3. **底部区（≈25%）· 桌面近景**：小绿植（左下，叶片泛金边——唯一绿色点缀、
   面积小）+ 暖棕色木桌面边缘 + 两三处柔和金色光斑。

### 硬约束（两风格共用，不随分区写法变化）

- **最高优先级 · 严禁人物**：画面中严禁任何人形、人物、人影、剪影、手。
- **底图完全无字**：书名/钩子/作者全部由本地 PIL 排版层（`cover-compose.py`）
  叠加。底图本身任何区域严禁文字/字母/数字/书名/标语/水印/logo——**顶部留白区必须无字**。
  书页也保持空白（无任何字）。
- **暖调配色（两风格共用）**：暖奶油/暖琥珀/暖金/暖棕为主，柔粉点缀。
  情绪温暖治愈。**禁止大面积冷色（蓝/绿/薄荷/青）**。绿植面积要小，被暖色包围。

### 风格差异（两风格唯一的分歧点）

| | `realistic`（写实摄影） | `anime`（动漫插画） |
|---|---|---|
| 表现手法 | 柔和自然光、浅景深、真实材质纹理（木纹/纸纹/玻璃/金属）、轻微胶片颗粒 | 柔和圆润线条、扁平色块加轻渐变、非写实 |
| 禁止 | 动漫/插画/3D/扁平矢量 | 写实摄影/3D/厚涂油画/扁平矢量 |
| 参考风格卡 | `templates/styles/warm-still-life.md` | `templates/styles/people/cute-anime-girl.md`（色板一致，但无人物） |

## 验收清单（每张过）

- [ ] 无任何人形（最优先）
- [ ] 画面风格与视频风格一致（视频写实用 realistic，视频动漫用 anime）
- [ ] 一体式留白：垂直剖面连续无断点，不是空出来的带子；纱帘柔光自然
- [ ] 三区齐全：顶部留白 / 中部主场景 / 底部近景，各占比例大致符合
- [ ] 暖调治愈氛围在（蜂蜜柠檬茶/暖琥珀台灯光晕/暖白书页/暖橘夕阳/小绿植点缀）
- [ ] 底图完全无字（书页也空白），文字全部走 PIL 排版层
- [ ] 顶部书名区干净无字
- [ ] 真 PNG、尺寸对齐（1728×2304 / 1440×2560，2K）

## 合成（出字层，无 Canva）

模板验收后**不再逐集重生成画面**：每集封面 = 模板 + 本地排版层
（`scripts/cover-compose.py --art <style>`，文字 100% 保真），规格见 `cover-design.md`。
模板更新流程：改 prompt → 重生成到 `assets/cover-image/` → 全系列生效。

## Few-shot 范文（校准出图质量）

重新生成母版时，**先读 `assets/cover-image/prompts/cover-examples.md`**——收录已验收
封面的完整 prompt + 拆解要点。学它的**具体程度**：每个物体写到材质/动态/光照，
空间关系交代清楚谁遮挡谁，负面约束重复强调。新写 prompt 对照范文自检。
