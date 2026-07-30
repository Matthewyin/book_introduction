#!/usr/bin/env python3
"""genimage.py — book-video-pipeline 统一生图入口（方案 B 薄分发层）

对外一个接口，对内按能力路由：

    无 --ref  → gptsapi_image.py（中文渲染好、固定 1K、带卡死检测重试）
    有 --ref  → baoyu-image-gen main.ts（参考图 / 人物一致性，gptsapi 不支持）

提示词一律走「多文件拼接」，风格段落是常量文件，模型只写画面内容：

    --promptfiles templates/style-prefix.en.md 03-assets/scenes/shot_002.scene.md

单张：
    python3 scripts/genimage.py \
      --promptfiles templates/style-prefix.en.md scenes/shot_002.scene.md \
      --image scenes/shot_002.png --ar 9:16

批量（并发）：
    python3 scripts/genimage.py --batchfile scenes/batch.json --jobs 3

batch.json 沿用 baoyu-image-gen 的 schema，便于将来无缝切换：

    {
      "jobs": 3,
      "stylePrefix": "templates/style-prefix.en.md",
      "tasks": [
        {"id": "shot_002", "promptFiles": ["scenes/shot_002.scene.md"],
         "image": "scenes/shot_002.png", "ar": "9:16"},
        {"id": "shot_007", "promptFiles": ["scenes/shot_007.scene.md"],
         "image": "scenes/shot_007.png", "ar": "9:16",
         "ref": ["scenes/shot_002.png"]}
      ]
    }

`stylePrefix` 会被自动插到每个 task 的 promptFiles 最前面（task 内已显式写出则不重复插）。
路径相对 batch.json 所在目录解析。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GPTSAPI_SCRIPT = Path.home() / ".agents/skills/ai-content-pipeline/scripts/gptsapi_image.py"
BAOYU_MAIN = Path.home() / ".agents/skills/baoyu-image-gen/scripts/main.ts"

DEFAULT_AR = "9:16"
DEFAULT_JOBS = 3
MAX_ATTEMPTS = 2  # 分发层重试；gptsapi_image.py 内部还有 3 次

# 参考图通道的默认 provider。本机可用的生图 key 只有 GPTSAPI_KEY 和 MINIMAX_API_KEY，
# 而 gptsapi 不支持参考图，所以 --ref 默认走 MiniMax image-01 的 subject_reference
# （type=character，正好对应「同一角色跨镜一致」的需求）。
# 不钉死的话会落到用户级 EXTEND.md 的 default_provider（当前是 zai，不支持 --ref）。
DEFAULT_REF_PROVIDER = "minimax"

# 画幅 → 显式像素尺寸。实测：只给 --ar 9:16，MiniMax 出的是 720×1280，
# 拉到 1080×1920 会糊；必须同时给 --size 才拿到足尺寸。
AR_TO_SIZE = {
    "9:16": "1080x1920",
    "16:9": "1920x1080",
    "3:4": "1080x1440",
    "1:1": "1080x1080",
}


# --------------------------------------------------------------------------- 提示词

def concat_prompts(files: list[Path]) -> str:
    """按顺序拼接多个提示词文件，段落间空行分隔。"""
    parts = []
    for f in files:
        if not f.is_file():
            raise SystemExit(f"提示词文件不存在：{f}")
        text = f.read_text(encoding="utf-8").strip()
        if text:
            parts.append(text)
    if not parts:
        raise SystemExit("拼接后提示词为空")
    return "\n\n".join(parts)


# --------------------------------------------------------------------------- 后端

def run_gptsapi(prompt: str, out: Path, ar: str) -> None:
    if not GPTSAPI_SCRIPT.is_file():
        raise SystemExit(f"gptsapi 脚本缺失：{GPTSAPI_SCRIPT}")
    out.parent.mkdir(parents=True, exist_ok=True)
    # gptsapi_image.py 只收单文件，这里落临时文件传入
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as tf:
        tf.write(prompt)
        tmp = Path(tf.name)
    try:
        subprocess.run(
            [sys.executable, str(GPTSAPI_SCRIPT),
             "--prompt-file", str(tmp),
             "--aspect-ratio", ar,
             "--image", str(out)],
            check=True,
        )
    finally:
        tmp.unlink(missing_ok=True)


def resolve_bun() -> list[str]:
    if shutil.which("bun"):
        return ["bun"]
    if shutil.which("npx"):
        return ["npx", "-y", "bun"]
    raise SystemExit("需要 bun 才能走 baoyu-image-gen 通道：brew install oven-sh/bun/bun")


def run_baoyu(prompt: str, out: Path, ar: str, refs: list[Path],
              provider: str | None, model: str | None) -> None:
    if not BAOYU_MAIN.is_file():
        raise SystemExit(f"baoyu-image-gen 缺失：{BAOYU_MAIN}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as tf:
        tf.write(prompt)
        tmp = Path(tf.name)
    try:
        cmd = resolve_bun() + [
            str(BAOYU_MAIN),
            "--promptfiles", str(tmp),
            "--image", str(out),
            # 钉死 provider：EXTEND.md 的 default_provider 未必支持 --ref
            "--provider", provider or DEFAULT_REF_PROVIDER,
        ]
        # 画幅必须显式钉死，否则会落到用户级 EXTEND.md 的默认值（当前是 16:9）静默出横图。
        # 优先给像素尺寸而非 --ar：MiniMax 的 body 构造是 if(aspect_ratio) else if(size)，
        # 两个都给时 size 被忽略，只按 aspect_ratio 出 720×1280（实测）。
        size = AR_TO_SIZE.get(ar)
        cmd += ["--size", size] if size else ["--ar", ar]
        if model:
            cmd += ["--model", model]
        if refs:
            cmd += ["--ref"] + [str(r) for r in refs]
        subprocess.run(cmd, check=True)
    finally:
        tmp.unlink(missing_ok=True)


# --------------------------------------------------------------------------- 任务

class Task:
    def __init__(self, tid: str, prompt_files: list[Path], image: Path,
                 ar: str, refs: list[Path], provider: str | None, model: str | None):
        self.id = tid
        self.prompt_files = prompt_files
        self.image = image
        self.ar = ar
        self.refs = refs
        self.provider = provider
        self.model = model

    @property
    def backend(self) -> str:
        return "baoyu" if self.refs else "gptsapi"


def ensure_png(path: Path) -> str:
    """MiniMax 等后端不管扩展名一律回 JPEG，落成 .png 是"假 PNG"。

    hyperframes 读得进去，但后续任何按扩展名判断格式的环节都会踩坑，
    所以统一用 sips 就地转成真 PNG。返回一句说明或空串。
    """
    if path.suffix.lower() != ".png" or not path.is_file():
        return ""
    with path.open("rb") as f:
        if f.read(8) == b"\x89PNG\r\n\x1a\n":
            return ""
    if not shutil.which("sips"):
        return " ⚠️ 实为 JPEG（无 sips 可转）"
    subprocess.run(["sips", "-s", "format", "png", str(path), "--out", str(path)],
                   check=True, capture_output=True)
    return " (JPEG→PNG)"


def run_task(task: Task, force: bool) -> tuple[str, bool, str]:
    if task.image.is_file() and not force:
        return task.id, True, "skipped (已存在，--force 可覆盖)"

    prompt = concat_prompts(task.prompt_files)
    last = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            if task.backend == "baoyu":
                run_baoyu(prompt, task.image, task.ar, task.refs, task.provider, task.model)
            else:
                run_gptsapi(prompt, task.image, task.ar)
            if not task.image.is_file():
                raise RuntimeError("后端返回成功但文件不存在")
            note = ensure_png(task.image)
            return task.id, True, f"{task.backend} → {task.image}{note}"
        except Exception as e:  # noqa: BLE001 — 汇总到批量报告，不中断其它任务
            last = str(e)
            print(f"[{task.id}] 第 {attempt}/{MAX_ATTEMPTS} 次失败：{last}", file=sys.stderr)
    return task.id, False, last


# --------------------------------------------------------------------------- batch

def load_batch(path: Path) -> tuple[list[Task], int]:
    spec = json.loads(path.read_text(encoding="utf-8"))
    base = path.parent

    def rel(p: str) -> Path:
        q = Path(p)
        return q if q.is_absolute() else (base / q)

    style_prefix = spec.get("stylePrefix")
    jobs = int(spec.get("jobs", DEFAULT_JOBS))

    tasks = []
    for i, t in enumerate(spec.get("tasks", [])):
        tid = t.get("id") or f"task_{i + 1}"
        files = [rel(f) for f in t.get("promptFiles", [])]
        if not files:
            raise SystemExit(f"[{tid}] 缺少 promptFiles")
        if style_prefix:
            sp = rel(style_prefix)
            if sp not in files:
                files.insert(0, sp)
        image = t.get("image")
        if not image:
            raise SystemExit(f"[{tid}] 缺少 image")
        tasks.append(Task(
            tid=tid,
            prompt_files=files,
            image=rel(image),
            ar=t.get("ar") or DEFAULT_AR,
            refs=[rel(r) for r in t.get("ref", [])],
            provider=t.get("provider"),
            model=t.get("model"),
        ))
    if not tasks:
        raise SystemExit("batch 文件里没有任务")
    return tasks, jobs


# --------------------------------------------------------------------------- CLI

def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--promptfiles", nargs="+", type=Path,
                   help="提示词文件，按顺序拼接（风格前缀放第一个）")
    p.add_argument("--image", type=Path, help="输出路径（单张模式）")
    p.add_argument("--batchfile", type=Path, help="批量清单 JSON")
    p.add_argument("--jobs", type=int, help=f"并发数，默认 {DEFAULT_JOBS}")
    p.add_argument("--ar", default=DEFAULT_AR, help=f"画幅，默认 {DEFAULT_AR}")
    p.add_argument("--ref", nargs="*", type=Path, default=[],
                   help="参考图；给了就走 baoyu-image-gen")
    p.add_argument("--provider", help="仅 baoyu 通道：强制 provider")
    p.add_argument("--model", help="仅 baoyu 通道：强制 model")
    p.add_argument("--force", action="store_true", help="覆盖已存在的输出")
    args = p.parse_args()

    if args.batchfile:
        tasks, jobs = load_batch(args.batchfile)
        jobs = args.jobs or jobs
    else:
        if not args.promptfiles or not args.image:
            raise SystemExit("单张模式需要 --promptfiles 和 --image")
        tasks = [Task("single", args.promptfiles, args.image,
                      args.ar, list(args.ref), args.provider, args.model)]
        jobs = 1

    jobs = max(1, min(jobs, len(tasks)))
    print(f"[genimage] {len(tasks)} 个任务，并发 {jobs}", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        results = list(pool.map(lambda t: run_task(t, args.force), tasks))

    ok = [r for r in results if r[1]]
    bad = [r for r in results if not r[1]]

    print(f"\n[genimage] 成功 {len(ok)} / 失败 {len(bad)}", file=sys.stderr)
    for tid, _, msg in ok:
        print(f"  ✓ {tid}  {msg}", file=sys.stderr)
    for tid, _, msg in bad:
        print(f"  ✗ {tid}  {msg}", file=sys.stderr)

    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
