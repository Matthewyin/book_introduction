#!/usr/bin/env python3
"""validate-spec.py — 校验视频是否符合心理励志图书视频规格

用法:
    python3 validate-spec.py <video.mp4>

检查项:
    - 时长 ≤ 180 秒
    - 分辨率 = 1080×1920
    - 帧率 = 30 fps
    - 视频编码 = h264
    - 音频编码 = aac
    - 音频采样率 = 48000 Hz
"""

import json
import subprocess
import sys
from pathlib import Path


def probe_video(video_path: str) -> dict:
    """用 ffprobe 获取视频信息"""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"✗ ffprobe 失败: {result.stderr}")
        sys.exit(1)
    return json.loads(result.stdout)


def check_spec(info: dict) -> list:
    """校验规格，返回问题列表"""
    issues = []

    fmt = info.get("format", {})
    streams = info.get("streams", [])

    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    if not video_stream:
        issues.append("✗ 未找到视频流")
        return issues

    # ── 时长 ──
    duration = float(fmt.get("duration", 0))
    if duration > 180:
        issues.append(f"✗ 时长超限: {duration:.1f}s > 180s")
    elif duration > 170:
        issues.append(f"⚠ 时长接近上限: {duration:.1f}s (建议 ≤170s)")

    # ── 分辨率 ──
    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))
    if width != 1080 or height != 1920:
        issues.append(f"✗ 分辨率不符: {width}x{height} (应为 1080x1920)")

    # ── 帧率 ──
    fps_str = video_stream.get("avg_frame_rate", "0/1")
    num, den = fps_str.split("/")
    fps = int(num) / int(den) if int(den) != 0 else 0
    if abs(fps - 30) > 1:
        issues.append(f"✗ 帧率不符: {fps:.1f}fps (应为 30fps)")

    # ── 视频编码 ──
    vcodec = video_stream.get("codec_name", "")
    if vcodec != "h264":
        issues.append(f"✗ 视频编码不符: {vcodec} (应为 h264)")

    # ── 像素格式 ──
    pix_fmt = video_stream.get("pix_fmt", "")
    if pix_fmt != "yuv420p":
        issues.append(f"⚠ 像素格式: {pix_fmt} (建议 yuv420p 保证兼容性)")

    # ── 音频 ──
    if audio_stream:
        acodec = audio_stream.get("codec_name", "")
        if acodec != "aac":
            issues.append(f"✗ 音频编码不符: {acodec} (应为 aac)")

        sample_rate = int(audio_stream.get("sample_rate", 0))
        if sample_rate != 48000:
            issues.append(f"⚠ 音频采样率: {sample_rate}Hz (建议 48000Hz)")

        channels = int(audio_stream.get("channels", 0))
        if channels != 2:
            issues.append(f"⚠ 音频声道: {channels} (建议立体声 2)")
    else:
        issues.append("✗ 未找到音频流")

    # ── 文件大小 ──
    size_mb = int(fmt.get("size", 0)) / 1024 / 1024
    if size_mb > 100:
        issues.append(f"⚠ 文件较大: {size_mb:.1f}MB (建议 <100MB 便于上传)")

    return issues, {
        "duration": duration,
        "resolution": f"{width}x{height}",
        "fps": fps,
        "video_codec": vcodec,
        "audio_codec": audio_stream.get("codec_name", "") if audio_stream else "",
        "size_mb": size_mb,
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python3 validate-spec.py <video.mp4>")
        sys.exit(1)

    video_path = sys.argv[1]
    if not Path(video_path).exists():
        print(f"✗ 文件不存在: {video_path}")
        sys.exit(1)

    print(f"▶ 校验视频: {video_path}")
    print()

    info = probe_video(video_path)
    issues, specs = check_spec(info)

    # 打印规格
    print("规格:")
    print(f"  时长:      {specs['duration']:.1f}s")
    print(f"  分辨率:    {specs['resolution']}")
    print(f"  帧率:      {specs['fps']:.0f}fps")
    print(f"  视频编码:  {specs['video_codec']}")
    print(f"  音频编码:  {specs['audio_codec']}")
    print(f"  文件大小:  {specs['size_mb']:.1f}MB")
    print()

    # 打印问题
    if not issues:
        print("✅ 全部通过！视频规格符合要求。")
    else:
        print(f"发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"  {issue}")
        print()

        errors = [i for i in issues if i.startswith("✗")]
        if errors:
            print(f"✗ 有 {len(errors)} 个严重问题，请修正后再发布。")
            sys.exit(1)
        else:
            print("⚠ 仅有警告，可以发布但建议优化。")


if __name__ == "__main__":
    main()
