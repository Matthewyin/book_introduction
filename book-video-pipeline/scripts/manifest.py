#!/usr/bin/env python3
"""manifest.py — book-video-pipeline 运行状态机（run-manifest.json v3）

每集目录的 run-manifest.json 是「机器可读」的进度真相源：
- 每步状态用固定枚举（pending/in_progress/needs_review/approved/completed/blocked/failed）
- 每步带 artifacts（产物相对路径）与 versions（递增不覆盖）
- 顶层 current_step 指明下一步该做什么，中断后可恢复

用法：
    python3 manifest.py init <ep_dir> --book <书名> --author <作者>
    python3 manifest.py update <ep_dir> --step step4_tts --status in_progress
    python3 manifest.py update <ep_dir> --step step4_tts --status completed \
        --note "danya_xuejie 1.1x" --artifacts 03-assets/audio/voiceover.wav
    python3 manifest.py update <ep_dir> --step step3_script --versions script=3
    python3 manifest.py get <ep_dir>
    python3 manifest.py resume <ep_dir>
    python3 manifest.py migrate <ep_dir>   # v2 → v3（保留 key_decisions/video_spec）

不传 <ep_dir> 时自动探测（cwd 向上找 run-manifest.json）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 更新 manifest 后自动刷新工作区总览 CSV（存在才写，失败不阻断）
try:
    from status import write_csv_file
except ImportError:  # status.py 同目录，import 失败时跳过自动刷新
    def write_csv_file(_ws):  # type: ignore[misc]
        return None

SCHEMA_VERSION = 3

# 固定状态枚举（工厂 7 态精简版，去掉本地用不到的 failed 保留）
STATUSES = (
    "pending",        # 尚未开始
    "in_progress",    # 正在制作
    "needs_review",   # 等待用户确认（审核点）
    "approved",       # 用户已确认
    "completed",      # 完成且通过校验
    "blocked",        # 缺工具/素材/必要输入
    "failed",         # 执行失败并留有说明
)

# 步骤清单（对应 SKILL.md Step 编号）
STEPS = (
    ("step0_brand", "片头片尾+品牌角标（一次性）"),
    ("step1_profile", "选书+weread数据采集"),
    ("step2_script_brief", "Kimi K3 文案策划"),
    ("step3_script", "口播稿四道工序"),
    ("step4_tts", "MiniMax TTS 配音"),
    ("step5_shot_timing", "从音频提取真实时间轴"),
    ("step6_storyboard", "DeepSeek V4 Pro 分镜"),
    ("step7_image_generation", "生图"),
    ("step7b_cover", "封面合成"),
    ("step8_motion_plan", "动效设计"),
    ("step9_composition", "hyperframes 合成"),
    ("step10_publish", "发布物料"),
)

VALID_STEPS = {key for key, _ in STEPS}


class ManifestError(RuntimeError):
    pass


def find_manifest_dir() -> Path:
    """从 cwd 向上探测含 run-manifest.json 的目录。"""
    cwd = Path.cwd()
    for parent in (cwd, *cwd.parents):
        if (parent / "run-manifest.json").is_file():
            return parent
    raise ManifestError("未找到 run-manifest.json（请指定 ep_dir 或在集目录下运行）")


def _blank_steps() -> dict:
    steps = {key: {"status": "pending", "note": ""} for key, _ in STEPS}
    # step0 是一次性品牌资产（SKILL.md 已标注"已完成"），新集默认 completed
    steps["step0_brand"] = {"status": "completed", "note": "一次性品牌资产，全局已就位"}
    return steps


def init_manifest(ep_dir: Path, book: str, author: str) -> Path:
    path = ep_dir / "run-manifest.json"
    if path.exists():
        raise ManifestError(f"run-manifest.json 已存在，不覆盖：{path}")
    data = {
        "schema_version": SCHEMA_VERSION,
        "run_id": ep_dir.name,
        "book": book,
        "author": author,
        "current_step": "step1_profile",
        "key_decisions": [],
        "steps": _blank_steps(),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"{path} 解析失败：{exc}") from exc


def migrate(path: Path) -> bool:
    """v2 → v3：补 current_step / 步骤枚举（保留 key_decisions、video_spec）。"""
    data = _load(path)
    if data.get("schema_version") == SCHEMA_VERSION:
        return False
    if data.get("schema_version") != 2:
        raise ManifestError(f"不支持的 schema_version：{data.get('schema_version')}（仅支持 v2 → v3）")
    steps = _blank_steps()
    old = data.get("steps", {})
    for key in steps:
        if key in old and isinstance(old[key], dict):
            status = old[key].get("status")
            steps[key] = {
                "status": status if status in STATUSES else "completed" if status == "completed" else "pending",
                "note": old[key].get("note", ""),
                **({"artifacts": old[key]["artifacts"]} if old[key].get("artifacts") else {}),
                **({"versions": old[key]["versions"]} if old[key].get("versions") else {}),
            }
    data["schema_version"] = SCHEMA_VERSION
    data["current_step"] = next(
        (key for key, _ in STEPS if steps[key]["status"] in ("in_progress", "needs_review", "blocked", "failed")
         or (steps[key]["status"] == "pending")),
        "step10_publish",
    )
    data["steps"] = steps
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def _refresh_csv(path: Path) -> None:
    """从集目录向上找工作区根（episodes/ 的父目录），刷新 production.csv。"""
    ep_dir = path.parent
    for parent in (ep_dir, *ep_dir.parents):
        if (parent / "episodes").is_dir():
            try:
                write_csv_file(parent)
            except Exception:  # noqa: BLE001 — 总览刷新失败不阻断主流程
                pass
            return


def update(path: Path, step: str, status: str | None, note: str | None,
           artifacts: list[str] | None, versions: dict | None) -> dict:
    if step not in VALID_STEPS:
        raise ManifestError(f"未知步骤：{step}（可选：{', '.join(sorted(VALID_STEPS))}）")
    if status is not None and status not in STATUSES:
        raise ManifestError(f"非法状态：{status}（可选：{'/'.join(STATUSES)}）")
    data = _load(path)
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ManifestError(f"{path} 不是 v3，请先 migrate")
    entry = data["steps"].setdefault(step, {"status": "pending", "note": ""})
    if status:
        entry["status"] = status
    if note is not None:
        entry["note"] = note
    if artifacts:
        entry["artifacts"] = sorted(set(entry.get("artifacts", [])) | set(artifacts))
    if versions:
        entry["versions"] = {**entry.get("versions", {}), **{k: int(v) for k, v in versions.items()}}
    # 推进 current_step：找第一个未 completed 的步骤
    for key, _ in STEPS:
        if data["steps"].get(key, {}).get("status") != "completed":
            data["current_step"] = key
            break
    else:
        data["current_step"] = "ALL_DONE"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _refresh_csv(path)
    return data


def resume(path: Path) -> dict:
    """输出恢复指令：当前步骤 + 该步骤是否已处于可继续状态。"""
    data = _load(path)
    step = data.get("current_step", "ALL_DONE")
    if step == "ALL_DONE":
        return {"current_step": "ALL_DONE", "message": "全部步骤已完成，无恢复项"}
    entry = data["steps"].get(step, {"status": "pending"})
    note = entry.get("note", "")
    artifacts = entry.get("artifacts", [])
    existing = [a for a in artifacts if (Path(path).parent / a).exists()]
    missing = [a for a in artifacts if a not in existing]
    return {
        "current_step": step,
        "status": entry.get("status", "pending"),
        "note": note,
        "artifacts_ok": existing,
        "artifacts_missing": missing,
        "message": (
            f"下一步：{step}（{entry.get('status')}）"
            + (f"，缺产物：{', '.join(missing)}" if missing else "")
        ),
    }


def get(path: Path) -> dict:
    return _load(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="管理每集 run-manifest.json 状态机")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_ep(parser) -> None:
        parser.add_argument("ep_dir", nargs="?", default=None, help="集目录（缺省自动探测）")

    init_p = sub.add_parser("init", help="初始化 v3 manifest")
    add_ep(init_p)
    init_p.add_argument("--book", required=True)
    init_p.add_argument("--author", default="")

    upd = sub.add_parser("update", help="更新某步状态")
    add_ep(upd)
    upd.add_argument("--step", required=True)
    upd.add_argument("--status")
    upd.add_argument("--note")
    upd.add_argument("--artifacts", nargs="*", default=None)
    upd.add_argument("--versions", nargs="*", default=None,
                     help="版本号 key=value，如 script=3 audio=2")

    get_p = sub.add_parser("get", help="查看 manifest")
    add_ep(get_p)

    res = sub.add_parser("resume", help="输出恢复指令")
    add_ep(res)

    mig = sub.add_parser("migrate", help="v2 → v3 迁移")
    add_ep(mig)

    args = parser.parse_args()
    ep_dir = Path(args.ep_dir).expanduser() if args.ep_dir else find_manifest_dir()
    try:
        if args.command == "init":
            path = init_manifest(ep_dir, args.book, args.author)
            print(json.dumps({"ok": True, "manifest": str(path)}, ensure_ascii=False))
        elif args.command == "migrate":
            changed = migrate(ep_dir / "run-manifest.json")
            print(json.dumps({"ok": True, "migrated": changed}, ensure_ascii=False))
        elif args.command == "update":
            versions = None
            if args.versions:
                versions = {}
                for item in args.versions:
                    key, _, val = item.partition("=")
                    if not key or not re.fullmatch(r"\d+", val):
                        raise ManifestError(f"非法版本参数：{item}（应为 key=N）")
                    versions[key] = int(val)
            data = update(ep_dir / "run-manifest.json", args.step, args.status,
                          args.note, args.artifacts, versions)
            print(json.dumps({"ok": True, "current_step": data["current_step"],
                              "step": data["steps"][args.step]}, ensure_ascii=False))
        elif args.command == "resume":
            print(json.dumps({"ok": True, **resume(ep_dir / "run-manifest.json")}, ensure_ascii=False))
        else:  # get
            print(json.dumps(get(ep_dir / "run-manifest.json"), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ManifestError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
