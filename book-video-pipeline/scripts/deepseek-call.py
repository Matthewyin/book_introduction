#!/usr/bin/env python3
"""deepseek-call.py — 调用 DeepSeek API 生成内容

用法:
    python3 deepseek-call.py <system_prompt_file> <user_prompt_file> <output_file> --model deepseek-v4-pro

环境变量:
    DEEPSEEK_API_KEY — DeepSeek API 密钥
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"


def get_api_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if key:
        return key
    zshrc = Path.home() / ".zshrc"
    if zshrc.is_file():
        for line in zshrc.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "DEEPSEEK_API_KEY=" in line:
                return line.split("=", 1)[1].strip().strip("'\"")
    raise SystemExit("DEEPSEEK_API_KEY not found")


def call_deepseek(system_prompt: str, user_prompt: str, key: str, model: str) -> str:
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

    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if "error" in data:
        raise SystemExit(f"DeepSeek API error: {data['error']}")

    content = data["choices"][0]["message"]["content"]
    return content


def main():
    if len(sys.argv) < 4:
        print("用法: python3 deepseek-call.py <system_prompt_file> <user_prompt_file> <output_file> [--model deepseek-v4-pro]")
        sys.exit(1)

    system_file = Path(sys.argv[1])
    user_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])

    model = "deepseek-v4-pro"
    for i, arg in enumerate(sys.argv[4:], 4):
        if arg == "--model" and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]

    system_prompt = system_file.read_text(encoding="utf-8").strip()
    user_prompt = user_file.read_text(encoding="utf-8").strip()

    key = get_api_key()

    print(f"▶ Calling DeepSeek ({model})...")
    result = call_deepseek(system_prompt, user_prompt, key, model)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(result, encoding="utf-8")
    print(f"✓ Saved to {output_file}")


if __name__ == "__main__":
    main()
