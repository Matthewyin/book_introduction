#!/usr/bin/env python3
"""genimage.py — book-video-pipeline 统一生图入口（薄分发层）

对外一个接口，对内按"有无主角 + 有无参考图 + 配置"路由：

    无 characters / 无 --ref       → default_backend（配置，当前 gptsapi；grok 为备选）
    有 characters / 有 charRef     → ref_backend（dreamina，角色+风格双锁）
    显式 --ref（无 charRef）        → baoyu-image-gen + MiniMax（备用）

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

指定后端（覆盖配置的 default_backend）：
    python3 scripts/genimage.py ... --backend grok

批量（并发）：
    python3 scripts/genimage.py --batchfile scenes/batch.json --jobs 3

batch.json schema（charRef 自动挂到 characters:true 的 task；task 可用 backend 覆盖）：

    {
      "jobs": 3,
      "style": "templates/styles/people/cute-anime-girl.md",
      "charRef": "03-assets/protagonist-ref.png",
      "tasks": [
        {"id": "shot_002", "characters": true,
         "promptFiles": ["scenes/shot_002.scene.md"],
         "image": "scenes/shot_002.png", "ar": "9:16"},
        {"id": "shot_005", "characters": false, "backend": "grok",
         "promptFiles": ["scenes/shot_005.scene.md"],
         "image": "scenes/shot_005.png", "ar": "9:16"}
      ]
    }

所有后端路径/模型/参数从 pipeline.yaml 读取（见 scripts/config.py）。
历史兼容：旧 batch.json 的 `stylePrefix` 仍被识别（当作 style 用）。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# 配置加载器与本脚本同目录
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import cfg  # noqa: E402


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
    """MiniMax/grok 等后端不管扩展名可能回 JPEG，落成 .png 是"假 PNG"。

    统一用 sips 就地转成真 PNG。返回一句说明或空串。
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
    script = cfg.path("image.backends.gptsapi.script")
    if not script.is_file():
        raise SystemExit(f"gptsapi 脚本缺失：{script}")
    out.parent.mkdir(parents=True, exist_ok=True)
    # gptsapi_image.py 只收单文件，这里落临时文件传入
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as tf:
        tf.write(prompt)
        tmp = Path(tf.name)
    try:
        subprocess.run(
            [sys.executable, str(script),
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
    script = cfg.path("image.backends.baoyu.script")
    if not script.is_file():
        raise SystemExit(f"baoyu-image-gen 缺失：{script}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as tf:
        tf.write(prompt)
        tmp = Path(tf.name)
    try:
        cmd = resolve_bun() + [
            str(script),
            "--promptfiles", str(tmp),
            "--image", str(out),
            "--provider", provider or cfg.get("image.backends.baoyu.provider", "minimax"),
        ]
        # 画幅必须显式钉死，否则会落到用户级 EXTEND.md 的默认值（当前是 16:9）静默出横图。
        # 优先给像素尺寸而非 --ar：MiniMax body 构造是 if(aspect_ratio) else if(size)，
        # 两个都给时 size 被忽略，只按 aspect_ratio 出 720×1280（实测）。
        size_map = cfg.get("image.size_map", {})
        size = size_map.get(ar)
        cmd += ["--size", size] if size else ["--ar", ar]
        if model:
            cmd += ["--model", model]
        elif cfg.get("image.backends.baoyu.ref_model"):
            cmd += ["--model", cfg.get("image.backends.baoyu.ref_model")]
        if refs:
            cmd += ["--ref"] + [str(r) for r in refs]
        subprocess.run(cmd, check=True)
    finally:
        tmp.unlink(missing_ok=True)


def run_dreamina(prompt: str, out: Path, ar: str, refs: list[Path]) -> None:
    """dreamina image2image（Seedream 4.x/5.0）。角色 + 风格双锁的主力参考图通道。

    dreamina 提交后异步返回 submit_id + result_json。--poll 轮询等待。
    image2image 强制 ≥2k，不支持 1k（dreamina CLI 明文）。
    """
    binary = cfg.path("image.backends.dreamina.binary")
    dreamina = str(binary) if binary.is_file() else shutil.which("dreamina")
    if not dreamina:
        raise SystemExit(f"dreamina CLI 缺失：{binary}（或加入 PATH）")

    if not refs:
        raise SystemExit("dreamina image2image 需要至少 1 张参考图（--charRef 或 --ref）")
    max_refs = cfg.get("image.backends.dreamina.max_refs", 4)
    if len(refs) > max_refs:
        refs = refs[:max_refs]

    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        dreamina, "image2image",
        "--images", *[str(r) for r in refs],
        "--prompt", prompt,
        "--ratio", ar,
        "--model_version", str(cfg.get("image.backends.dreamina.model", "5.0")),
        "--resolution_type", cfg.get("image.backends.dreamina.resolution", "2k"),
        "--generate_num", "1",
        "--poll", str(cfg.get("image.backends.dreamina.poll_seconds", 240)),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    stdout = result.stdout.strip()

    url = _extract_dreamina_image_url(stdout)
    if not url:
        raise SystemExit(
            f"dreamina 未返回图片 URL。submit 输出：\n{stdout[:800]}\n"
            f"如已提交，用 `dreamina query_result --submit_id=<id>` 手动查询。"
        )
    _download(url, out)


def _extract_dreamina_image_url(stdout: str) -> str | None:
    """从 dreamina 的 JSON 输出里提取第一张图片 URL。"""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        m = re.search(r'https?://[^\s"\\]+\.png[^\s"\\]*', stdout)
        return m.group(0) if m else None
    images = (data.get("result_json") or {}).get("images") or []
    if images and isinstance(images[0], dict):
        return images[0].get("image_url")
    return None


def run_grok(prompt: str, out: Path, ar: str) -> None:
    """grok CLI 生图（备选后端）。

    grok 是 agent 式生图：模型自主调用内置 image_gen 工具（xAI Imagine API）。
    输出路径靠提示词约定 + 解析 JSON 输出捕获。非确定性，但走订阅不消耗 API key。
    认证红线：用 --always-approve（订阅继承），不读 ~/.grok/auth.json、不缓存 token。
    """
    binary = cfg.path("image.backends.grok.binary")
    grok = str(binary) if binary.is_file() else shutil.which("grok")
    if not grok:
        raise SystemExit(f"grok CLI 缺失：{binary}（或加入 PATH）")

    out.parent.mkdir(parents=True, exist_ok=True)
    # 提示词里显式声明画幅和保存路径，grok 据此调 image_gen
    full_prompt = (
        f"{prompt}\n\n"
        f"Generate a single vertical image at {ar} aspect ratio. "
        f"Save the generated image to this absolute path: {out.resolve()}"
    )
    cmd = [grok, "-p", full_prompt]
    if cfg.get("image.backends.grok.always_approve", True):
        cmd.append("--always-approve")
    fmt = cfg.get("image.backends.grok.output_format", "json")
    cmd += ["--output-format", fmt]
    if cfg.get("image.backends.grok.no_subagents", True):
        cmd.append("--no-subagents")
    cmd += ["--tools", "image_gen"]
    cmd += ["--model", cfg.get("image.backends.grok.model", "grok-4.5")]
    cmd += ["--max-turns", str(cfg.get("image.backends.grok.max_turns", 5))]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    # 优先看文件是否已落到指定路径（提示词里约定的）
    if out.is_file():
        return

    # 否则从输出里找图片路径或 URL
    located = _extract_grok_image(result.stdout + result.stderr, out)
    if not located:
        detail = (result.stdout + result.stderr)[:800]
        raise SystemExit(
            f"grok 未产出可定位的图片。输出：\n{detail}\n"
            f"可能原因：余额耗尽(402)、模型未调 image_gen、输出路径未被采纳。"
        )


def _extract_grok_image(output: str, target: Path) -> bool:
    """从 grok 输出里找图片路径或 URL，复制/下载到 target。成功返回 True。"""
    # 1. 找绝对路径（/...png）
    for m in re.finditer(r'(/[^\s"\'\\]+\.(?:png|jpg|jpeg|webp))', output, re.IGNORECASE):
        src = Path(m.group(1))
        if src.is_file():
            shutil.copy2(src, target)
            return True
    # 2. 找 URL
    m = re.search(r'https?://[^\s"\'\\]+\.(?:png|jpg|jpeg|webp)[^\s"\'\\]*', output, re.IGNORECASE)
    if m:
        try:
            _download(m.group(0), target)
            return True
        except Exception:  # noqa: BLE001
            pass
    return False


def _download(url: str, out: Path) -> None:
    import urllib.request
    scheme_ok = url.startswith("http://") or url.startswith("https://")
    if not scheme_ok:
        raise SystemExit(f"图片地址协议非法：{url}")
    req = urllib.request.Request(url, headers={"User-Agent": "book-video-pipeline/genimage"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        content = resp.read()
    out.write_bytes(content)


# 后端分发表
_BACKENDS = {
    "gptsapi": run_gptsapi,
    "baoyu": run_baoyu,
    "dreamina": run_dreamina,
    "grok": run_grok,
}


def _backend_enabled(name: str) -> bool:
    """后端是否启用：pipeline.yaml image.backends.<name>.enabled（缺省 true）。

    enabled=false 等价于该工具不可用（余额耗尽/未安装时人工关闭）。
    """
    if name not in _BACKENDS:
        return False
    return cfg.get(f"image.backends.{name}.enabled", True) is not False


# --------------------------------------------------------------------------- 任务

class Task:
    def __init__(self, tid: str, prompt_files: list[Path], image: Path,
                 ar: str, chars: bool, char_ref: Path | None, refs: list[Path],
                 backend_override: str | None, provider: str | None, model: str | None):
        self.id = tid
        self.prompt_files = prompt_files
        self.image = image
        self.ar = ar
        self.chars = chars            # 该镜是否含主角
        self.char_ref = char_ref      # episode 级主角参考图
        self.refs = refs              # 额外参考图（task 级 --ref）
        self.backend_override = backend_override  # task 级强制后端
        self.provider = provider
        self.model = model

    @property
    def backend(self) -> str:
        """路由优先级：task 级 backend 覆盖 > charRef→ref_backend > --ref→baoyu > default_backend。"""
        if self.backend_override:
            return self.backend_override
        if self.chars and self.char_ref:
            return cfg.get("image.ref_backend", "dreamina")
        if self.refs:
            return "baoyu"
        return cfg.get("image.default_backend", "gptsapi")

    @property
    def effective_refs(self) -> list[Path]:
        """dreamina/baoyu 通道用到的参考图。"""
        if self.backend in ("dreamina", "baoyu"):
            if self.backend == "dreamina" and self.char_ref:
                return [self.char_ref, *self.refs]
            return list(self.refs)
        return []

    def run_backend(self, backend: str, prompt: str) -> None:
        fn = _BACKENDS.get(backend)
        if not fn:
            raise SystemExit(f"未知后端：{backend}（可选：{', '.join(_BACKENDS)}）")
        if not _backend_enabled(backend):
            raise RuntimeError(
                f"后端 {backend} 已被禁用（pipeline.yaml image.backends.{backend}.enabled=false）"
            )
        refs = self.effective_refs
        if backend == "baoyu":
            fn(prompt, self.image, self.ar, refs, self.provider, self.model)
        elif backend == "dreamina":
            fn(prompt, self.image, self.ar, refs)
        else:
            fn(prompt, self.image, self.ar)


def run_task(task: Task, force: bool) -> tuple[str, bool, str]:
    if task.image.is_file() and not force:
        return task.id, True, "skipped (已存在，--force 可覆盖)"

    prompt = concat_prompts(task.prompt_files)
    primary = task.backend
    max_attempts = cfg.get("image.max_attempts", 2)
    last = ""
    for attempt in range(1, max_attempts + 1):
        try:
            task.run_backend(primary, prompt)
            if not task.image.is_file():
                raise RuntimeError("后端返回成功但文件不存在")
            note = ensure_png(task.image)
            return task.id, True, f"{primary} → {task.image}{note}"
        except Exception as e:  # noqa: BLE001 — 汇总到批量报告，不中断其它任务
            last = str(e)
            print(f"[{task.id}] 第 {attempt}/{max_attempts} 次失败（{primary}）：{last}", file=sys.stderr)

    # fallback：主力失败后尝试 backup_backend（仅当主力是无 ref 的 default 通道）
    backup = cfg.get("image.backup_backend")
    if backup and backup != primary and not task.refs and not task.chars:
        try:
            print(f"[{task.id}] fallback {primary}→{backup}", file=sys.stderr)
            task.run_backend(backup, prompt)
            if task.image.is_file():
                note = ensure_png(task.image)
                return task.id, True, f"{backup}(fallback) → {task.image}{note}"
        except Exception as e:  # noqa: BLE001
            last = f"{primary} 失败 + {backup} fallback 也失败：{e}"
            print(f"[{task.id}] fallback {backup} 也失败：{e}", file=sys.stderr)

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
    jobs = int(spec.get("jobs", cfg.get("image.jobs", 3)))
    default_ar = cfg.get("image.aspect_ratio", "9:16")

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
            ar=t.get("ar") or default_ar,
            chars=bool(t.get("characters", False)),
            char_ref=char_ref,
            refs=[rel(r) for r in t.get("ref", [])],
            backend_override=t.get("backend"),
            provider=t.get("provider"),
            model=t.get("model"),
        ))
    if not tasks:
        raise SystemExit("batch 文件里没有任务")
    return tasks, jobs


# --------------------------------------------------------------------------- CLI

def main() -> int:
    default_ar = cfg.get("image.aspect_ratio", "9:16")
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--promptfiles", nargs="+", type=Path,
                   help="提示词文件，按顺序拼接")
    p.add_argument("--image", type=Path, help="输出路径（单张模式）")
    p.add_argument("--batchfile", type=Path, help="批量清单 JSON")
    p.add_argument("--jobs", type=int, help="并发数")
    p.add_argument("--ar", default=default_ar, help=f"画幅，默认 {default_ar}")
    p.add_argument("--style", type=Path,
                   help="风格卡文件（自动插到 promptFiles 最前面）")
    p.add_argument("--charRef", type=Path,
                   help="主角参考图；给了且该镜 characters=true 时走 ref_backend（dreamina）")
    p.add_argument("--ref", nargs="*", type=Path, default=[],
                   help="参考图；给了（无 charRef）走 baoyu-image-gen")
    p.add_argument("--backend",
                   help=f"强制后端（覆盖配置 default_backend），可选：{','.join(_BACKENDS)}")
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
                files.remove(args.style)
                files.insert(0, args.style)
        tasks = [Task("single", files, args.image, args.ar,
                      chars=bool(args.charRef), char_ref=args.charRef,
                      refs=list(args.ref), backend_override=args.backend,
                      provider=args.provider, model=args.model)]
        jobs = 1

    jobs = max(1, min(jobs, len(tasks)))

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
