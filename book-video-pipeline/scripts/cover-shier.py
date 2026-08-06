#!/usr/bin/env python3
"""cover-shier.py — 素材截图手写体封面（A/B 线通用）

复刻抖音「十二..」封面风格：空旷风景截图 + LXGW 霞鹜文楷白色手写体 + 无底条无描边。

用法（在集目录下运行）:
    python3 scripts/cover-shier.py \
        --image 03-assets/cover/candidates/cover-cand-03.jpg \
        --book-title 影响力 \
        --author 罗伯特·西奥迪尼 \
        --out-dir 03-assets/cover

前置：先从素材视频截 6 张候选图（见 quote-workflow.md Q5a），用户审核选定后传入 --image。
输出：03-assets/cover/cover-final.png（3:4）+ cover-final-9x16.png（9:16）。
字体：~/Library/Fonts/LxgwWenKai-Regular.ttf（霞鹜文楷，需预装）。
"""
import argparse, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

FONT_PATH = str(Path.home() / "Library/Fonts/LxgwWenKai-Regular.ttf")
TAGS = "#读书  #好书推荐  #情感共鸣"


def make_cover(bg_im: Image.Image, out_path: Path, target_w: int, target_h: int,
               book_title: str, author: str):
    """生成一版封面：截图背景 + 白色手写体文字。"""
    bg = bg_im.copy()
    bg_ratio = bg.width / bg.height
    target_ratio = target_w / target_h
    if bg_ratio > target_ratio:
        new_w = int(bg.height * target_ratio)
        x = (bg.width - new_w) // 2
        bg = bg.crop((x, 0, x + new_w, bg.height))
    else:
        new_h = int(bg.width / target_ratio)
        y = (bg.height - new_h) // 2
        bg = bg.crop((0, y, bg.width, y + new_h))
    bg = bg.resize((target_w, target_h), Image.LANCZOS)

    # 低饱和 + 提亮（治愈感）
    bg = ImageEnhance.Color(bg).enhance(0.85)
    bg = ImageEnhance.Brightness(bg).enhance(1.05)

    # 上半部极淡白色渐变
    overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for y in range(target_h // 2):
        alpha = int(40 * (1 - y / (target_h // 2)))
        draw_ov.line([(0, y), (target_w, y)], fill=(255, 250, 240, alpha))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(bg)
    scale = target_w / 1080

    f_title = ImageFont.truetype(FONT_PATH, int(88 * scale))
    f_author = ImageFont.truetype(FONT_PATH, int(42 * scale))
    f_tags = ImageFont.truetype(FONT_PATH, int(30 * scale))

    white = (255, 255, 255)
    y_cursor = int(target_h * 0.12)

    # 书名
    line1 = f"《{book_title}》"
    w1 = draw.textlength(line1, font=f_title)
    draw.text(((target_w - w1) / 2, y_cursor), line1, fill=white, font=f_title)
    y_cursor += int(110 * scale)

    # 作者
    line2 = f"作者：{author}"
    w2 = draw.textlength(line2, font=f_author)
    draw.text(((target_w - w2) / 2, y_cursor), line2, fill=white, font=f_author)

    # 底部标签
    w_tags = draw.textlength(TAGS, font=f_tags)
    draw.text(((target_w - w_tags) / 2, target_h - int(60 * scale)), TAGS, fill=white, font=f_tags)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    bg.save(out_path, quality=95)
    print(f"✓ {out_path}: {target_w}x{target_h}")


def main():
    p = argparse.ArgumentParser(description="素材截图手写体封面（复刻十二..风格）")
    p.add_argument("--image", required=True, help="用户审核选定的候选图路径（如 03-assets/cover/candidates/cover-cand-03.jpg）")
    p.add_argument("--book-title", required=True, help="书名（不含《》）")
    p.add_argument("--author", required=True, help="作者")
    p.add_argument("--out-dir", default="03-assets/cover", help="输出目录")
    args = p.parse_args()

    bg = Image.open(args.image).convert("RGB")
    print(f"背景图: {bg.size} ({args.image})")

    out_dir = Path(args.out_dir)
    make_cover(bg, out_dir / "cover-final.png", 1080, 1440, args.book_title, args.author)
    make_cover(bg, out_dir / "cover-final-9x16.png", 1080, 1920, args.book_title, args.author)
    print("完成")


if __name__ == "__main__":
    main()
