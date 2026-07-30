#!/usr/bin/env python3
"""tts-minimax.py — 用 MiniMax T2A v2 生成旁白配音

用法:
    python3 tts-minimax.py <text_file> <output.wav> [--voice <voice_id>] [--speed <float>]

环境变量:
    MINIMAX_API_KEY — MiniMax API 密钥

默认音色: danya_xuejie（淡雅学姐，清冷克制，从 assets/voices/voice-library.json 选）。
语速/音色以 assets/voices/voice-library.json 为准（当前 approved 音色均为 1.1x）。
"""

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import cfg  # noqa: E402


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
        "model": cfg.get("tts.model", "speech-02-hd"),
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice,
            "speed": speed,
            "vol": cfg.get("tts.volume", 1.0),
            "pitch": cfg.get("tts.pitch", 0),
        },
        "audio_setting": {
            "sample_rate": cfg.get("tts.sample_rate", 32000),
            "bitrate": cfg.get("tts.bitrate", 128000),
            "format": "mp3",
            "channel": 1,
        },
    }, ensure_ascii=False)

    cmd = [
        "curl", "-s", "-w", "\n%{http_code}",
        "-X", "POST", cfg.get("tts.endpoint", "https://api.minimaxi.com/v1/t2a_v2"),
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
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp3_temp), "-ar", "48000", "-ac", "2",
             "-acodec", "pcm_s16le", str(output)],
            capture_output=True,
        )
        if result.returncode != 0:
            # 转换失败：保留 mp3 以便排查，不静默留下空 wav
            err = result.stderr.decode("utf-8", errors="replace")[-500:]
            raise SystemExit(f"ffmpeg mp3→wav 转换失败（mp3 保留在 {mp3_temp}）：{err}")
        mp3_temp.unlink()

    return {"size": len(audio_bytes), "voice": voice, "speed": speed}


def main():
    if len(sys.argv) < 3:
        print("用法: python3 tts-minimax.py <text_file> <output.wav> [--voice <id>] [--speed <float>]")
        sys.exit(1)

    text_file = Path(sys.argv[1])
    output = Path(sys.argv[2])

    voice = cfg.get("tts.default_voice", "danya_xuejie")
    speed = cfg.get("tts.default_speed", 1.1)
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
