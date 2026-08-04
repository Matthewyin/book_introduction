#!/usr/bin/env python3
"""pixabay-fetch.py — 从 Pixabay 搜索并下载暖调实拍视频素材

用法:
    python3 pixabay-fetch.py --query "cozy reading book warm" --count 5 --output-dir footage/

通过 ego-browser 搜索 Pixabay 视频页面，提取视频详情页 URL，
逐个打开详情页抓取 <video> 标签的 CDN 链接，然后 curl 下载 mp4。

Pixabay 内容许可证：免费可商用，无需署名。
"""

import argparse
import json
import pathlib
import subprocess
import sys
import urllib.parse


def ego_browser(script: str) -> str:
    """执行 ego-browser nodejs heredoc，返回 cliLog 输出（在 stderr 里）。"""
    result = subprocess.run(
        ["ego-browser", "nodejs"],
        input=script,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # ego-browser 的 cliLog 输出到 stderr，不是 stdout
    output = result.stderr or ""
    if result.stdout:
        output = output + "\n" + result.stdout
    return output


def search_videos(query: str, count: int) -> list[dict]:
    """搜索 Pixabay 视频，返回 [{url, label}] 列表。"""
    encoded = urllib.parse.quote(query)
    search_url = f"https://pixabay.com/videos/search/{encoded}/"
    limit = count * 3

    # 用字符串拼接避免 f-string 花括号冲突
    script = (
        "const task = await useOrCreateTaskSpace('pixabay-fetch')\n"
        f"await openOrReuseTab({json.dumps(search_url)}, {{ wait: true, timeout: 20 }})\n"
        "await wait(5)\n"
        "await scrollBy(300)\n"
        "await wait(2)\n"
        "const data = await js(String.raw`(() => {\n"
        "  const links = [...document.querySelectorAll('a[href*=\"/videos/\"]')];\n"
        "  const seen = new Set();\n"
        "  const results = [];\n"
        "  links.forEach(a => {\n"
        "    const href = a.href;\n"
        "    if (href.includes('/search/') || href.includes('/upload') || href.includes('istockphoto')) return;\n"
        "    const match = href.match(/\\/videos\\/[^?#]+/);\n"
        "    if (!match) return;\n"
        "    const url = match[0];\n"
        "    if (seen.has(url)) return;\n"
        "    seen.add(url);\n"
        "    const parent = a.parentElement;\n"
        "    if (parent?.innerText?.includes('Sponsored')) return;\n"
        "    const text = a.getAttribute('aria-label') || a.title || '';\n"
        "    results.push({url: 'https://pixabay.com' + url, label: text.substring(0, 80)});\n"
        "  });\n"
        "  return results;\n"
        "})()`)\n"
        f"const limited = data.slice(0, {limit})\n"
        "limited.forEach((v, i) => cliLog('ITEM:' + i + '|' + v.label + '|' + v.url))\n"
    )
    stdout = ego_browser(script)
    results = []
    for line in stdout.strip().split("\n"):
        line = line.strip()
        if line.startswith("ITEM:") and "pixabay.com/videos/" in line:
            # ITEM:0|label|url
            rest = line[5:]  # 去掉 "ITEM:"
            parts = rest.split("|", 2)
            if len(parts) == 3:
                results.append({"label": parts[1], "url": parts[2]})
    return results


def get_video_cdn(video_page_url: str) -> str | None:
    """打开视频详情页，抓取 <video> CDN 链接。"""
    script = (
        "await useOrCreateTaskSpace('pixabay-fetch')\n"
        f"await openOrReuseTab({json.dumps(video_page_url)}, {{ wait: true, timeout: 20 }})\n"
        "await wait(3)\n"
        "const src = await js(String.raw`(() => {\n"
        "  const v = document.querySelector('video');\n"
        "  if (!v) return '';\n"
        "  return v.src || '';\n"
        "})()`)\n"
        "cliLog('CDN:' + src)\n"
    )
    stdout = ego_browser(script)
    for line in stdout.split("\n"):
        line = line.strip()
        if line.startswith("CDN:") and "cdn.pixabay.com" in line:
            return line[4:]  # 去掉 "CDN:"
    return None


def download(url: str, output: pathlib.Path) -> bool:
    """curl 下载文件。"""
    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["curl", "-sL", "-o", str(output), url],
        capture_output=True,
        timeout=120,
    )
    return output.exists() and output.stat().st_size > 10000


def main() -> int:
    p = argparse.ArgumentParser(description="Pixabay 实拍视频素材搜索下载")
    p.add_argument("--query", required=True, help="搜索关键词（英文）")
    p.add_argument("--count", type=int, default=5, help="下载数量（默认 5）")
    p.add_argument("--output-dir", required=True, help="输出目录")
    args = p.parse_args()

    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"搜索 Pixabay: '{args.query}'…")
    videos = search_videos(args.query, args.count)
    print(f"  → 找到 {len(videos)} 个候选视频\n")

    if not videos:
        print("未找到视频，请尝试其他关键词。")
        return 1

    downloaded = 0
    for i, video in enumerate(videos):
        if downloaded >= args.count:
            break
        print(f"[{i}] {video['label']}")
        print(f"    {video['url']}")

        # 抓 CDN 链接
        cdn = get_video_cdn(video["url"])
        if not cdn or "cdn.pixabay.com" not in cdn:
            print(f"    ✗ 未找到 CDN 链接，跳过\n")
            continue

        print(f"    CDN: {cdn[:70]}…")

        # 下载
        out = output_dir / f"clip-{downloaded + 1:02d}.mp4"
        if download(cdn, out):
            size_mb = out.stat().st_size / 1024 / 1024
            print(f"    ✓ 已下载: {out} ({size_mb:.1f}MB)\n")
            downloaded += 1
        else:
            print(f"    ✗ 下载失败\n")

    print(f"完成：共下载 {downloaded}/{args.count} 个素材到 {output_dir}")
    if downloaded == 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
