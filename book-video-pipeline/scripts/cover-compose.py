#!/usr/bin/env python3
"""cover-compose.py — 本地封面排版合成（无 Canva，零 API 依赖）

以 assets/cover-image/ 下已验收的 2 张无字模板（cover-3x4.png / cover-9x16.png）
为底图，在顶部留白区排版：左上 logo 品牌卡、右上「好书推荐」、居中书名（黑体加粗）、
钩子（仿宋，严格适应屏宽不超界）、作者，生成该书的最终封面，保存到该书
03-assets/cover/ 目录。

文字 100% 保真（PIL 排版，不依赖 AI 渲染中文）。

用法:
  python3 scripts/cover-compose.py \
    --book-title 非暴力沟通 \
    --hook 你说的每句狠话，都在推开最亲的人 \
    --author 马歇尔·卢森堡 --episode EP03 \
    --out-dir episodes/ep003-非暴力沟通/03-assets/cover

配置（pipeline.yaml cover.*，可被 CLI 覆盖）:
  cover.template_dir  模板目录（含 cover-3x4.png / cover-9x16.png）
  cover.logo          左上角 logo 品牌卡路径（无则回退系列名文字）
  cover.corner_right  右上角文字（默认「好书推荐」）
  cover.font_title    书名黑体（默认系统 STHeiti Medium，加粗用描边）
  cover.font_hook     钩子仿宋（默认 FandolFang）
  cover.font_body     系列/作者/右上角（默认 LxgwWenKai 暖调）
  cover.out_3x4       3:4 输出文件名（默认 cover-final.png）
  cover.out_9x16      9:16 输出文件名（默认 cover-final-9x16.png）
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------- 配置

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import cfg  # noqa: E402

DEFAULT_TEMPLATE_DIR = Path.home() / "Coding/video/assets/cover-image"
DEFAULT_SERIES = "好书慢读"
DEFAULT_CORNER_RIGHT = "好书推荐"

FONT_FALLBACK_TITLE = [
    "/System/Library/Fonts/STHeiti Medium.ttc",      # 黑体
    "~/Library/Fonts/NotoSansSC-Bold.otf",           # 思源黑体加粗
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]
FONT_FALLBACK_HOOK = [
    "~/Library/Fonts/FandolFang-Regular.otf",        # 仿宋
    "~/Library/Fonts/NotoSansSC-Regular.otf",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]
FONT_FALLBACK_BODY = [
    "~/Library/Fonts/LxgwWenKai-Regular.ttf",        # 暖调
    "~/Library/Fonts/NotoSansSC-Regular.otf",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]

# 文字配色（暖深棕，压在浅暖留白区上对比清晰）
C_TITLE = (74, 46, 27, 255)
C_SHADOW = (58, 34, 15, 130)
C_HOOK = (92, 58, 32, 255)
C_META = (122, 92, 62, 235)
C_CORNER = (122, 92, 62, 255)

# 版式（以高度 H 的比例定位，3:4 与 9:16 通用）
LAYOUT = {
    "logo": {"x": 0.045, "y": 0.030, "w": 0.240},        # 左上：logo 品牌卡（放大）
    "corner": {"x": 0.950, "y": 0.038, "size": 0.030},   # 右上：「好书推荐」右对齐
    "ep": {"x": 0.950, "y": 0.076, "size": 0.022},       # 右上角下方：EP 集数
    "title": {"y": 0.160, "size": 0.105, "max_w": 0.86}, # 居中：书名（黑体不加粗，自动缩字号）
    "hook": {"y": 0.300, "size": 0.042, "max_w": 0.82},  # 居中：钩子（仿宋，严格不超宽）
    "author": {"y": 0.425, "size": 0.027},               # 居中：作者
}

# logo 品牌卡底卡（浅暖色，提亮暗色 lockup 的对比）
LOGO_CARD_FILL = (250, 243, 226, 215)
LOGO_CARD_PAD = 0.36  # 底卡内边距（相对 logo 高度）


def load_font(paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    for p in paths:
        q = Path(p).expanduser()
        if q.is_file():
            try:
                return ImageFont.truetype(str(q), size)
            except OSError:
                continue
    raise SystemExit(f"无可用字体（尝试过: {paths}）")


def fit_font_size(draw: ImageDraw.ImageDraw, text: str, font_paths: list[str],
                  max_w: int, start: int, floor: int) -> ImageFont.FreeTypeFont:
    """缩字号直至单行放得下（≥floor）。"""
    size = start
    while size > floor:
        f = load_font(font_paths, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return load_font(font_paths, floor)


def compose(template: Path, out: Path, spec: dict) -> None:
    im = Image.open(template).convert("RGB")
    W, H = im.size
    L = LAYOUT
    draw = ImageDraw.Draw(im, "RGBA")

    # ── 1) 左上：logo 品牌卡（浅暖底卡 + 放大提亮；无则回退「系列名 · EP」文字）──
    logo = spec.get("logo")
    if logo and logo.is_file():
        lg = Image.open(logo).convert("RGBA")
        lw = int(W * L["logo"]["w"])
        lh = int(lg.height * lw / lg.width)
        lg = lg.resize((lw, lh), Image.LANCZOS)
        pad = int(lh * LOGO_CARD_PAD)
        cx = int(W * L["logo"]["x"])
        cy = int(H * L["logo"]["y"])
        draw.rounded_rectangle(
            [cx - pad, cy - pad, cx + lw + pad, cy + lh + pad],
            radius=int(lh * 0.35), fill=LOGO_CARD_FILL)
        im.paste(lg, (cx, cy), lg)
    else:
        series_font = load_font(spec["font_body"], int(H * L["corner"]["size"]))
        series_text = f"{spec['series']} · {spec['episode']}" if spec["episode"] else spec["series"]
        draw.text((W * L["logo"]["x"], H * L["logo"]["y"]), series_text,
                  font=series_font, fill=C_META)

    # ── 2) 右上：「好书推荐」+ EP 集数（右对齐）──
    corner_font = load_font(spec["font_body"], int(H * L["corner"]["size"]))
    cr_text = spec["corner_right"] or DEFAULT_CORNER_RIGHT
    cw = draw.textlength(cr_text, font=corner_font)
    draw.text((W * L["corner"]["x"] - cw, H * L["corner"]["y"]), cr_text,
              font=corner_font, fill=C_CORNER)
    if spec["episode"]:
        ep_font = load_font(spec["font_body"], int(H * L["ep"]["size"]))
        ew = draw.textlength(spec["episode"], font=ep_font)
        draw.text((W * L["ep"]["x"] - ew, H * L["ep"]["y"]), spec["episode"],
                  font=ep_font, fill=C_META)

    # ── 3) 书名：黑体不加粗（常规字重，柔和投影），居中 ──
    title_font = fit_font_size(draw, spec["title"], spec["font_title"],
                               int(W * L["title"]["max_w"]),
                               int(H * L["title"]["size"]), int(H * 0.045))
    tw = draw.textlength(spec["title"], font=title_font)
    tx = (W - tw) / 2
    ty = H * L["title"]["y"]
    shadow = (W * 0.0015, H * 0.0025)
    draw.text((tx + shadow[0], ty + shadow[1]), spec["title"],
              font=title_font, fill=C_SHADOW)
    draw.text((tx, ty), spec["title"], font=title_font, fill=C_TITLE)

    # ── 4) 钩子：仿宋加粗（描边 fake-bold），严格适应屏宽（单行优先，绝不超出 max_w）──
    max_w = int(W * L["hook"]["max_w"])
    floor = int(H * 0.028)
    start = int(H * L["hook"]["size"])
    hook_font = fit_font_size(draw, spec["hook"], spec["font_hook"], max_w, start, floor)
    hook_stroke = max(1, int(H * 0.0014))  # 比初始(0)粗、比上一版(0.0022)细
    if draw.textlength(spec["hook"], font=hook_font) > max_w:
        # floor 仍超宽 → 折 2 行（每行仍需 ≤ max_w）
        line_h = hook_font.size * 1.4
        lines: list[str] = []
        cur = ""
        for ch in spec["hook"]:
            if draw.textlength(cur + ch, font=hook_font) <= max_w:
                cur += ch
            else:
                if cur:
                    lines.append(cur)
                cur = ch
        if cur:
            lines.append(cur)
        hy = H * L["hook"]["y"]
        for i, ln in enumerate(lines[:2]):
            lw = draw.textlength(ln, font=hook_font)
            draw.text(((W - lw) / 2, hy + i * line_h), ln, font=hook_font, fill=C_HOOK,
                      stroke_width=hook_stroke, stroke_fill=C_HOOK)
    else:
        hw = draw.textlength(spec["hook"], font=hook_font)
        draw.text(((W - hw) / 2, H * L["hook"]["y"]), spec["hook"],
                  font=hook_font, fill=C_HOOK, stroke_width=hook_stroke,
                  stroke_fill=C_HOOK)

    # ── 5) 作者：仿宋加粗，小字居中 ──
    author_font = load_font(spec["font_hook"], int(H * L["author"]["size"]))
    aw = draw.textlength(spec["author"], font=author_font)
    draw.text(((W - aw) / 2, H * L["author"]["y"]), spec["author"],
              font=author_font, fill=C_META, stroke_width=hook_stroke,
              stroke_fill=C_META)

    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    print(f"✓ {out.name}: {W}x{H} 书名「{spec['title']}」 钩子「{spec['hook']}」")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out-dir", type=Path, required=True, help="该书 03-assets/cover 目录")
    p.add_argument("--book-title", required=True, help="书名（≤10 字，不加《》）")
    p.add_argument("--hook", default="", help="钩子文案（≤12 字）")
    p.add_argument("--author", default="", help="作者/副标题")
    p.add_argument("--episode", default="", help="集数，如 EP03")
    p.add_argument("--series", default=None, help="系列名（默认读 config）")
    p.add_argument("--corner-right", default=None, help="右上角文字（默认「好书推荐」）")
    p.add_argument("--template-dir", type=Path, default=None,
                   help="模板目录（默认读 config）")
    p.add_argument("--logo", type=Path, default=None, help="logo 品牌卡路径（默认读 config）")
    p.add_argument("--font-title", default=None, help="书名黑体字体（默认读 config）")
    p.add_argument("--font-hook", default=None, help="钩子仿宋字体（默认读 config）")
    p.add_argument("--font-body", default=None, help="正文/系列/作者字体（默认读 config）")
    args = p.parse_args()

    tdir = args.template_dir or cfg.path("cover.template_dir") or DEFAULT_TEMPLATE_DIR
    out_3x4 = cfg.get("cover.out_3x4", "cover-final.png")
    out_9x16 = cfg.get("cover.out_9x16", "cover-final-9x16.png")

    def _fonts(key: str, fallback: list[str]) -> list[str]:
        v = cfg.get(f"cover.{key}")
        return [v] + fallback if v else fallback

    spec = {
        "title": args.book_title,
        "hook": args.hook,
        "author": args.author,
        "episode": args.episode,
        "series": args.series or cfg.get("cover.series_name", DEFAULT_SERIES),
        "corner_right": args.corner_right or cfg.get("cover.corner_right", DEFAULT_CORNER_RIGHT),
        "logo": args.logo or cfg.path("cover.logo"),
        "font_title": _fonts("font_title", FONT_FALLBACK_TITLE),
        "font_hook": _fonts("font_hook", FONT_FALLBACK_HOOK),
        "font_body": _fonts("font_body", FONT_FALLBACK_BODY),
    }

    t34 = tdir / "cover-3x4.png"
    t916 = tdir / "cover-9x16.png"
    if not t34.is_file() or not t916.is_file():
        raise SystemExit(f"模板缺失：{tdir} 下需要 cover-3x4.png 与 cover-9x16.png")

    compose(t34, args.out_dir / out_3x4, spec)
    compose(t916, args.out_dir / out_9x16, spec)
    print(f"完成：{args.out_dir}（{out_3x4} 3:4 + {out_9x16} 9:16）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
