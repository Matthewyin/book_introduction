#!/usr/bin/env python3
"""Derive the real shot timeline from a finished voiceover.

Step 5 of the pipeline. The voiceover is already locked at this point, so the
shot boundaries must follow the audio rather than the other way round: each
shot gets a share of the timeline proportional to its character count, then
every boundary snaps to the nearest natural pause so cuts land between
sentences instead of mid-word.

Usage:
    python3 realign-shots.py <voiceover.wav> <shots.json> <out-timing.json>

`shots.json` is a list of {"shot": N, "voiceover": "..."} in playback order.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

NOISE_DB = "-35dB"
MIN_SILENCE = 0.28
SNAP_TOLERANCE = 2.5  # a boundary drifts no further than this to reach a pause
MIN_SHOT = 1.0


def probe_duration(audio: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio)],
        capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def run_silencedetect(audio: Path, min_dur: float) -> tuple[list[float], list[float]]:
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(audio),
         "-af", f"silencedetect=noise={NOISE_DB}:d={min_dur}",
         "-f", "null", "-"],
        capture_output=True, text=True)
    log = proc.stderr
    return ([float(m) for m in re.findall(r"silence_start: ([\d.]+)", log)],
            [float(m) for m in re.findall(r"silence_end: ([\d.]+)", log)])


def speech_bounds(audio: Path, duration: float) -> tuple[float, float]:
    """Locate where speech actually starts and ends inside the file.

    TTS output carries a short lead-in and trailing silence. Treating the file
    start as t=0 pushes every later cut earlier than the words it belongs to,
    so the timeline is anchored on the speech instead.
    """
    starts, ends = run_silencedetect(audio, 0.15)

    head = ends[0] if starts and abs(starts[0]) < 1e-6 and ends else 0.0
    tail = starts[-1] if starts and len(starts) > len(ends) else duration
    if tail <= head:
        tail = duration
    return head, tail


def detect_pauses(audio: Path, duration: float) -> list[float]:
    """Return the midpoint of every detected silence, excluding the tail."""
    starts, ends = run_silencedetect(audio, MIN_SILENCE)

    pauses = []
    for i, s in enumerate(starts):
        if i >= len(ends):
            break
        e = ends[i]
        if e < duration - 0.05:
            pauses.append((s + e) / 2)
    return pauses


def solve_boundaries(shots: list[dict], duration: float, pauses: list[float],
                     head: float, tail: float) -> list[float]:
    """Split [head, tail] by character weight, snapping each cut to a pause.

    Boundaries are returned in file time, but the proportional split runs over
    the spoken span only — otherwise the lead-in silence steals time from the
    first shot and every later cut drifts ahead of its words.
    """
    counts = [len(s["voiceover"]) for s in shots]
    total = sum(counts)
    span = tail - head

    targets, acc = [], 0
    for c in counts[:-1]:
        acc += c
        targets.append(head + span * acc / total)

    snapped = []
    for target in targets:
        floor = (snapped[-1] if snapped else head) + MIN_SHOT
        candidates = [p for p in pauses if floor < p < tail - MIN_SHOT]
        best = min(candidates, key=lambda p: abs(p - target), default=None)
        snapped.append(round(best, 3) if best is not None
                       and abs(best - target) <= SNAP_TOLERANCE else round(target, 3))

    # The first shot opens at the file start so the lead-in silence is covered
    # by its image; the last one runs to the end of the file.
    return [0.0] + snapped + [round(duration, 3)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio", type=Path)
    ap.add_argument("shots", type=Path, help="JSON list of {shot, voiceover}")
    ap.add_argument("output", type=Path)
    ap.add_argument("--intro", type=float, default=1.5)
    ap.add_argument("--outro", type=float, default=3.04)
    args = ap.parse_args()

    shots = json.loads(args.shots.read_text(encoding="utf-8"))
    duration = probe_duration(args.audio)
    head, tail = speech_bounds(args.audio, duration)
    pauses = detect_pauses(args.audio, duration)
    bounds = solve_boundaries(shots, duration, pauses, head, tail)

    print(f"audio {duration:.3f}s · speech {head:.3f}–{tail:.3f}s "
          f"· {len(pauses)} pauses detected\n")
    print(f"{'#':>3}  {'start':>8}  {'end':>8}  {'dur':>7}  {'chars':>5}  {'c/s':>5}")
    print("-" * 52)

    out_shots = []
    for i, shot in enumerate(shots):
        start, end = bounds[i], bounds[i + 1]
        dur = round(end - start, 3)
        chars = len(shot["voiceover"])
        rate = round(chars / dur, 2) if dur else 0.0
        out_shots.append({
            "shot": shot["shot"],
            "start": start,
            "end": end,
            "duration": dur,
            "chars": chars,
            "chars_per_second": rate,
            # Shot order and image order can diverge once paragraphs are split
            # or reordered, so an explicit mapping in the input wins.
            "image": shot.get("image", f"shot_{shot['shot']:03d}.png"),
            "voiceover": shot["voiceover"],
        })
        print(f"{shot['shot']:>3}  {start:8.3f}  {end:8.3f}  {dur:7.3f}  {chars:5d}  {rate:5.2f}")

    slow = [s for s in out_shots if s["chars_per_second"] < 3.0]
    fast = [s for s in out_shots if s["chars_per_second"] > 5.5]
    if slow or fast:
        print("\nwarning: uneven pacing — "
              f"{[s['shot'] for s in slow]} too slow, {[s['shot'] for s in fast]} too fast",
              file=sys.stderr)

    total = round(bounds[-1] + args.intro + args.outro, 3)
    print("-" * 52)
    print(f"body {bounds[-1]}s  +intro {args.intro}s +outro {args.outro}s = {total}s")
    if total > 200:
        print(f"ERROR: {total}s exceeds the 200s limit", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({
        "audio": str(args.audio),
        "body_duration": bounds[-1],
        "intro_duration": args.intro,
        "outro_duration": args.outro,
        "total_duration": total,
        "shots": out_shots,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nsaved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
