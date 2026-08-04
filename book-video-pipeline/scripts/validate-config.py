#!/usr/bin/env python3
"""validate-config.py — book-video-pipeline 全局配置校验

检查 pipeline.yaml / 工作区资产 / 后端工具是否齐备，开工前跑一遍，
避免字体缺失、后端 binary 消失等问题到运行时才炸。

用法：
    python3 scripts/validate-config.py          # 校验默认配置
    python3 scripts/validate-config.py --book episodes/ep005-心流  # 含单书覆盖

检查项：
    - pipeline.yaml 必填字段完整性（缺键报 error）
    - 布尔 / 整数 / 枚举字段类型
    - 路径类字段展开后文件存在性（字体、封面底图、logo、定妆图、后端 binary/script）
    - 后端 enabled 开关（阶段五后生效）
退出码：0 = 无 error；1 = 有 error（warning 不阻断）。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import cfg, DEFAULT_CONFIG, _SEARCH_PATHS, _parse_yaml, expandpath, PIPELINE_ROOT, workspace_root  # noqa: E402

# 必填字段（点号路径）：值缺失或为 None 时报 error
REQUIRED = {
    "image.default_backend": "生图默认后端",
    "image.ref_backend": "参考图后端",
    "image.aspect_ratio": "画幅",
    "llm.kimi.endpoint": "Kimi endpoint",
    "llm.deepseek.model_pro": "DeepSeek Pro 模型",
    "llm.deepseek.model_flash": "DeepSeek Flash 模型",
    "tts.endpoint": "TTS endpoint",
    "tts.model": "TTS 模型",
    "cover.template_dir": "封面模板目录",
    "cover.out_3x4": "3:4 封面输出名",
    "cover.out_9x16": "9:16 封面输出名",
}

# 布尔字段
BOOLEAN_FIELDS = {
    "image.backends.grok.always_approve",
    "cover.template_has_brand",
}

# 正整数字段
POSITIVE_INT_FIELDS = {
    "image.jobs",
    "image.max_attempts",
    "image.backends.dreamina.poll_seconds",
    "image.backends.dreamina.max_refs",
    "llm.kimi.timeout",
    "llm.deepseek.timeout",
    "tts.sample_rate",
    "tts.bitrate",
}

# 枚举字段：值必须在给定集合内
ENUM_FIELDS = {
    "image.default_backend": {"openrouter", "grok", "gptsapi", "dreamina", "baoyu"},
    "image.ref_backend": {"dreamina", "baoyu"},
}

# 路径类字段：展开后必须存在（缺文件报 error；显式标注可缺省的除外）
REQUIRED_FILES = {
    "cover.template_dir": "封面模板目录（应有 cover-3x4.png / cover-9x16.png）",
    "cover.logo": "品牌 logo",
    "cover.font_title": "书名字体",
    "cover.font_title_viral": "病毒标题字体",
    "cover.font_hook": "钩子字体",
    "cover.font_body": "正文字体",
    "image.backends.grok.binary": "grok CLI",
    "image.backends.openrouter.script": "openrouter 脚本",
    "image.backends.dreamina.binary": "dreamina CLI",
}

# 工作区资产（相对 ${WORKSPACE}，与 REQUIRED_FILES 分开以便提示路径）
WORKSPACE_ASSETS = {
    "assets/protagonist-base/anime-girl.png": "动漫·女孩定妆图",
    "assets/protagonist-base/anime-boy.png": "动漫·男孩定妆图",
    "assets/protagonist-base/realistic-literary-female.png": "写实·文艺女定妆图",
    "assets/protagonist-base/realistic-intellectual-female.png": "写实·知性女定妆图",
    "assets/protagonist-base/realistic-literary-male.png": "写实·文艺男定妆图",
    "assets/protagonist-base/realistic-intellectual-male.png": "写实·知性男定妆图",
}


def check_required(values: dict) -> list[str]:
    errors = []
    for key, label in REQUIRED.items():
        if key not in values or values[key] in (None, ""):
            errors.append(f"✗ 缺少必需字段：{key}（{label}）")
    return errors


def check_types(values: dict) -> list[str]:
    errors = []
    for key in BOOLEAN_FIELDS:
        if key in values and values[key] not in (True, False):
            errors.append(f"✗ {key} 必须为 true/false，当前：{values[key]!r}")
    for key in POSITIVE_INT_FIELDS:
        if key in values:
            val = values[key]
            if not isinstance(val, int) or isinstance(val, bool) or val <= 0:
                errors.append(f"✗ {key} 必须为正整数，当前：{val!r}")
    for key, allowed in ENUM_FIELDS.items():
        if key in values and values[key] not in allowed:
            errors.append(f"✗ {key} 必须 ∈ {sorted(allowed)}，当前：{values[key]!r}")
    return errors


def collect_paths(config_path: Path) -> dict:
    """读取配置文件的极简 YAML，返回 点号路径 → 值 的扁平 dict（含嵌套）。"""
    try:
        data = _parse_yaml(config_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {}
    flat: dict = {}

    def walk(node: dict, prefix: str) -> None:
        for key, val in node.items():
            dotted = f"{prefix}.{key}" if prefix else key
            if isinstance(val, dict):
                walk(val, dotted)
            else:
                flat[dotted] = val

    walk(data, "")
    return flat


def check_files(flat: dict, base_dir: Path, book_dir: Path | None) -> tuple[list[str], list[str]]:
    """检查路径类字段 + 工作区资产存在性。返回 (errors, warnings)。"""
    errors, warnings = [], []
    # 配置里的路径字段（${WORKSPACE}/~ 由 expandpath 展开）
    for key, label in REQUIRED_FILES.items():
        raw = flat.get(key)
        if not raw:
            continue  # 缺失由 check_required 报
        p = expandpath(str(raw))
        if p.is_dir():
            if not any(p.glob("cover-3x4*")):
                errors.append(f"✗ {key}（{label}）目录下未找到 cover-3x4 母版：{p}")
        elif not p.is_file():
            errors.append(f"✗ {key}（{label}）不存在：{p}")
    # 工作区资产
    ws = workspace_root()
    for rel, label in WORKSPACE_ASSETS.items():
        p = ws / rel
        if not p.is_file():
            errors.append(f"✗ 工作区资产缺失：{rel}（{label}）→ {p}")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 book-video-pipeline 全局配置")
    parser.add_argument("--book", default=None, help="集目录（可选，同时校验其 book-overrides.yaml）")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    # 显式指定集目录时，让 cfg 加载其覆盖
    if args.book:
        cfg.set_book(args.book)
    else:
        cfg.reload()

    # 1) 找到实际生效的 pipeline.yaml（项目级或用户级）
    config_path = next((p for p in _SEARCH_PATHS if p.is_file()), None)
    flat = collect_paths(config_path) if config_path else {}

    errors: list[str] = []
    warnings: list[str] = []

    # 2) 字段校验（用合并后的 cfg 值，反映覆盖结果）
    merged = {}
    def walk(node, prefix=""):
        for key, val in node.items():
            dotted = f"{prefix}.{key}" if prefix else key
            if isinstance(val, dict):
                walk(val, dotted)
            else:
                merged[dotted] = val
    walk(cfg._data)
    errors += check_required(merged)
    errors += check_types(merged)

    # 3) 文件存在性
    file_errors, file_warnings = check_files(flat, config_path.parent if config_path else PIPELINE_ROOT, cfg.book_dir)
    errors += file_errors
    warnings += file_warnings

    # 4) 单书覆盖文件本身可解析（若存在）
    if cfg.book_dir:
        ovr = cfg.book_dir / "book-overrides.yaml"
        if ovr.is_file():
            try:
                _parse_yaml(ovr.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"✗ book-overrides.yaml 解析失败：{ovr}（{exc}）")

    result = {"ok": not errors, "errors": errors, "warnings": warnings,
              "config": str(config_path) if config_path else "(内置默认)"}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"配置源：{result['config']}")
        for e in errors:
            print(e)
        for w in warnings:
            print(f"⚠ {w}")
        if not errors:
            print("✓ 配置校验通过")
        elif warnings:
            print(f"✓ 校验完成：{len(errors)} 个错误，{len(warnings)} 个警告")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
