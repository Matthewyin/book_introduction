#!/usr/bin/env python3
"""cover-compose.py — 本地封面排版合成（无 Canva，零 API 依赖）

两段式架构：
  1. 底图（--base）：无字主视觉 + logo 品牌卡 → 保存为统一封面模板
     （assets/cover-image/cover-3x4-{art}.png + cover-9x16-{art}.png）
  2. 每集：底图（已含 logo，template_has_brand=true 时跳过 logo）
     + 右上「好书推荐」+ EP + 书名 + 钩子/作者
     → 输出到该书 03-assets/cover/cover-final*.png

文字 100% 保真（PIL 排版，不依赖 AI 渲染中文）。

画面风格（--art）—— 跟随本集视频风格:
  realistic  写实摄影（默认）——视频用写实人设时选
  anime      动漫插画——视频用动漫人设时选

样式系统（--style）:
  quiet  暖棕安静体（默认）——书名黑体常规 + 钩子仿宋描边
  viral  病毒标题体——书名超粗黑体白字 + 钩子亮黄标签黑字

配色系统（--palette）:
  sunny  阳光暖棕（默认）
  warm   秋冬暖橙
  calm   冷静蓝灰

模板系统（--template）:
  ambient   氛围静物版（默认，当前母版）
  bookshot  书封特写版（书占 60-70% 画面）

用法:
  底图：python3 scripts/cover-compose.py --base \
          --out-dir <统一封面目录=模板目录>
  每集：python3 scripts/cover-compose.py \
          --book-title 非暴力沟通 --hook ... --author ... --episode EP03 \
          --out-dir episodes/ep003-非暴力沟通/03-assets/cover
  病毒体：python3 scripts/cover-compose.py \
          --book-title ... --hook ... --style viral \
          --out-dir episodes/ep00X/03-assets/cover

配置（pipeline.yaml cover.*，可被 CLI 覆盖）:
  cover.template_dir       模板/底图目录
  cover.logo               左上角 logo（透明背景直贴）
  cover.corner_right       右上角文字（默认「好书推荐」）
  cover.template_has_brand 底图是否已含 logo（true 时每集不再画 logo）
  cover.font_title / font_title_viral / font_hook / font_body
  cover.out_3x4 / out_9x16 每集输出文件名
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
    "~/Library/Fonts/NotoSansSC-Regular.otf",          # 思源黑体常规（不加粗）
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]
FONT_FALLBACK_TITLE_VIRAL = [
    "~/Library/Fonts/ZCOOLKuHei.ttf",                  # 站酷酷黑（病毒标题体首选，笔画最疏大字号最清晰）
    "~/Library/Fonts/YouSheBiaoTiHei.ttf",              # 优设标题黑（备选）
    "~/Library/Fonts/NotoSansSC-Bold.otf",              # 思源黑体粗体（备选）
    "~/Library/Fonts/SourceHanSansSC-Heavy.otf",        # 思源黑体 Heavy（兜底）
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
]
FONT_FALLBACK_HOOK = [
    "~/Library/Fonts/FandolFang-Regular.otf",          # 仿宋（描边加粗）
    "~/Library/Fonts/NotoSansSC-Regular.otf",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]
FONT_FALLBACK_BODY = [
    "~/Library/Fonts/LxgwWenKai-Regular.ttf",          # 暖调
    "~/Library/Fonts/NotoSansSC-Regular.otf",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]

# --------------------------------------------------------------------------- 配色系统（--palette）

PALETTES = {
    "sunny": {
        "title":  (74, 46, 27, 255),      # #4A2E1B 暖深棕
        "shadow": (58, 34, 15, 130),      # 柔和投影
        "hook":   (92, 58, 32, 255),      # #5A3A20
        "meta":   (122, 92, 62, 235),     # #7A5C3E
        "corner": (122, 92, 62, 255),
    },
    "warm": {
        "title":  (123, 63, 0, 255),      # #7B3F00 暖橙棕
        "shadow": (80, 40, 0, 130),
        "hook":   (160, 82, 45, 255),     # #A0522D 赭石
        "meta":   (139, 94, 60, 235),     # #8B5E3C
        "corner": (139, 94, 60, 255),
    },
    "calm": {
        "title":  (44, 62, 80, 255),      # #2C3E50 深蓝灰
        "shadow": (20, 30, 40, 130),
        "hook":   (52, 73, 94, 255),      # #34495E
        "meta":   (93, 109, 126, 235),    # #5D6D7E
        "corner": (93, 109, 126, 255),
    },
}

# --------------------------------------------------------------------------- 样式系统（--style）

WHITE = (255, 255, 255, 255)
BLACK = (30, 30, 30, 255)
DARK_SHADOW = (0, 0, 0, 160)
YELLOW_LABEL = (255, 225, 0, 255)       # #FFE100 亮黄标签底

STYLES = {
    "quiet": {
        "title_font_key": "font_title",
        "title_stroke_mult": 0,           # 书名不描边
        "title_shadow": True,
        "title_tracking": 0,              # 无字间距
        "hook_font_key": "font_hook",
        "hook_stroke_mult": 0.0014,       # 钩子仿宋描边加粗
        "hook_bg": None,                  # 无色块
        "hook_bg_color": None,
        "hook_text_color": None,          # 用 palette.hook
    },
    "viral": {
        "title_font_key": "font_title_viral",
        "title_stroke_mult": 0,              # 不加描边（超粗字体+大字号+描边=笔画粘连）
        "title_shadow": True,
        "title_tracking": 0.05,              # 字间距 5% 字高，大字号防笔画粘连
        "hook_font_key": "font_title_viral",  # 钩子也用粗黑体
        "hook_stroke_mult": 0,
        "hook_bg": "label",               # 亮黄圆角矩形标签
        "hook_bg_color": YELLOW_LABEL,
        "hook_text_color": BLACK,
    },
}

# --------------------------------------------------------------------------- 版式

# 氛围版（默认）：文字落顶部留白区，主视觉在下方
LAYOUT_AMBIENT = {
    "logo": {"x": 0.045, "y": 0.030, "w": 0.300},        # 左上：logo 品牌卡
    "corner": {"x": 0.950, "y": 0.038, "size": 0.030},   # 右上：「好书推荐」右对齐
    "ep": {"x": 0.950, "y": 0.076, "size": 0.022},       # 右上角下方：EP 集数
    "title": {"y": 0.160, "size": 0.105, "max_w": 0.86, "max_chars": 6}, # 居中：书名（每行≤6字，自动缩字号）
    "hook": {"y": 0.300, "size": 0.042, "max_w": 0.82},  # 居中：钩子（严格不超宽）
    "author": {"y": 0.425, "size": 0.027},               # 居中：作者
}

# 书封特写版：人物+书在下方，文字在顶部一体留白区
LAYOUT_BOOKSHOT = {
    "logo": {"x": 0.045, "y": 0.030, "w": 0.300},
    "corner": {"x": 0.950, "y": 0.038, "size": 0.030},
    "ep": {"x": 0.950, "y": 0.076, "size": 0.022},
    "title": {"y": 0.180, "size": 0.125, "max_w": 0.92, "max_chars": 6}, # 书名（下移，每行≤6字自动折行）
    "hook": {"y": 0.380, "size": 0.030, "max_w": 0.82, "x": 0.06, "align": "left"},  # 钩子（左对齐，y 随标题行数动态调整）
    "author": {"y": 0.430, "size": 0.022, "x": 0.06, "align": "left"},  # 作者（左对齐）
}

LAYOUTS = {"ambient": LAYOUT_AMBIENT, "bookshot": LAYOUT_BOOKSHOT,
           "bookshot-character": LAYOUT_BOOKSHOT}


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


def _check_safe_zone(draw: ImageDraw.ImageDraw, element: str, bbox: tuple,
                     W: int, H: int, margin: float) -> None:
    """检查元素 bounding box 是否在安全区内（距四边 ≥ margin*W/H）。打印警告。"""
    x0, y0, x1, y1 = bbox
    mx = W * margin
    my = H * margin
    violations = []
    if x0 < mx:
        violations.append(f"左边距 {x0:.0f}px < {mx:.0f}px")
    if y0 < my:
        violations.append(f"上边距 {y0:.0f}px < {my:.0f}px")
    if x1 > W - mx:
        violations.append(f"右边距 {W-x1:.0f}px < {mx:.0f}px")
    if y1 > H - my:
        violations.append(f"下边距 {H-y1:.0f}px < {my:.0f}px")
    if violations:
        print(f"  ⚠ 安全区警告 [{element}]: {'; '.join(violations)}")


def compose(template: Path, out: Path, spec: dict) -> None:
    im = Image.open(template).convert("RGB")
    W, H = im.size
    L = dict(LAYOUTS[spec["template"]])
    pal = PALETTES[spec["palette"]]
    sty = STYLES[spec["style"]]
    margin = spec.get("safe_margin", 0.10)

    # hook_y 覆盖：如果指定，覆盖默认 hook y，作者 y 相应下移避免重叠
    hook_y_override = spec.get("hook_y")
    if hook_y_override is not None:
        L["hook"] = dict(L["hook"], y=float(hook_y_override))
        L["author"] = dict(L["author"], y=L["hook"]["y"] + 0.06 + 0.025)

    draw = ImageDraw.Draw(im, "RGBA")
    is_base = bool(spec.get("base"))
    skip_logo = bool(spec.get("skip_brand"))

    # ── 1) 左上：logo 品牌卡（透明背景直贴；底图画 logo，模板已含则跳过）──
    if not skip_logo:
        logo = spec.get("logo")
        if logo and logo.is_file():
            lg = Image.open(logo).convert("RGBA")
            lw = int(W * L["logo"]["w"])
            lh = int(lg.height * lw / lg.width)
            lg = lg.resize((lw, lh), Image.LANCZOS)
            lx, ly = int(W * L["logo"]["x"]), int(H * L["logo"]["y"])
            im.paste(lg, (lx, ly), lg)
            _check_safe_zone(draw, "logo", (lx, ly, lx + lw, ly + lh), W, H, margin)
        else:
            series_font = load_font(spec["font_body"], int(H * L["corner"]["size"]))
            series_text = f"{spec['series']} · {spec['episode']}" if spec["episode"] else spec["series"]
            draw.text((W * L["logo"]["x"], H * L["logo"]["y"]), series_text,
                      font=series_font, fill=pal["meta"])

    # 底图模式：art + logo，到此结束
    if is_base:
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out)
        print(f"✓ {out.name}: {W}x{H} 底图（art+logo）")
        return

    # ── 2) 右上：「好书推荐」+ EP 集数（右对齐）──
    corner_font = load_font(spec["font_body"], int(H * L["corner"]["size"]))
    cr_text = spec["corner_right"] or DEFAULT_CORNER_RIGHT
    cw = draw.textlength(cr_text, font=corner_font)
    cx = W * L["corner"]["x"] - cw
    cy = H * L["corner"]["y"]
    draw.text((cx, cy), cr_text, font=corner_font, fill=pal["corner"])
    _check_safe_zone(draw, "corner", (cx, cy, cx + cw, cy + corner_font.size), W, H, margin)

    if spec["episode"]:
        ep_font = load_font(spec["font_body"], int(H * L["ep"]["size"]))
        ew = draw.textlength(spec["episode"], font=ep_font)
        ex = W * L["ep"]["x"] - ew
        ey = H * L["ep"]["y"]
        draw.text((ex, ey), spec["episode"], font=ep_font, fill=pal["meta"])
        _check_safe_zone(draw, "ep", (ex, ey, ex + ew, ey + ep_font.size), W, H, margin)

    # ── 3) 书名：居中（支持字间距 tracking + 每行 max_chars 自动折行）──
    title_font_paths = spec[sty["title_font_key"]]
    if spec["title"]:
        tracking = sty.get("title_tracking", 0)
        max_chars = L["title"].get("max_chars", 0)

        # 按 max_chars 折行
        raw_title = spec["title"]
        if max_chars and len(raw_title) > max_chars:
            title_lines = [raw_title[i:i+max_chars] for i in range(0, len(raw_title), max_chars)]
        else:
            title_lines = [raw_title]

        # 测量单行宽度（含 tracking）
        def _line_w(font: ImageFont.FreeTypeFont, text: str, tpx: int) -> float:
            if tpx:
                return sum(font.getlength(ch) for ch in text) + tpx * (len(text) - 1)
            return draw.textlength(text, font=font)

        # 缩字号：以最长一行为准，确保 ≤ max_w
        title_font = load_font(title_font_paths, int(H * L["title"]["size"]))
        tracking_px = int(title_font.size * tracking) if tracking else 0
        max_w_px = int(W * L["title"]["max_w"])
        widest = max(title_lines, key=len)
        while _line_w(title_font, widest, tracking_px) > max_w_px and title_font.size > int(H * 0.045):
            title_font = load_font(title_font_paths, title_font.size - 2)
            tracking_px = int(title_font.size * tracking) if tracking else 0

        title_color = pal["title"]
        title_stroke = max(0, int(H * sty["title_stroke_mult"])) if sty["title_stroke_mult"] else 0
        kwargs = {"font": title_font, "fill": title_color}
        if title_stroke:
            kwargs["stroke_width"] = title_stroke
            kwargs["stroke_fill"] = title_color

        line_h = title_font.size * 1.1
        total_h = line_h * len(title_lines)
        ty0 = H * L["title"]["y"]
        shadow = (W * 0.0015, H * 0.0025)

        for li, line in enumerate(title_lines):
            lw = _line_w(title_font, line, tracking_px)
            lx = (W - lw) / 2
            ly = ty0 + li * line_h

            # 投影
            if sty["title_shadow"]:
                if tracking_px:
                    cx = lx + shadow[0]
                    for ch in line:
                        draw.text((cx, ly + shadow[1]), ch, font=title_font, fill=pal["shadow"])
                        cx += title_font.getlength(ch) + tracking_px
                else:
                    draw.text((lx + shadow[0], ly + shadow[1]), line,
                              font=title_font, fill=pal["shadow"])

            # 正文
            if tracking_px:
                cx = lx
                for ch in line:
                    draw.text((cx, ly), ch, **kwargs)
                    cx += title_font.getlength(ch) + tracking_px
            else:
                draw.text((lx, ly), line, **kwargs)

        _check_safe_zone(draw, "title",
                         ((W - max_w_px)/2, ty0, (W + max_w_px)/2, ty0 + total_h),
                         W, H, margin)

    # 标题折行时，hook/author 的 y 需动态下移（避免与多行标题重叠）
    n_title_lines = len(title_lines) if spec["title"] else 1
    title_extra_h = (n_title_lines - 1) * (title_font.size * 1.1) if spec["title"] else 0
    hook_y_offset = title_extra_h  # 多行标题下移钩子
    author_y_offset = title_extra_h

    # hook/author 的水平对齐：LAYOUT 有 align=left 时左对齐，否则居中
    def _element_x(text_w: float, layout_elem: dict) -> float:
        align = layout_elem.get("align", "center")
        if align == "left":
            return W * layout_elem.get("x", 0.06)
        return (W - text_w) / 2

    # ── 4) 钩子（quiet=仿宋描边居中 / viral=亮黄标签黑字左对齐）──
    hook_font_paths = spec[sty["hook_font_key"]]
    if spec["hook"]:
        max_w = int(W * L["hook"]["max_w"])
        floor = int(H * 0.028)
        start = int(H * L["hook"]["size"])
        hook_font = fit_font_size(draw, spec["hook"], hook_font_paths, max_w, start, floor)

        # 钩子颜色：viral 用黑色，quiet 用 palette hook 色
        hook_color = sty["hook_text_color"] or pal["hook"]
        hook_stroke = max(1, int(H * sty["hook_stroke_mult"])) if sty["hook_stroke_mult"] else 0

        if draw.textlength(spec["hook"], font=hook_font) > max_w:
            # floor 仍超宽 → 折 2 行
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
            hy = H * L["hook"]["y"] + hook_y_offset
            for i, ln in enumerate(lines[:2]):
                lw = draw.textlength(ln, font=hook_font)
                lx = _element_x(lw, L["hook"])
                ly = hy + i * line_h
                _draw_hook_line(draw, ln, hook_font, lx, ly, W, H, sty, hook_color,
                                hook_stroke, max_w)
        else:
            hw = draw.textlength(spec["hook"], font=hook_font)
            hx = _element_x(hw, L["hook"])
            hy = H * L["hook"]["y"] + hook_y_offset
            _draw_hook_line(draw, spec["hook"], hook_font, hx, hy, W, H, sty, hook_color,
                            hook_stroke, max_w)

    # ── 5) 作者（跟随 hook 对齐）──
    if spec["author"]:
        author_font = load_font(spec["font_hook"], int(H * L["author"]["size"]))
        aw = draw.textlength(spec["author"], font=author_font)
        ax = _element_x(aw, L["author"])
        ay = H * L["author"]["y"] + author_y_offset
        hook_stroke = max(1, int(H * 0.0014))
        draw.text((ax, ay), spec["author"], font=author_font,
                  fill=pal["meta"], stroke_width=hook_stroke, stroke_fill=pal["meta"])
        _check_safe_zone(draw, "author", (ax, ay, ax + aw, ay + author_font.size), W, H, margin)

    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    style_tag = f" [{spec['style']}/{spec['palette']}/{spec['template']}]" if \
        (spec["style"] != "quiet" or spec["palette"] != "sunny" or spec["template"] != "ambient") else ""
    print(f"✓ {out.name}: {W}x{H} 书名「{spec['title']}」 钩子「{spec['hook']}」{style_tag}")


def _draw_hook_line(draw: ImageDraw.ImageDraw, text: str,
                    font: ImageFont.FreeTypeFont, x: float, y: float,
                    W: int, H: int, sty: dict, color: tuple,
                    stroke_w: int, max_w: int) -> None:
    """画钩子单行。viral 样式先铺亮黄圆角矩形标签底再叠黑字。"""
    tw = draw.textlength(text, font=font)
    if sty["hook_bg"] == "label":
        # 亮黄圆角矩形标签：左右各留 padding
        pad_x = H * 0.015
        pad_y = H * 0.005
        radius = int(H * 0.008)
        bg_x0 = x - pad_x
        bg_y0 = y - pad_y
        bg_x1 = x + tw + pad_x
        bg_y1 = y + font.size + pad_y
        draw.rounded_rectangle((bg_x0, bg_y0, bg_x1, bg_y1), radius=radius,
                               fill=sty["hook_bg_color"])
    kwargs = {"font": font, "fill": color}
    if stroke_w:
        kwargs["stroke_width"] = stroke_w
        kwargs["stroke_fill"] = color
    draw.text((x, y), text, **kwargs)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out-dir", type=Path, required=True,
                   help="输出目录：--base 时=模板/底图目录；每集时=该书 03-assets/cover")
    p.add_argument("--base", action="store_true", help="底图模式：只画 art+logo，无文字")
    p.add_argument("--book-title", default="", help="书名（≤10 字，不加《》）")
    p.add_argument("--hook", default="", help="钩子文案（≤12 字）")
    p.add_argument("--author", default="", help="作者/副标题")
    p.add_argument("--episode", default="", help="集数，如 EP03")
    p.add_argument("--hook-y", type=float, default=None,
                   help="钩子 y 比例（覆盖默认值，覆盖时作者 y 自动下移）")
    p.add_argument("--style", choices=["quiet", "viral"], default="quiet",
                   help="文字样式：quiet=暖棕安静体（默认）viral=病毒标题体（超粗+亮黄标签）")
    p.add_argument("--palette", choices=["sunny", "warm", "calm"], default="sunny",
                   help="配色：sunny=阳光暖棕（默认）warm=秋冬暖橙 calm=冷静蓝灰")
    p.add_argument("--template", choices=["ambient", "bookshot", "bookshot-character"], default="ambient",
                   help="模板版式：ambient=氛围静物（默认）bookshot=书封特写 bookshot-character=书封+人物推荐")
    p.add_argument("--art", choices=["realistic", "anime"], default="realistic",
                   help="画面风格：realistic=写实摄影（默认）anime=动漫插画。跟随本集视频风格——视频写实用 realistic，视频动漫用 anime")
    p.add_argument("--safe-margin", type=float, default=0.10,
                   help="安全区边距比例（默认 0.10=10%%，元素超出时打印警告）")
    p.add_argument("--series", default=None, help="系列名（默认读 config）")
    p.add_argument("--corner-right", default=None, help="右上角文字（默认「好书推荐」）")
    p.add_argument("--template-dir", type=Path, default=None,
                   help="模板/底图目录（默认读 config）")
    p.add_argument("--logo", type=Path, default=None, help="logo 品牌卡路径（默认读 config）")
    p.add_argument("--font-title", default=None, help="书名黑体字体（默认读 config）")
    p.add_argument("--font-title-viral", default=None, help="病毒标题体超粗字体（默认读 config）")
    p.add_argument("--font-hook", default=None, help="钩子/作者仿宋字体（默认读 config）")
    p.add_argument("--font-body", default=None, help="系列/右上角字体（默认读 config）")
    args = p.parse_args()

    tdir = args.template_dir or cfg.path("cover.template_dir") or DEFAULT_TEMPLATE_DIR
    out_3x4 = cfg.get("cover.out_3x4", "cover-final.png")
    out_9x16 = cfg.get("cover.out_9x16", "cover-final-9x16.png")

    def _fonts(key: str, fallback: list[str]) -> list[str]:
        v = cfg.get(f"cover.{key}")
        return [v] + fallback if v else fallback

    spec = {
        "base": args.base,
        "skip_brand": (not args.base) and bool(cfg.get("cover.template_has_brand", False)),
        "title": args.book_title,
        "hook": args.hook,
        "author": args.author,
        "episode": args.episode,
        "series": args.series or cfg.get("cover.series_name", DEFAULT_SERIES),
        "corner_right": args.corner_right or cfg.get("cover.corner_right", DEFAULT_CORNER_RIGHT),
        "logo": args.logo or cfg.path("cover.logo"),
        "style": args.style,
        "palette": args.palette,
        "template": args.template,
        "art": args.art,
        "safe_margin": args.safe_margin,
        "hook_y": args.hook_y,
        "font_title": _fonts("font_title", FONT_FALLBACK_TITLE),
        "font_title_viral": _fonts("font_title_viral", FONT_FALLBACK_TITLE_VIRAL),
        "font_hook": _fonts("font_hook", FONT_FALLBACK_HOOK),
        "font_body": _fonts("font_body", FONT_FALLBACK_BODY),
    }

    # 模板文件名：cover-{ratio}-{template?}-{art}.png
    # ambient（默认版式）省略 template 段：cover-3x4-realistic.png / cover-3x4-anime.png
    # 其他版式带 template 段：cover-3x4-bookshot-anime.png
    tmpl = "" if args.template == "ambient" else f"-{args.template}"
    t34 = tdir / f"cover-3x4{tmpl}-{args.art}.png"
    t916 = tdir / f"cover-9x16{tmpl}-{args.art}.png"
    if not t34.is_file() or not t916.is_file():
        raise SystemExit(f"模板缺失：{tdir} 下需要 {t34.name} 与 {t916.name}")

    if args.base:
        # 底图：读纯艺术模板，写入同目录覆盖（art+logo 成为新模板）
        compose(t34, t34, spec)
        compose(t916, t916, spec)
        print(f"底图完成：{tdir}（{t34.name} + {t916.name} 已含 logo，"
              f"请确认 pipeline.yaml cover.template_has_brand=true）")
    else:
        compose(t34, args.out_dir / out_3x4, spec)
        compose(t916, args.out_dir / out_9x16, spec)
        print(f"完成：{args.out_dir}（{out_3x4} 3:4 + {out_9x16} 9:16）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
