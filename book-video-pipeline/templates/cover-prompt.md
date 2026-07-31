# 封面主视觉提示词模板（无字）

> 封面职责分离：本文件只生成 **无字 AI 主视觉图**，书名/钩子/排版由
> Canva 完成（见 `cover-design.md`）。生图模型严禁写任何文字。
> 输出：`cover/cover-art.png`，走 dreamina ref 通道（含主角定妆 ref）。

## 输出规格

- 尺寸：3:4（`--ar 3:4`；dreamina Seedream 出原生 2k，Canva 侧缩到 1080×1440）
- 文件：`03-assets/cover/cover-art.png`
- 后端：`--charRef assets/protagonist-base/girl-ref.png` → ref_backend（dreamina），锁主角形象

## 生成命令

```bash
python3 scripts/genimage.py \
  --style templates/styles/people/cute-anime-girl.md \
  --promptfiles 03-assets/cover/cover-art.scene.md \
  --image 03-assets/cover/cover-art.png --ar 3:4 \
  --charRef assets/protagonist-base/girl-ref.png
```

## 主视觉 prompt 硬约束（写进 scene 文件）

1. **顶部 40% 干净留白**：上部是纯净纯色/柔和渐变背景区，不画任何物体、
   文字、图案。这是软约束——Canva 模板的书名区自带 scrim，不依赖它。
2. **无任何文字**：画面中禁止出现文字、字母、书名、标语（生图文字必糊）。
3. **主角在场**：含主角（带定妆 ref），形象跟随定妆图。
4. **书作为道具**：主角手持或桌面摆一本素面书（封面上无字），与书名呼应。
5. **风格一致**：跟随风格卡（cute-anime-girl），色板内取色，无表外 hex。
6. **情绪来自该集角度**：如 ep003 非暴力沟通 = 安静沟通、暖光、和解感。

## 构图参考

- 主角侧坐/低头看书，暖色台灯，画面重心在下半部（书名区会被 Canva 覆盖）。
- 上半部留白区可以是纯色或从主体延伸的柔和渐变，方便文字压上后对比清晰。
- 底部 35% 不必预留纯色——Canva 的 scrim 色带兜底。
