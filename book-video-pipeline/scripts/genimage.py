#!/usr/bin/env python3
"""genimage.py — book-video-pipeline 统一生图入口（薄分发层）

对外一个接口，对内按"有无主角 + 有无参考图"三档路由：

    无 characters / 无 --ref       → gptsapi_image.py（中文渲染好、固定 1K、带卡死重试）
    有 characters / 有 charRef     → dreamina image2image（Seedream 4.x/5.0，角色+风格双锁）
    显式 --ref（无 charRef）        → baoyu-image-gen + MiniMax（保留备用，对插画锁定弱）

提示词一律走「多文件拼接」，风格段落是常量文件（风格卡），模型只写画面内容：

    --style templates/styles/people/cute-anime-girl.md
    --promptfiles 03-assets/scenes/shot_002.scene.md

单张：
    python3 scripts/genimage.py \
      --style templates/styles/people/cute-anime-girl.md \
      --promptfiles scenes/shot_002.scene.md \
      --image scenes/shot_002.png --ar 9:16

带主角参考图（Seedream 通道）：
    python3 scripts/genimage.py \
      --style templates/styles/people/cute-anime-girl.md \
      --promptfiles scenes/shot_002.scene.md \
      --image scenes/shot_002.png --ar 9:16 \
      --charRef scenes/protagonist-ref.png

批量（并发）：
    python3 scripts/genimage.py --batchfile scenes/batch.json --jobs 3

batch.json schema（charRef 是 episode 级主角参考图，task 的 characters:true 自动挂上）：

    {
      "jobs": 3,
      "style": "templates/styles/people/cute-anime-girl.md",
      "charRef": "03-assets/protagonist-ref.png",
      "tasks": [
        {"id": "shot_002", "characters": true,
         "promptFiles": ["scenes/shot_002.scene.md"],
         "image": "scenes/shot_002.png", "ar": "9:16"},
        {"id": "shot_005", "characters": false,
         "promptFiles": ["scenes/shot_005.scene.md"],
         "image": "scenes/shot_005.png", "ar": "9:16"},
        {"id": "shot_007", "characters": true,
         "promptFiles": ["scenes/shot_007.scene.md"],
         "image": "scenes/shot_007.png", "ar": "9:16",
         "ref": ["scenes/shot_002.png"]}
      ]
    }

`style`（风格卡）和 `charRef`（主角参考图）都会被自动插到对应位置，不用每条 task 重复写。
路径相对 batch.json 所在目录解析。

历史兼容：旧 batch.json 的 `stylePrefix` 仍被识别（当作 style 用）。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GPTSAPI_SCRIPT = Path.home() / ".agents/skills/ai-content-pipeline/scripts/gptsapi_image.py"
BAOYU_MAIN = Path.home() / ".agents/skills/baoyu-image-gen/scripts/main.ts"
DREAMINA = Path.home() / ".local/bin/dreamina"

DEFAULT_AR = "9:16"
DEFAULT_JOBS = 3
MAX_ATTEMPTS = 2  # 分发层重试；各后端内部还有重试

# dreamina image2image 模型版本；5.0 风格质量最好。
DREAMINA_MODEL = os.environ.get("BOOK_VIDEO_DREAMINA_MODEL", "5.0")
# image2image 不支持 1k（dreamina CLI 明文），最低 2k。
DREAMINA_RESOLUTION = os.environ.get("BOOK_VIDEO_DREAMINA_RESOLUTION", "2k")
DREAMINA_POLL = int(os.environ.get("BOOK_VIDEO_DREAMINA_POLL", "240"))
# dreamina image2image 支持 1-10 张参考图；主角锁定用 1 张就够。
DREAMINA_MAX_REFS = 4

# 参考图通道（备用）：baoyu-image-gen + MiniMax。gptsapi 不支持参考图。
DEFAULT_REF_PROVIDER = "minimax"

# 画幅 → 显式像素尺寸。仅用于 baoyu/MiniMax 通道：防 MiniMax body 构造把 9:16 出成
# 720×1280（实测：if(aspect_ratio) else if(size) 两参都给时 size 被忽略）。
# Seedream (dreamina) 通道出原生 2k、gptsapi 出 1080×1920，都不缩放——素材保留原生分辨率，
# 最终 1080×1920 由 hyperframes 渲染时统一处理。
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


# --------------------------------------------------------------------------- 后处理

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
    """baoyu-image-gen + MiniMax。对 anime 插画的角色锁定较弱，保留为备用通道。"""
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
            "--provider", provider or DEFAULT_REF_PROVIDER,
        ]
        # 画幅必须显式钉死，否则会落到用户级 EXTEND.md 的默认值（当前是 16:9）静默出横图。
        # 优先给像素尺寸而非 --ar：MiniMax body 构造是 if(aspect_ratio) else if(size)，
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


def run_dreamina(prompt: str, out: Path, ar: str, refs: list[Path]) -> None:
    """dreamina image2image（Seedream 4.x/5.0）。角色 + 风格双锁的主力参考图通道。

    dreamina 提交后异步返回 submit_id + result_json。--poll 轮询等待。
    image2image 强制 ≥2k，不支持 1k（dreamina CLI 明文）；生成后由 resize_to_target 缩到 1080×1920。
    """
    if not DREAMINA.is_file():
        # 尝试 PATH 查找
        dreamina = shutil.which("dreamina")
        if not dreamina:
            raise SystemExit(f"dreamina CLI 缺失：{DREAMINA}（或加入 PATH）")
    else:
        dreamina = str(DREAMINA)

    if not refs:
        raise SystemExit("dreamina image2image 需要至少 1 张参考图（--charRef 或 --ref）")
    if len(refs) > DREAMINA_MAX_REFS:
        refs = refs[:DREAMINA_MAX_REFS]

    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        dreamina, "image2image",
        "--images", *[str(r) for r in refs],
        "--prompt", prompt,
        "--ratio", ar,
        "--model_version", DREAMINA_MODEL,
        "--resolution_type", DREAMINA_RESOLUTION,
        "--generate_num", "1",
        "--poll", str(DREAMINA_POLL),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    stdout = result.stdout.strip()

    # dreamina 输出 JSON，解析出图片 URL
    url = _extract_dreamina_image_url(stdout)
    if not url:
        raise SystemExit(
            f"dreamina 未返回图片 URL。submit 输出：\n{stdout[:800]}\n"
            f"如已提交，用 `dreamina query_result --submit_id=<id>` 手动查询。"
        )
    # 下载
    _download(url, out)


def _extract_dreamina_image_url(stdout: str) -> str | None:
    """从 dreamina 的 JSON 输出里提取第一张图片 URL。"""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        # 容错：尝试从输出里正则提取 URL
        m = re.search(r'https?://[^\s"\\]+\.png[^\s"\\]*', stdout)
        return m.group(0) if m else None
    images = (data.get("result_json") or {}).get("images") or []
    if images and isinstance(images[0], dict):
        return images[0].get("image_url")
    return None


def _download(url: str, out: Path) -> None:
    import urllib.request
    scheme_ok = url.startswith("http://") or url.startswith("https://")
    if not scheme_ok:
        raise SystemExit(f"dreamina 图片地址协议非法：{url}")
    req = urllib.request.Request(url, headers={"User-Agent": "book-video-pipeline/genimage"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        content = resp.read()
    out.write_bytes(content)


# --------------------------------------------------------------------------- 任务

class Task:
    def __init__(self, tid: str, prompt_files: list[Path], image: Path,
                 ar: str, chars: bool, char_ref: Path | None, refs: list[Path],
                 provider: str | None, model: str | None):
        self.id = tid
        self.prompt_files = prompt_files
        self.image = image
        self.ar = ar
        self.chars = chars            # 该镜是否含主角
        self.char_ref = char_ref      # episode 级主角参考图
        self.refs = refs              # 额外参考图（task 级 --ref）
        self.provider = provider
        self.model = model

    @property
    def backend(self) -> str:
        """路由：charRef 优先 dreamina；纯 --ref 走 baoyu/MiniMax；否则 gptsapi。"""
        if self.chars and self.char_ref:
            return "dreamina"
        if self.refs:
            return "baoyu"
        return "gptsapi"

    @property
    def effective_refs(self) -> list[Path]:
        """dreamina 通道用 charRef + task refs；baoyu 通道只用 task refs。"""
        if self.backend == "dreamina":
            return [self.char_ref, *self.refs] if self.char_ref else list(self.refs)
        return list(self.refs)


def run_task(task: Task, force: bool) -> tuple[str, bool, str]:
    if task.image.is_file() and not force:
        return task.id, True, "skipped (已存在，--force 可覆盖)"

    prompt = concat_prompts(task.prompt_files)
    last = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            backend = task.backend
            refs = task.effective_refs
            if backend == "dreamina":
                run_dreamina(prompt, task.image, task.ar, refs)
            elif backend == "baoyu":
                run_baoyu(prompt, task.image, task.ar, refs, task.provider, task.model)
            else:
                run_gptsapi(prompt, task.image, task.ar)
            if not task.image.is_file():
                raise RuntimeError("后端返回成功但文件不存在")
            note = ensure_png(task.image)
            # 不强制缩放：Seedream 出 2k、gptsapi 出 1080×1920，素材各自保留原生分辨率，
            # 最终统一由 hyperframes 渲染到 1080×1920（hyperframes 的 center-crop/scale 处理）。
            return task.id, True, f"{backend} → {task.image}{note}"
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

    style = spec.get("style") or spec.get("stylePrefix")
    char_ref = rel(spec["charRef"]) if spec.get("charRef") else None
    jobs = int(spec.get("jobs", DEFAULT_JOBS))

    tasks = []
    for i, t in enumerate(spec.get("tasks", [])):
        tid = t.get("id") or f"task_{i + 1}"
        files = [rel(f) for f in t.get("promptFiles", [])]
        if not files:
            raise SystemExit(f"[{tid}] 缺少 promptFiles")
        if style:
            sp = rel(style)
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
            chars=bool(t.get("characters", False)),
            char_ref=char_ref,
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
                   help="提示词文件，按顺序拼接")
    p.add_argument("--image", type=Path, help="输出路径（单张模式）")
    p.add_argument("--batchfile", type=Path, help="批量清单 JSON")
    p.add_argument("--jobs", type=int, help=f"并发数，默认 {DEFAULT_JOBS}")
    p.add_argument("--ar", default=DEFAULT_AR, help=f"画幅，默认 {DEFAULT_AR}")
    p.add_argument("--style", type=Path,
                   help="风格卡文件（自动插到 promptFiles 最前面）")
    p.add_argument("--charRef", type=Path,
                   help="主角参考图；给了且该镜 characters=true 时走 dreamina Seedream 通道")
    p.add_argument("--ref", nargs="*", type=Path, default=[],
                   help="参考图；给了（无 charRef）走 baoyu-image-gen + MiniMax")
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
        files = list(args.promptfiles)
        if args.style:
            if args.style not in files:
                files.insert(0, args.style)
            else:
                # 已在列表里则确保在最前
                files.remove(args.style)
                files.insert(0, args.style)
        # 单张模式默认当作含主角镜头（给了 charRef 就走 dreamina）
        tasks = [Task("single", files, args.image, args.ar,
                      chars=bool(args.charRef), char_ref=args.charRef,
                      refs=list(args.ref), provider=args.provider, model=args.model)]
        jobs = 1

    jobs = max(1, min(jobs, len(tasks)))

    # 后端分布预览
    backends = {}
    for t in tasks:
        backends[t.backend] = backends.get(t.backend, 0) + 1
    dist = ", ".join(f"{b}:{n}" for b, n in sorted(backends.items()))
    print(f"[genimage] {len(tasks)} 个任务，并发 {jobs}（{dist}）", file=sys.stderr)

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
