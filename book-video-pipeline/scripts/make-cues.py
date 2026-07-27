#!/usr/bin/env python3
"""Turn each shot's narration into subtitle cues with per-frame time codes.

Cues break only at punctuation, never mid-word: a line is built by packing
whole punctuation-delimited segments until the next one would overflow. Each
cue holds at most two lines so the bottom third stays readable, and each line
stays within MAX_CHARS. Cue durations follow character weight within the shot,
with a readable floor.

Usage:
    python3 make-cues.py <shot-timing.json> [--out cues.json]
"""

import argparse
import json
import re
from pathlib import Path

MAX_CHARS = 15      # preferred line length
HARD_CHARS = 18     # a segment up to this long stays whole rather than being cut mid-word
MAX_LINES = 2       # per cue
MIN_CUE = 1.2       # seconds a cue must stay on screen

PUNCT = "。！？；：，、"
# Secondary break points inside an over-long segment, in preference order.
SOFT_BREAKS = "的了是就和与或把被让给对从在为者上下中"


def segments(text: str) -> list[str]:
    """Split into punctuation-terminated segments, keeping the punctuation.

    A closing quote belongs to the sentence it ends, so a break is only taken
    after it — otherwise the quote drifts to the head of the next cue.
    """
    parts = re.split(rf"(?<=[{PUNCT}])(?![”』\"'）】」])", text)
    return [p for p in (s.strip() for s in parts) if p]


def split_long(seg: str) -> list[str]:
    """Break a segment that has no punctuation, preferring a particle boundary."""
    if len(seg) <= HARD_CHARS:
        return [seg]

    # Look for a particle near the middle so neither half is lopsided.
    lo, hi = max(4, len(seg) // 3), min(len(seg) - 4, MAX_CHARS)
    best = None
    for i in range(hi, lo - 1, -1):
        if seg[i - 1] in SOFT_BREAKS:
            best = i
            break
    if best is None:
        best = MAX_CHARS
    return [seg[:best]] + split_long(seg[best:])


def pack_lines(segs: list[str]) -> list[str]:
    """Pack whole segments into lines, never splitting a segment mid-word."""
    lines, cur = [], ""
    for seg in segs:
        if not cur:
            cur = seg
        elif len(cur) + len(seg) <= MAX_CHARS:
            cur += seg
        else:
            lines.append(cur)
            cur = seg
    if cur:
        lines.append(cur)

    out = []
    for line in lines:
        out.extend(split_long(line))
    return out


def build_cues(text: str) -> list[list[str]]:
    """Group packed lines into cues, keeping a segment's own lines together."""
    cues, cur = [], []
    for seg in segments(text):
        seg_lines = split_long(seg)

        # A segment that needs both slots starts its own cue, so a wrapped
        # sentence is never split across two on-screen cues.
        if len(seg_lines) >= MAX_LINES:
            if cur:
                cues.append(cur)
                cur = []
            for i in range(0, len(seg_lines), MAX_LINES):
                cues.append(seg_lines[i:i + MAX_LINES])
            continue

        line = seg_lines[0]
        if cur and len(cur[-1]) + len(line) <= MAX_CHARS:
            cur[-1] += line
        elif len(cur) < MAX_LINES:
            cur.append(line)
        else:
            cues.append(cur)
            cur = [line]
    if cur:
        cues.append(cur)
    return cues


def distribute(cues: list[list[str]], span: float) -> list[float]:
    weights = [sum(len(l) for l in cue) for cue in cues]
    total = sum(weights) or 1
    raw = [max(MIN_CUE, span * w / total) for w in weights]
    scale = span / sum(raw)
    return [d * scale for d in raw]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("timing", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    data = json.loads(args.timing.read_text(encoding="utf-8"))
    result = []

    for shot in data["shots"]:
        span = shot["duration"]
        cues = build_cues(shot["voiceover"])
        durations = distribute(cues, span)

        print(f"--- Frame {shot['shot']}  {span:.3f}s  {len(cues)} cues ---")
        entries, t = [], 0.0
        for cue, dur in zip(cues, durations):
            entries.append({
                "lines": cue,
                "start": round(t, 3),
                "end": round(t + dur, 3),
                "abs_start": round(shot["start"] + t, 3),
                "abs_end": round(shot["start"] + t + dur, 3),
            })
            widths = "/".join(str(len(l)) for l in cue)
            print(f"  {t:6.2f}–{t + dur:6.2f}  [{widths}]  {' ⏎ '.join(cue)}")
            t += dur
        result.append({"shot": shot["shot"], "duration": span, "cues": entries})

    over = [(r["shot"], l) for r in result for c in r["cues"]
            for l in c["lines"] if len(l) > HARD_CHARS]
    if over:
        print(f"\nwarning: {len(over)} line(s) exceed {HARD_CHARS} chars")
        for shot, line in over:
            print(f"  frame {shot}: {line}")

    if args.out:
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                            encoding="utf-8")
        print(f"\nsaved: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
