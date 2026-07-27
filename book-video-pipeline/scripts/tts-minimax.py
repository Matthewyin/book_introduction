#!/usr/bin/env python3
"""tts-minimax.py — 用 MiniMax T2A v2 生成旁白配音

用法:
    python3 tts-minimax.py <text_file> <output.wav> [--voice <voice_id>] [--speed <float>]

环境变量:
    MINIMAX_API_KEY — MiniMax API 密钥

默认音色: female-tianmei（甜美女声，适合心理励志类）
"""

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

API_ENDPOINT = "https://api.minimaxi.com/v1/t2a_v2"
DEFAULT_VOICE = "female-tianmei"
DEFAULT_SPEED = 0.95  # 略慢，适合叙事


def get_api_key():
    key = os.environ.get("MINIMAX_API_KEY", "").strip()
    if key:
        return key
    # 从 .zshrc 读取
    zshrc = Path.home() / ".zshrc"
    if zshrc.is_file():
        for line in zshrc.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("export MINIMAX_API_KEY="):
                val = line.split("=", 1)[1].strip().strip("'\"")
                if val:
                    return val
    raise SystemExit("MINIMAX_API_KEY 未设置")


def synthesize(text: str, output: Path, voice: str, speed: float, key: str):
    """调用 MiniMax T2A v2 合成语音"""
    body = json.dumps({
        "model": "speech-02-hd",
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice,
            "speed": speed,
            "vol": 1.0,
            "pitch": 0,
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3",
            "channel": 1,
        },
    }, ensure_ascii=False)

    cmd = [
        "curl", "-s", "-w", "\n%{http_code}",
        "-X", "POST", API_ENDPOINT,
        "-H", f"authorization: Bearer {key}",
        "-H", "content-type: application/json",
        "-d", body,
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    out = result.stdout.decode("utf-8", errors="replace")
    http_code = out[-3:]
    resp_body = out[:-4]

    if http_code != "200":
        raise SystemExit(f"MiniMax API 失败: HTTP {http_code}\n{resp_body[:500]}")

    resp = json.loads(resp_body)
    audio_hex = resp.get("data", {}).get("audio", "")
    if not audio_hex:
        raise SystemExit(f"MiniMax 返回无音频: {json.dumps(resp, ensure_ascii=False)[:300]}")

    # hex → bytes
    audio_bytes = bytes.fromhex(audio_hex)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(audio_bytes)

    # 如果输出是 wav，用 ffmpeg 转换
    if output.suffix == ".wav":
        mp3_temp = output.with_suffix(".mp3")
        mp3_temp.write_bytes(audio_bytes)
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp3_temp), "-ar", "48000", "-ac", "2",
             "-acodec", "pcm_s16le", str(output)],
            capture_output=True,
        )
        mp3_temp.unlink()

    return {"size": len(audio_bytes), "voice": voice, "speed": speed}


def main():
    if len(sys.argv) < 3:
        print("用法: python3 tts-minimax.py <text_file> <output.wav> [--voice <id>] [--speed <float>]")
        sys.exit(1)

    text_file = Path(sys.argv[1])
    output = Path(sys.argv[2])

    voice = DEFAULT_VOICE
    speed = DEFAULT_SPEED
    for i, arg in enumerate(sys.argv[3:], 3):
        if arg == "--voice" and i + 1 < len(sys.argv):
            voice = sys.argv[i + 1]
        elif arg == "--speed" and i + 1 < len(sys.argv):
            speed = float(sys.argv[i + 1])

    text = text_file.read_text(encoding="utf-8").strip()
    # 移除 markdown 标记，只保留纯文本
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("|") or line.startswith("-"):
            continue
        if line.startswith("**") and line.endswith("**"):
            line = line.strip("*")
        lines.append(line)
    clean_text = "".join(lines)

    print(f"▶ 合成语音: {len(clean_text)} 字, 音色={voice}, 语速={speed}")

    key = get_api_key()
    result = synthesize(clean_text, output, voice, speed, key)
    print(f"✓ 完成: {output} ({result['size']} bytes)")


if __name__ == "__main__":
    main()
