#!/usr/bin/env python3
"""openrouter_image.py — OpenRouter gpt-image-2 同步生图后端。

OpenRouter 统一 Image API：一次 POST 同步返回 base64 图片，无异步轮询、无卡死问题。
模型固定 openai/gpt-image-2（与原 gptsapi 同模型，提示词完全复用）。

流程：
  POST https://openrouter.ai/api/v1/images
       { model, prompt, aspect_ratio, resolution, quality, output_format, n }
  → data[0].b64_json → base64 解码 → 写 --image

API Key 来源（按优先级）：
  1. --api-key 参数
  2. 环境变量 OPENROUTER_API_KEY
  3. ~/.zshrc 中的 export OPENROUTER_API_KEY（shell 启动加载；本脚本不解析 zshrc，
     非交互 shell 需用户确保 key 已在环境，或显式传 --api-key）

用法：
  python3 openrouter_image.py --prompt-file prompt.md --aspect-ratio 9:16 --image out.png
  python3 openrouter_image.py --prompt "..." --aspect-ratio 3:4 --image cover.png
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = "https://openrouter.ai"
ENDPOINT_IMAGES = "/api/v1/images"
DEFAULT_MODEL = "openai/gpt-image-2"
DEFAULT_RESOLUTION = "1K"
DEFAULT_QUALITY = "high"
DEFAULT_OUTPUT_FORMAT = "png"
REQUEST_TIMEOUT = 240  # 同步 API，gpt-image-2 high quality 大图偶发慢，给足余量
MAX_ATTEMPTS = 3
ALLOWED_RATIOS = {"auto", "1:1", "16:9", "9:16", "4:3", "3:4", "1:4", "4:1"}


def load_key(cli_key: str | None) -> str:
    if cli_key:
        return cli_key.strip()
    env = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if env:
        return env
    raise SystemExit(
        "OPENROUTER_API_KEY 不可见：请在环境变量或 --api-key 中提供"
    )


def generate(prompt: str, ratio: str, output: Path, key: str,
             base_url: str, model: str, resolution: str,
             quality: str, output_format: str) -> dict:
    url = f"{base_url.rstrip('/')}{ENDPOINT_IMAGES}"
    body = {
        "model": model,
        "prompt": prompt,
        "aspect_ratio": ratio,
        "resolution": resolution,
        "quality": quality,
        "output_format": output_format,
        "n": 1,
    }
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")

    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        req = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "User-Agent": "book-video-pipeline/openrouter",
            },
        )
        try:
            print(f"[openrouter] 第 {attempt}/{MAX_ATTEMPTS} 次请求（{model} {ratio}/{resolution}）…", file=sys.stderr)
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            data_list = result.get("data") or []
            if not data_list:
                last_error = f"响应缺少 data 数组：{json.dumps(result, ensure_ascii=False)[:300]}"
                print(f"[openrouter] {last_error}，重试…", file=sys.stderr)
                time.sleep(2)
                continue
            b64 = data_list[0].get("b64_json")
            if not b64:
                last_error = f"data[0] 缺少 b64_json：{json.dumps(data_list[0], ensure_ascii=False)[:200]}"
                print(f"[openrouter] {last_error}，重试…", file=sys.stderr)
                time.sleep(2)
                continue
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(base64.b64decode(b64))
            usage = result.get("usage", {})
            cost = usage.get("cost")
            cost_note = f"（${cost:.4f}）" if isinstance(cost, (int, float)) else ""
            print(f"[openrouter] 完成：{output}{cost_note}", file=sys.stderr)
            return {"attempts": attempt, "output": str(output), "usage": usage}
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")[:500]
            last_error = f"HTTP {e.code} {detail}"
            print(f"[openrouter] 第 {attempt} 次失败：{last_error}", file=sys.stderr)
            time.sleep(2)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            last_error = f"网络/超时：{e}"
            print(f"[openrouter] 第 {attempt} 次失败：{last_error}", file=sys.stderr)
            time.sleep(2)

    raise SystemExit(f"openrouter 连续 {MAX_ATTEMPTS} 次尝试均失败，最后原因：{last_error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="OpenRouter gpt-image-2 同步生图")
    parser.add_argument("--prompt-file", help="prompt 文件路径")
    parser.add_argument("--prompt", help="prompt 字符串（与 --prompt-file 二选一）")
    parser.add_argument("--aspect-ratio", default="9:16",
                        help=f"画幅，可选 {sorted(ALLOWED_RATIOS)}（默认 9:16）")
    parser.add_argument("--image", required=True, help="输出图片路径")
    parser.add_argument("--api-key", default=None, help="OpenRouter API key")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION,
                        help="512 / 1K / 2K / 4K（默认 1K）")
    parser.add_argument("--quality", default=DEFAULT_QUALITY,
                        help="auto / low / medium / high（默认 high）")
    parser.add_argument("--output-format", default=DEFAULT_OUTPUT_FORMAT,
                        help="png / jpeg / webp（默认 png）")
    args = parser.parse_args()

    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()
    elif args.prompt:
        prompt = args.prompt
    else:
        parser.error("必须提供 --prompt-file 或 --prompt")

    ratio = args.aspect_ratio
    if ratio not in ALLOWED_RATIOS:
        parser.error(f"不支持的画幅 {ratio}，可选 {sorted(ALLOWED_RATIOS)}")

    key = load_key(args.api_key)
    generate(
        prompt=prompt,
        ratio=ratio,
        output=Path(args.image).expanduser(),
        key=key,
        base_url=args.base_url,
        model=args.model,
        resolution=args.resolution,
        quality=args.quality,
        output_format=args.output_format,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
