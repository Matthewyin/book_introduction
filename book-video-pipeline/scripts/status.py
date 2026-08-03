#!/usr/bin/env python3
"""status.py — book-video-pipeline 多集生产总览

扫描 episodes/ 下所有集的 run-manifest.json（v3），聚合输出一张总览表：
每集一行，列出各阶段状态、当前步骤、阻塞集。数据源是 manifest（真相源），
CSV 只是视图——不双写。

用法：
    python3 scripts/status.py                  # 总览表
    python3 scripts/status.py --csv            # 输出 CSV 到 stdout
    python3 scripts/status.py --workspace ~/Coding/video   # 指定工作区
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import workspace_root  # noqa: E402

# 总览列顺序（对应 manifest 步骤；中文表头对齐生产习惯）
COLUMNS = [
    ("run_id", "编号"),
    ("book", "书名"),
    ("step1_profile", "选书"),
    ("step2_script_brief", "策划"),
    ("step3_script", "文案"),
    ("step4_tts", "配音"),
    ("step5_shot_timing", "时间轴"),
    ("step6_storyboard", "分镜"),
    ("step7_image_generation", "生图"),
    ("step7b_cover", "封面"),
    ("step8_motion_plan", "动效"),
    ("step9_composition", "合成"),
    ("step10_publish", "发布"),
]

STATUS_SHORT = {
    "pending": "·",
    "in_progress": "…",
    "needs_review": "审",
    "approved": "✓",
    "completed": "✓",
    "blocked": "✗",
    "failed": "✗",
}


def find_manifests(ws: Path) -> list[Path]:
    episodes = ws / "episodes"
    if not episodes.is_dir():
        return []
    return sorted(
        p for p in episodes.glob("*/run-manifest.json")
        if p.is_file()
    )


def load_manifest(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if data.get("schema_version") != 3:
        return None  # 非 v3 不参与总览，提示先 migrate
    return data


def summarize(ws: Path) -> list[dict]:
    rows = []
    for manifest_path in find_manifests(ws):
        data = load_manifest(manifest_path)
        if data is None:
            rows.append({"run_id": manifest_path.parent.name, "book": "(非 v3，请 migrate)", **{k: "" for k, _ in COLUMNS[2:]}})
            continue
        row = {"run_id": data.get("run_id", manifest_path.parent.name),
               "book": data.get("book", "")}
        steps = data.get("steps", {})
        for key, _ in COLUMNS[2:]:
            status = steps.get(key, {}).get("status", "pending")
            row[key] = STATUS_SHORT.get(status, status)
        row["_current"] = data.get("current_step", "")
        row["_ep_dir"] = str(manifest_path.parent)
        rows.append(row)
    return rows


def to_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([label for _, label in COLUMNS])
    for row in rows:
        writer.writerow([row.get(key, "") for key, _ in COLUMNS])
    return buf.getvalue()


def write_csv_file(ws: Path) -> Path | None:
    """把总览写到 <workspace>/episodes/production.csv。返回路径或 None（无集目录）。"""
    episodes = ws / "episodes"
    if not episodes.is_dir():
        return None
    rows = summarize(ws)
    out = episodes / "production.csv"
    out.write_text(to_csv(rows), encoding="utf-8")
    return out


def print_table(rows: list[dict], ws: Path) -> None:
    if not rows:
        print(f"（{ws}/episodes 下未找到集目录）")
        return
    header = [label for _, label in COLUMNS]
    widths = [len(h) for h in header]
    for row in rows:
        for i, (key, _) in enumerate(COLUMNS):
            widths[i] = max(widths[i], len(str(row.get(key, ""))))
    line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(header))
    print(line)
    print("-" * len(line))
    for row in rows:
        cells = [str(row.get(key, "")).ljust(widths[i]) for i, (key, _) in enumerate(COLUMNS)]
        print("  ".join(cells))
        current = row.get("_current", "")
        if current and current != "ALL_DONE":
            print(f"    ↳ 进行中：{current}（{row['_ep_dir']}）")
    # 阻塞提示
    blocked = [r for r in rows if "✗" in {r.get(k, "") for k, _ in COLUMNS[2:]}]
    if blocked:
        print()
        print("⚠ 有阻塞/失败步骤的集：")
        for r in blocked:
            failed = [label for (k, label) in COLUMNS[2:] if r.get(k) == "✗"]
            print(f"  - {r['run_id']}：{'/'.join(failed)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="多集生产总览")
    parser.add_argument("--workspace", default=None, help="工作区根（缺省自动探测）")
    parser.add_argument("--csv", action="store_true", help="输出 CSV")
    args = parser.parse_args()

    ws = Path(args.workspace).expanduser() if args.workspace else workspace_root()
    rows = summarize(ws)
    if args.csv:
        print(to_csv(rows), end="")
    else:
        print_table(rows, ws)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
