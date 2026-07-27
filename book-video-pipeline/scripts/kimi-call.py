#!/usr/bin/env python3
"""kimi-call.py — 调用 Kimi K3 API 生成文案

用法:
    python3 kimi-call.py <system_prompt_file> <user_prompt_file> <output_file> [--model kimi-k3]

环境变量:
    KIMI_API_KEY — Kimi API 密钥
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

API_ENDPOINT = "https://api.kimi.com/coding/v1/chat/completions"
DEFAULT_MODEL = "kimi-k3"


def get_api_key():
    key = os.environ.get("KIMI_API_KEY", "").strip()
    if key:
        return key
    zshrc = Path.home() / ".zshrc"
    if zshrc.is_file():
        for line in zshrc.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "KIMI_API_KEY=" in line:
                return line.split("=", 1)[1].strip().strip("'\"")
    raise SystemExit("KIMI_API_KEY not found")


def call_kimi(system_prompt: str, user_prompt: str, key: str, model: str) -> str:
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }, ensure_ascii=False)

    req = urllib.request.Request(
        API_ENDPOINT,
        data=body.encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )

    # K3 is a reasoning model; a heavy rewrite can think for several minutes.
    with urllib.request.urlopen(req, timeout=600) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if "error" in data:
        raise SystemExit(f"Kimi API error: {data['error']}")

    content = data["choices"][0]["message"]["content"]
    return content


def main():
    if len(sys.argv) < 4:
        print("用法: python3 kimi-call.py <system_prompt_file> <user_prompt_file> <output_file> [--model kimi-k3]")
        sys.exit(1)

    system_file = Path(sys.argv[1])
    user_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])

    model = DEFAULT_MODEL
    for i, arg in enumerate(sys.argv[4:], 4):
        if arg == "--model" and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]

    system_prompt = system_file.read_text(encoding="utf-8").strip()
    user_prompt = user_file.read_text(encoding="utf-8").strip()

    key = get_api_key()

    print(f"▶ Calling Kimi K3 ({model})...")
    result = call_kimi(system_prompt, user_prompt, key, model)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(result, encoding="utf-8")
    print(f"✓ Saved to {output_file}")


if __name__ == "__main__":
    main()
