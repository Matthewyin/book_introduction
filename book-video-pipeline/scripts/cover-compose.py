#!/usr/bin/env python3
"""cover-compose.py — 本地封面排版合成（无 Canva，零 API 依赖）

以 assets/cover-image/ 下已验收的 2 张无字模板（cover-3x4.png / cover-9x16.png）
为底图，在顶部留白区排版书名/钩子/作者/系列/集数，生成该书的最终封面，
保存到该书 03-assets/cover/ 目录。

文字 100% 保真（PIL 排版，不依赖 AI 渲染中文）。

用法:
  python3 scripts/cover-compose.py \
    --book-title 非暴力沟通 \
    --hook 你说的每句狠话，都在推开最亲的人 \
    --author 马歇尔·卢森堡 --episode EP03 \
    --out-dir episodes/ep003-非暴力沟通/03-assets/cover

配置（pipeline.yaml cover.*，可被 CLI 覆盖）:
  cover.template_dir  模板目录（含 cover-3x4.png / cover-9x16.png）
  cover.series_name   系列名
  cover.font_title    书名粗体字体路径
  cover.font_body     正文/钩子字体路径
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

FONT_FALLBACK_TITLE = [
    "~/Library/Fonts/NotoSansSC-Bold.otf",
    "~/Library/Fonts/NotoSansSC-Regular.otf",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
]
FONT_FALLBACK_BODY = [
    "~/Library/Fonts/LxgwWenKai-Regular.ttf",
    "~/Library/Fonts/NotoSansSC-Regular.otf",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
]

# 文字配色（暖深棕，压在浅暖留白区上对比清晰）
C_SERIES = (122, 92, 62, 235)
C_TITLE = (74, 46, 27, 255)
C_SHADOW = (58, 34, 15, 130)
C_HOOK = (92, 58, 32, 255)
C_AUTHOR = (122, 92, 62, 215)

# 版式（以高度 H 的比例定位，3:4 与 9:16 通用）
LAYOUT = {
    "series": {"x": 0.055, "y": 0.038, "size": 0.028},       # 左上：系列名 + EP
    "title": {"y": 0.160, "size": 0.105, "max_w": 0.86},     # 居中：书名（自动缩字号）
    "hook": {"y": 0.300, "size": 0.042, "max_w": 0.80},      # 居中：钩子（≤2 行）
    "author": {"y": 0.425, "size": 0.027},                   # 居中：作者
}


def load_font(paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    for p in paths:
        q = Path(p).expanduser()
        if q.is_file():
            try:
                return ImageFont.truetype(str(q), size)
            except OSError:
                continue
    raise SystemExit(f"无可用字体（尝试过: {paths}）")


def wrap_fit(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
             max_w: int, max_lines: int = 2) -> list[str]:
    """按宽度换行，最多 max_lines 行；超行返回按字符数折半的方案（由调用方缩小字号重试）。"""
    lines: list[str] = []
    cur = ""
    for ch in text:
        if draw.textlength(cur + ch, font=font) <= max_w:
            cur += ch
        else:
            if cur:
                lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        # 平均切 max_lines 段，宁可超出宽度（调用方随后缩字号）
        n = len(text)
        per = -(-n // max_lines)
        lines = [text[i:i + per] for i in range(0, n, per)][:max_lines]
    return lines


def fit_font_size(draw: ImageDraw.ImageDraw, text: str, font_path: str,
                  max_w: int, start: int, floor: int) -> ImageFont.FreeTypeFont:
    size = start
    while size > floor:
        f = load_font(font_path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return load_font(font_path, floor)


def compose(template: Path, out: Path, spec: dict) -> None:
    im = Image.open(template).convert("RGB")
    W, H = im.size
    draw = ImageDraw.Draw(im, "RGBA")
    L = LAYOUT

    title_font = fit_font_size(draw, spec["title"], spec["font_title"],
                               int(W * L["title"]["max_w"]),
                               int(H * L["title"]["size"]), int(H * 0.045))
    body_font = load_font(spec["font_body"], int(H * L["hook"]["size"]))
    series_font = load_font(spec["font_body"], int(H * L["series"]["size"]))
    author_font = load_font(spec["font_body"], int(H * L["author"]["size"]))

    # 1) 左上：系列名 · EP
    series_text = f"{spec['series']} · {spec['episode']}" if spec["episode"] else spec["series"]
    draw.text((W * L["series"]["x"], H * L["series"]["y"]), series_text,
              font=series_font, fill=C_SERIES)

    # 2) 书名（居中，深棕 + 柔和投影）
    tw = draw.textlength(spec["title"], font=title_font)
    tx = (W - tw) / 2
    ty = H * L["title"]["y"]
    shadow = (W * 0.0015, H * 0.0025)
    draw.text((tx + shadow[0], ty + shadow[1]), spec["title"],
              font=title_font, fill=C_SHADOW)
    draw.text((tx, ty), spec["title"], font=title_font, fill=C_TITLE)

    # 3) 钩子（居中，≤2 行，自动缩字号直至放得下）
    hook_font = body_font
    max_w = int(W * L["hook"]["max_w"])
    for _ in range(30):  # 缩字号重试
        lines = wrap_fit(draw, spec["hook"], hook_font, max_w, 2)
        line_h = hook_font.size * 1.35
        total_h = line_h * len(lines)
        ok_h = H * (L["author"]["y"] - L["hook"]["y"]) > total_h
        if ok_h:
            break
        hook_font = load_font(spec["font_body"], hook_font.size - 2)
    line_h = hook_font.size * 1.35
    hy = H * L["hook"]["y"]
    for i, ln in enumerate(lines):
        lw = draw.textlength(ln, font=hook_font)
        draw.text(((W - lw) / 2, hy + i * line_h), ln, font=hook_font, fill=C_HOOK)

    # 4) 作者（居中，小字）
    aw = draw.textlength(spec["author"], font=author_font)
    draw.text(((W - aw) / 2, H * L["author"]["y"]), spec["author"],
              font=author_font, fill=C_AUTHOR)

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
    p.add_argument("--template-dir", type=Path, default=None,
                   help="模板目录（默认读 config）")
    p.add_argument("--font-title", default=None, help="书名粗体字体（默认读 config）")
    p.add_argument("--font-body", default=None, help="正文/钩子字体（默认读 config）")
    args = p.parse_args()

    tdir = args.template_dir or cfg.path("cover.template_dir") or DEFAULT_TEMPLATE_DIR
    font_title = args.font_title or cfg.get("cover.font_title")
    font_body = args.font_body or cfg.get("cover.font_body")

    spec = {
        "title": args.book_title,
        "hook": args.hook,
        "author": args.author,
        "episode": args.episode,
        "series": args.series or cfg.get("cover.series_name", DEFAULT_SERIES),
        "font_title": [font_title] + FONT_FALLBACK_TITLE if font_title else FONT_FALLBACK_TITLE,
        "font_body": [font_body] + FONT_FALLBACK_BODY if font_body else FONT_FALLBACK_BODY,
    }

    t34 = tdir / "cover-3x4.png"
    t916 = tdir / "cover-9x16.png"
    if not t34.is_file() or not t916.is_file():
        raise SystemExit(f"模板缺失：{tdir} 下需要 cover-3x4.png 与 cover-9x16.png")

    compose(t34, args.out_dir / "cover.png", spec)
    compose(t916, args.out_dir / "cover-9x16.png", spec)
    print(f"完成：{args.out_dir}（cover.png 3:4 + cover-9x16.png 9:16）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
