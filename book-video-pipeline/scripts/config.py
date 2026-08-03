#!/usr/bin/env python3
"""config.py — book-video-pipeline 配置加载器

全管线可配置参数的唯一入口。所有脚本 import 本模块读取配置，
不再各自硬编码模型名/端点/后端路径。

配置文件格式：pipeline.yaml（极简 YAML 子集，见下方解析器说明）。
加载优先级（先命中先返回）：
    1. 单书覆盖：<episodes/ep00X>/book-overrides.yaml（若有）
    2. 项目级：<pipeline 根>/pipeline.yaml
    3. 用户级：~/.config/book-video-pipeline/pipeline.yaml
    4. 内置默认（DEFAULT_CONFIG，等于历史硬编码值）

API key 不在此管理——继续走环境变量 / ~/.zshrc / .baoyu-skills/.env。
本模块只管「非密钥偏好」：模型名、端点、超时、后端选择、画幅等。

路径支持 `${VAR}` 占位符（expandpath / cfg.path 自动展开）：
    ${PIPELINE_ROOT}  本 skill 根目录（自动推导，无需配置）
    ${WORKSPACE}      工作区根（pipeline.yaml `workspace.root` 指定；
                      未配置时从 cwd 向上探测含 episodes/ 或 assets/ 的目录）

单书覆盖：在集目录放 book-overrides.yaml 只写想覆盖的键（如 tts.default_voice），
与 pipeline.yaml 同构。脚本在集目录（或其子目录）下运行时自动加载；
也可显式 cfg.set_book(<集目录>) 指定。

用法：
    from config import cfg
    endpoint = cfg.get("llm.deepseek.endpoint")
    model = cfg.get("llm.deepseek.model_pro")
    backends = cfg.get("image.backends")  # 返回整个 dict
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# 本 skill 根目录（自动推导，供 ${PIPELINE_ROOT} 展开）
PIPELINE_ROOT = Path(__file__).resolve().parent.parent

# 配置文件搜索路径（先命中先返回）
_SEARCH_PATHS = [
    PIPELINE_ROOT / "pipeline.yaml",                                        # 项目级
    Path.home() / ".config" / "book-video-pipeline" / "pipeline.yaml",      # 用户级
]


# --------------------------------------------------------------------------- 默认值
# 等于历史硬编码值。pipeline.yaml 缺失或某键缺失时回退到这里，
# 保证不破坏存量行为。

DEFAULT_CONFIG: dict = {
    "image": {
        "default_backend": "gptsapi",
        "ref_backend": "dreamina",
        "backup_backend": "gptsapi",
        "backends": {
            "grok": {
                "binary": "~/.grok/bin/grok",
                "model": "grok-4.5",
                "always_approve": True,
                "output_format": "json",
                "no_subagents": True,
                "max_turns": 5,
            },
            "gptsapi": {
                "script": "~/.agents/skills/ai-content-pipeline/scripts/gptsapi_image.py",
                "aspect_ratio": "9:16",
            },
            "dreamina": {
                "binary": "~/.local/bin/dreamina",
                "model": "5.0",
                "resolution": "2k",
                "poll_seconds": 240,
                "max_refs": 4,
            },
            "baoyu": {
                "script": "~/.agents/skills/baoyu-image-gen/scripts/main.ts",
                "provider": "minimax",
                "ref_model": "image-01",
            },
        },
        "aspect_ratio": "9:16",
        "size_map": {"9:16": "1080x1920", "16:9": "1920x1080",
                     "3:4": "1080x1440", "1:1": "1080x1080"},
        "jobs": 3,
        "max_attempts": 2,
    },
    "llm": {
        "kimi": {
            "endpoint": "https://api.kimi.com/coding/v1/chat/completions",
            "model": "kimi-k3",
            "timeout": 600,
        },
        "deepseek": {
            "endpoint": "https://api.deepseek.com/v1/chat/completions",
            "model_pro": "deepseek-v4-pro",
            "model_flash": "deepseek-v4-flash",
            "timeout": 120,
        },
        "grok_review": {
            "binary": "~/.grok/bin/grok",
            "model": "grok-4.5",
            "fallback_model": "ocx-zai-glm-5-2",
        },
    },
    "tts": {
        "endpoint": "https://api.minimaxi.com/v1/t2a_v2",
        "model": "speech-02-hd",
        "default_voice": "danya_xuejie",
        "default_speed": 1.1,
        "sample_rate": 32000,
        "bitrate": 128000,
        "volume": 1.0,
        "pitch": 0,
    },
    "i2v": {
        "model_version": "seedance2.0fast_vip",
        "duration": 5,
        "resolution": "720p",
        "poll_seconds": 180,
    },
    "cover": {
        "template_dir": "${WORKSPACE}/assets/cover-image",
        "logo": "${WORKSPACE}/assets/brand/corner-lockup.png",
        "corner_right": "好书推荐",
        "template_has_brand": False,
        "series_name": "好书慢读",
        "font_title": "~/Library/Fonts/NotoSansSC-Regular.otf",
        "font_hook": "~/Library/Fonts/FandolFang-Regular.otf",
        "font_body": "~/Library/Fonts/LxgwWenKai-Regular.ttf",
        "out_3x4": "cover-final.png",
        "out_9x16": "cover-final-9x16.png",
    },
}


# --------------------------------------------------------------------------- 极简 YAML 解析器
# 只支持本项目用到的结构：缩进嵌套 + `key: value` + 注释（#）。
# 标量类型推断：int / float / bool (true/false) / str。
# 值带引号时去引号；~ 开头的路径保持原样（由 expandpath 处理）。
# 不支持：列表、多行字符串、锚点、流式语法。够用即可，避免引入 pyyaml 依赖。

_BOOL = {"true": True, "false": False, "yes": True, "no": False, "null": None, "~": None}


def _strip_comment(line: str) -> str:
    """去掉行内注释。但引号内的 # 不算注释。"""
    in_squote = in_dquote = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_dquote:
            in_squote = not in_squote
        elif ch == '"' and not in_squote:
            in_dquote = not in_dquote
        elif ch == "#" and not in_squote and not in_dquote:
            return line[:i]
    return line


def _scalar(raw: str):
    """把字符串值推断为 int/float/bool/None/str。"""
    s = raw.strip()
    if not s:
        return ""
    low = s.lower()
    if low in _BOOL:
        return _BOOL[low]
    # 去引号
    if (s[0] == s[-1]) and s[0] in ("'", '"'):
        return s[1:-1]
    # int
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    # float
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    return s


def _parse_yaml(text: str) -> dict:
    """极简 YAML 子集解析：缩进嵌套 dict。

    缩进必须用空格（不能用 tab）。每 2 空格一级（实际按相对缩进计算）。
    """
    root: dict = {}
    # stack: [(indent_level, dict_obj)]，根在 index 0
    stack = [(0, root)]
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = _strip_comment(raw)
        if not line.strip():
            continue
        if "\t" in line:
            raise ValueError(f"YAML 第 {lineno} 行含 tab，请用空格缩进：{raw.strip()}")
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        # 弹栈到当前缩进的父级（同级键也是兄弟：indent <= 栈顶时弹栈）
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent_indent, parent = stack[-1]
        if indent < parent_indent:
            # 回到根
            stack = [(0, root)]
            parent = root
        if ":" not in stripped:
            raise ValueError(f"YAML 第 {lineno} 行无 key: {raw.strip()}")
        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            # 子 dict 起点
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _scalar(val)
    return root


def _deep_merge(base: dict, override: dict) -> dict:
    """把 override 深合并到 base（override 优先），返回新 dict，不改入参。"""
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


# --------------------------------------------------------------------------- 路径展开

def _find_workspace_root() -> Path | None:
    """从 cwd 向上探测工作区根：含 episodes/ 或 assets/ 目录的最近父目录。"""
    cwd = Path.cwd()
    for parent in (cwd, *cwd.parents):
        if (parent / "episodes").is_dir() or (parent / "assets").is_dir():
            return parent
    return None


def workspace_root() -> Path:
    """确定 ${WORKSPACE} 指向：pipeline.yaml `workspace.root` > 自动探测 > skill 根。

    workspace.root 只做 ~ 展开（不做 ${VAR}，避免循环引用）。
    """
    for path in _SEARCH_PATHS:
        if path.is_file():
            try:
                data = _parse_yaml(path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            root = (data.get("workspace") or {}).get("root")
            if root:
                # 只做 ~ 展开，不展开 ${VAR}（否则与 expandpath 的 ${WORKSPACE} 递归）
                s = str(root)
                if s.startswith("~"):
                    s = os.path.expanduser(s)
                return Path(s)
    detected = _find_workspace_root()
    if detected:
        return detected
    return PIPELINE_ROOT


def expandpath(p: str | Path) -> Path:
    """展开 ${VAR} 占位符、~ 和 $HOME。

    支持 ${PIPELINE_ROOT}（skill 根）与 ${WORKSPACE}（工作区根，见 workspace_root）。
    """
    s = str(p)
    s = s.replace("${PIPELINE_ROOT}", str(PIPELINE_ROOT))
    s = s.replace("${WORKSPACE}", str(workspace_root()))
    if s.startswith("~"):
        s = os.path.expanduser(s)
    return Path(s)


# --------------------------------------------------------------------------- 加载

def _load_file(paths: list[Path]) -> dict | None:
    for path in paths:
        if path.is_file():
            try:
                return _parse_yaml(path.read_text(encoding="utf-8"))
            except Exception as e:  # noqa: BLE001
                print(f"[config] 警告：{path} 解析失败，回退默认值：{e}", file=sys.stderr)
                return None
    return None


def _find_book_dir() -> Path | None:
    """从 cwd 向上探测集目录：含 run-manifest.json 的最近父目录。

    脚本在 episodes/ep00X/ 下（或其子目录）运行时，自动加载该集 book-overrides.yaml。
    """
    cwd = Path.cwd()
    for parent in (cwd, *cwd.parents):
        if (parent / "run-manifest.json").is_file():
            return parent
    return None


def _load_book_overrides(book_dir: Path | None) -> dict | None:
    if book_dir is None:
        return None
    path = book_dir / "book-overrides.yaml"
    if not path.is_file():
        return None
    try:
        return _parse_yaml(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"[config] 警告：{path} 解析失败，忽略单书覆盖：{e}", file=sys.stderr)
        return None


def _resolve_config(book_dir: Path | None = None) -> dict:
    data = DEFAULT_CONFIG
    file_cfg = _load_file(_SEARCH_PATHS)
    if file_cfg:
        data = _deep_merge(data, file_cfg)
    book_cfg = _load_book_overrides(book_dir)
    if book_cfg:
        data = _deep_merge(data, book_cfg)
    return data


# --------------------------------------------------------------------------- 公开接口

class _Config:
    """单例配置访问。get("a.b.c") 走点号路径；缺失返回 default。"""

    def __init__(self):
        self._book_dir = _find_book_dir()
        self._data = _resolve_config(self._book_dir)

    @property
    def book_dir(self) -> Path | None:
        """当前生效的单书覆盖目录（自动探测或 set_book 指定）。"""
        return self._book_dir

    def set_book(self, book_dir: str | Path | None):
        """显式指定集目录以加载其 book-overrides.yaml；None 清除覆盖。"""
        self._book_dir = None if book_dir is None else Path(book_dir)
        self._data = _resolve_config(self._book_dir)

    def get(self, dotted_key: str, default=None):
        node = self._data
        for part in dotted_key.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def path(self, dotted_key: str, default=None) -> Path:
        """get 的路径版：自动展开 ${VAR}/~ 并返回 Path 对象。"""
        val = self.get(dotted_key, default)
        if val is None:
            return None  # type: ignore[return-value]
        return expandpath(val)

    def reload(self):
        """重新读配置（测试/运行时改了 pipeline.yaml 后调用）。"""
        self._book_dir = _find_book_dir()
        self._data = _resolve_config(self._book_dir)


cfg = _Config()
