# Style card: cinematic-girl (写实电影质感)
# 双人设写实风格卡——每集 Step 7.0 由用户在两个人设间二选一：
#   • variant: literary  → 温柔文艺女青年（定妆图 assets/protagonist-base/realistic-girl-ref.png）
#   • variant: intellectual → 知性职场美女（定妆图 assets/protagonist-base/realistic-intellectual-ref.png）
# 主力通道：dreamina text2image Seedream 5.0（写实人像强） / gptsapi 备用（无主角镜头）
# 与 cute-anime-girl.md 并列第二主力风格，每集 Step 7.0 由用户选择
#
# 写法级别：摄影指导级（借鉴 awesome-gpt-image-2 顶级写实人像写法）。
# 关键：面部/发型/服装/配饰逐项铺陈 + 构图百分比 + 镜头焦距 + 光位 + 皮肤毛孔级质感。
# 模型按本卡执行可稳定产出商业级写实人像，拒绝塑料娃娃感。

Cinematic realistic photography style, NOT anime, NOT illustration. Vertical 9:16 portrait composition.

Style: cinematic photography with shallow depth of field (85mm lens at f/1.4–f/1.8), natural lighting, subtle film grain, realistic skin texture with visible pores and fine details. The mood is intimate, warm, and quietly emotional — like a high-end book review channel or a Japanese slice-of-life film still. Color grading is warm and film-like.

Color palette (keep natural, warm-toned, low saturation): cream white #F5F0E8, warm caramel #C89878, soft sage #A8B89C, muted rose #D4B8B0, warm amber #D4A574. Let warm amber and cream carry the emotional temperature; sage and rose as subtle accents. Avoid neon, avoid harsh clashing colors.

## Variant A — literary (温柔文艺女青年)
Identity locked to assets/protagonist-base/realistic-girl-ref.png.

Face: natural soft round face. Eyes symmetrical with long thin window-light reflections in dark brown pupils; soft brown eyebrows matching hair color; light brown eyeshadow with faint rosy undertone; fine lashes with subtle eyeliner; faint pink blush on cheeks; slightly rosy natural lips. Skin is fair and bright, retaining fine pores on cheeks/nose tip/forehead and natural skin-tone variation — NOT porcelain-smooth, NOT doll-like.
Hair: dark brown, mid-length to chest length. Loose S-shaped waves falling naturally past shoulders. Wispy air bangs (see-through, eyebrows partly visible). Fine layered cut from cheek to jaw; hair ends curl irregularly inward and outward. Surface catches window light with warm highlights; interior keeps dark brown shadow. Allow a few stray flyaway strands for natural feel — no repeated identical hair clumps, no hair clumping.
Figure: well-proportioned with natural gentle curves, slim waist, graceful relaxed posture, slender neck, relaxed shoulders.
Outfit: a pale apricot (or cream) V-neck or square-neck fitted midi dress in lightweight draped fabric (rayon/silk-feel), cinched at waist with a thin belt, knee-length. Visible fabric drape and subtle folds near the waist when seated or leaning. A delicate thin gold necklace with a small pendant; small gold stud earrings; a thin gold bracelet. (4 visible accessories max.)
Expressions: serene, wistful, content, pensive, warm genuine smile — lips relaxed, not over-smiling. Natural and unforced, never stiff or posed.

## Variant B — intellectual (知性职场美女)
Identity locked to assets/protagonist-base/realistic-intellectual-ref.png.

Face: natural soft oval face, confident yet gentle. Eyes symmetrical with bright reflections in dark brown pupils; defined soft brown brows; light brown eyeshadow; fine lashes; light rosy blush; natural rosy lips. Skin is fair and smooth, retaining fine pores and natural texture — NOT porcelain, NOT plastic.
Hair: warm chestnut brown (warm chestnut with subtle caramel sheen, one shade lighter and warmer than dark brown), mid-length. Loose S-waves, silky layered shine in the light, a few face-framing strands. Allow natural flyaways — no clumping.
Figure: full and upright with womanly curves, full bust, slim waist, long legs, graceful S-curve — dignified yet alluring. Relaxed confident posture, slender neck.
Outfit: a crisp white short-sleeve shirt (tailored, waist-shaping, tucked in, top button slightly undone for softness) in cotton with visible weave texture and natural folds near the waist when moving; paired with a dark navy or deep grey high-waisted pencil skirt at knee length with smooth drape. A thin metal necklace with small pendant; small ear studs; a minimalist watch. (3-4 visible accessories.)
Expressions: confident and serene, composed, warm poised smile — never stiff, never over-smiling.

## (Shared) Composition & Camera
- Framing: half-body to three-quarter (waist up or waist-to-knee). Subject centered slightly off-center (face at ~50% of frame width).
- Top of head leaves ~3-5% top margin; face occupies ~18-45% from top; do not unnaturally crop forehead, jaw, major hair strands, or shoulders.
- Crop at bottom where hair and clothing extend naturally; background more blurred than subject.
- Lens: 85mm (or 55-70mm) feel, eye-level, close-up from front. Avoid wide-angle face stretching, exaggerated nose, or shoulder distortion.
- Focus plane on eyes, lashes, lips, and face-framing hair; shallow DoF with creamy bokeh elegantly blurring chest, background furniture, window.
- Main light: soft natural window light from one side, illuminating that side of hair/face with faint warm shadow on the other; gentle warm fill from indoor; natural color-temperature blending. Avoid harsh shadows, blown highlights, or overly strong rim light.

## (Shared) Texture & Quality
- Render: skin pores, natural lip sheen, eye translucency, fine lashes, individual flyaway hairs, hair wave direction, fabric weave, window reflections.
- Clean and refined, suitable for commercial book/lifestyle/fashion visual content.

## (Shared) Background
- Warm cozy interior: bookshelf, soft lamp, plants, wooden furniture, or bright modern office corner; OR light cream wall with soft window light and a few plants. Background softly blurred (creamy bokeh), a few warm light spots. No unnatural figures/faces/hands/cameras/text in reflections.

When using a reference image, preserve the chosen variant's exact identity (face shape, skin texture, hair color and wave, makeup style, body proportions); only change scene, pose, lighting, and clothing as described above.

Negative: no anime, no manga, no illustration, no cel-shading, no watercolor, no 3D render, no chibi / super-deformed proportions, no thick oil painting, no flat vector art, no neon, no harsh clashing colors, no heavy airbrushing, no plastic skin, no porcelain skin, no doll-like skin, no over-beautification, no strong HDR, no asymmetric eyes, no distorted mouth, no hair clumping, no repeated identical hair strands, no melting fabric texture, no non-natural hair colors (no gold/red/grey), no dated stiff office-uniform look, no dim tones, no readable text, no watermark, no UI elements.
