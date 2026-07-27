# 视频技术规格

> 所有产出的视频必须满足此规格。

## 强制规格

| 项目 | 规格 | 容差 |
|------|------|------|
| 容器格式 | MP4 | — |
| 视频编码 | H.264 (libx264) | — |
| 音频编码 | AAC | — |
| 宽度 | 1080 px | ±0 |
| 高度 | 1920 px | ±0 |
| 帧率 | 30 fps | ±0 |
| 像素长宽比 | 1:1 (SAR 1:1) | — |
| 色彩空间 | yuv420p | — |
| 视频码率 | 5000 kbps | ±500 |
| 音频采样率 | 48000 Hz | — |
| 音频码率 | 192 kbps | — |
| 声道 | 立体声（stereo） | — |
| 最大时长 | 180 秒 | 硬上限 |
| 目标时长 | 150-170 秒 | 推荐范围 |

## 时长结构建议

```
开头钩子      5s   ( 3%)
场景演绎     45s   (27%)
观点拆解     60s   (36%)
方法实操     40s   (24%)
结尾引导     10s   ( 6%)
─────────────────────
合计        160s   (96%)  ← 目标
```

## ffmpeg 合成参数参考

```bash
ffmpeg \
  -framerate 30 \
  -i "scenes/shot_%03d.png" \
  -i "audio/voiceover.wav" \
  -i "audio/bgm.mp3" \
  -filter_complex "
    [0:v]scale=1080:1920,setsar=1,
    subtitles='subtitle.ass':force_style='FontName=Noto Sans CJK SC,FontSize=52,PrimaryColour=&H00D6D600,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=180'[v];
    [2:a]volume=0.15[bgm];
    [1:a][bgm]amix=inputs=2:duration=first:dropout_transition=0[a]
  " \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset medium -crf 18 \
  -profile:v high -level 4.0 \
  -pix_fmt yuv420p \
  -b:v 5000k -maxrate 5500k -bufsize 10000k \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart \
  -t 180 \
  "output.mp4"
```

## 关键参数说明

| 参数 | 值 | 说明 |
|------|-----|------|
| `-crf 18` | 恒定质量 | 视觉无损，文件适中 |
| `-preset medium` | 编码速度 | 质量与速度平衡 |
| `-profile:v high` | H.264 profile | 兼容性好 |
| `-pix_fmt yuv420p` | 像素格式 | 最大兼容性 |
| `-movflags +faststart` | moov atom 前置 | 支持边下边播 |
| `-t 180` | 硬截断 | 不超过 180 秒 |

## 字幕规格

| 项目 | 值 |
|------|-----|
| 格式 | ASS（高级字幕） |
| 字体 | Noto Sans CJK SC |
| 字号 | 52 |
| 颜色 | #FFD700（金黄） |
| 描边 | 黑色，2px |
| 阴影 | 1px |
| 对齐 | 底部居中（Alignment=2） |
| 底部边距 | 180px（约画面 1/3 处） |
| 每行最大字数 | 16 |
| 每条最长显示 | 4 秒 |

## 校验清单

产出视频后用 `validate-spec.py` 自动检查：

- [ ] 时长 ≤ 180s
- [ ] 分辨率 = 1080×1920
- [ ] 帧率 = 30fps
- [ ] 编码 = H.264
- [ ] 音频 = AAC 48kHz 立体声
- [ ] 文件 < 100MB（便于上传）
- [ ] faststart 已启用
