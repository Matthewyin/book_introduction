---
version: 1

# 项目级覆盖 —— book-video-pipeline（竖版书籍短视频）
#
# 为什么需要这份文件：
#   用户级 ~/.baoyu-skills/baoyu-image-gen/EXTEND.md 是 default_provider: zai +
#   default_aspect_ratio: "16:9"。在本项目里若不覆盖，任何没显式钉参数的调用都会
#   静默出 16:9 横图，而且 zai 不支持 --ref。
#
# 注意：scripts/genimage.py 已经在命令行显式钉死 --provider 和 --size，
#       本文件是第二道保险，用于手工直接调 baoyu-image-gen 的场合。

default_provider: minimax   # 本机可用的生图 key 只有 GPTSAPI_KEY / MINIMAX_API_KEY，
                            # 其中只有 minimax 支持 --ref（subject_reference）
default_quality: 2k
default_aspect_ratio: "9:16"
default_image_size: null

default_model:
  minimax: image-01         # 支持 subject_reference，用于跨镜人物一致性
---

# book-video-pipeline 生图偏好

## 画幅陷阱（实测记录）

MiniMax provider 的 body 构造是 `if (aspect_ratio) {...} else if (size) {...}`
（`scripts/providers/minimax.ts:140`）——**两个都给时 `size` 被忽略**，
只按 `aspect_ratio` 出 **720×1280**，拉伸到 1080×1920 会糊。

所以要足尺寸必须**只给 `--size 1080x1920`，不要同时给 `--ar 9:16`**。
`genimage.py` 的 `AR_TO_SIZE` 映射已处理这一点。

## 输出格式陷阱（实测记录）

MiniMax 不管输出扩展名写的是什么，一律返回 **JPEG** 字节流。落成 `.png`
就是"假 PNG"。`genimage.py` 的 `ensure_png()` 会用 `sips` 就地转成真 PNG。

## 通道分工

| 场景 | 通道 | 原因 |
|------|------|------|
| 常规场景插画（无参考图） | gptsapi + gpt-image-2 | 中文渲染好，固定 1K，带卡死检测重试 |
| 跨镜人物一致性（有参考图） | baoyu-image-gen + minimax | gptsapi 接口不支持参考图 |

统一入口：`python3 book-video-pipeline/scripts/genimage.py`，按有无 `--ref` 自动路由。
