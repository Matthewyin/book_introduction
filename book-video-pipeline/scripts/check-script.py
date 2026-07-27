#!/usr/bin/env python3
"""Check a voiceover script against the de-AI checklist.

Covers the machine-decidable rules in references/deai-checklist.md: the AI-tell
phrase families (A1-A6), the structural tells (B1-B4) and the hard subtitle
constraints (C1-C6), plus the content-safety wordlist (D1-D5). Judgement calls
that need a human ear — whether a transition is empty, whether a line reads
aloud cleanly — are reported as reminders, not verdicts.

Usage:
    python3 check-script.py <script.md> [--before <earlier-draft.md>]
"""

import argparse
import re
import sys
from pathlib import Path

MAX_SENTENCE = 20      # chars between 。！？
MAX_RUN = 18           # chars with no punctuation at all
SENTENCE_END = "。！？"
ANY_PUNCT = "。！？；：，、"

# A1 — telling the viewer what they now feel or understand.
CONCLUDE_FOR_VIEWER = [
    r"是不是[一下]*子?轻[了松]",
    r"你会发现",
    r"看到这里[，,]?你",
    r"你就会明白",
    r"试过一次就知道",
    r"你已?经?明白了",
    r"心里[是会]?[一下]*[松轻]",
]

# A2 — narrating that what was just said matters.
NARRATED_PRAISE = [
    r"这[句话点段].{0,4}[很特别]{1,3}[关重]",
    r"很关键", r"很重要", r"特别实用", r"值得[停注]",
    r"最[狠绝妙][的]?一?[句话]", r"这就是.{0,6}的?[价意]义",
]

# A3 — announcing the next move instead of making it.
PROCESS_EXPOSED = [
    r"光说没用", r"说个场景", r"举个例子", r"打个比方",
    r"我们[先来]{1,2}看", r"接下来[我们]?[讲说看]",
    r"就在拆这件事", r"下面[我们]?[讲说]",
]

# A4 — negate-then-affirm, only flagged when it stays inside one sentence.
NEGATE_AFFIRM = [
    r"不是[^。！？]{1,12}[，,]而是",
    r"不在于[^。！？]{1,12}[，,]而在于",
    r"不只是[^。！？]{1,12}[，,]更是",
    r"不[是在]{1,2}[^。！？]{1,12}[，,]而[是在]",
]

# A5 — words that would fit any book at all.
EMPTY_BIG_WORDS = [
    r"瞬间被点醒", r"彻底改变", r"重新定义", r"颠覆",
    r"在这个时代", r"当下这个社会", r"成长的意义",
    r"从此以后", r"人生[从就]此",
]

# A6 — written-register leftovers that nobody says out loud.
WRITTEN_REGISTER = [
    r"将告诉你", r"恰恰说明", r"对于[^。！？]{1,10}来说",
    r"使得[^。！？]{1,10}得以", r"基于[^。！？]{1,8}[，,]",
    r"围绕[^。！？]{1,8}展开", r"值得注意的是", r"从某种意义上说",
]

# B1 — enumerated points read like a lecture.
ENUMERATION = [r"第[一二三四五六]{1}[，,、]", r"首先[，,]", r"其次[，,]", r"最后[，,]"]

# D — content safety.
MEDICAL = [r"治好", r"根治", r"痊愈", r"治愈"]
ABSOLUTE = [r"一定[能会]", r"必须", r"全都", r"永远[不会]", r"百分之百"]
BELITTLING = [r"你太[软弱蠢笨]", r"你怎么这么", r"活该"]
PROMISES = [r"月入", r"暴涨", r"爆款", r"改变你的人生"]

GROUPS = [
    ("A1 替观众下结论", CONCLUDE_FOR_VIEWER),
    ("A2 旁白式评价", NARRATED_PRAISE),
    ("A3 写作决策外露", PROCESS_EXPOSED),
    ("A5 空泛大词与拔高", EMPTY_BIG_WORDS),
    ("A6 书面语翻译腔", WRITTEN_REGISTER),
    ("B1 编号罗列", ENUMERATION),
    ("D1 医疗承诺", MEDICAL),
    ("D2 绝对化用词", ABSOLUTE),
    ("D3 贬低读者", BELITTLING),
    ("D5 夸大承诺", PROMISES),
]

# B3 — a device used too many times stops being a device.
DEVICES = {
    "书里说/书里还有": r"书[里中][说还有]|阿德勒说",
    "反问句": r"[？?]",
    "场景引入": r"随口一句|有没有过|想想那个",
}
DEVICE_LIMIT = {"书里说/书里还有": 3, "反问句": 6, "场景引入": 3}


def load(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if "===SCRIPT===" in text:
        text = text.split("===SCRIPT===")[1].split("===NOTES===")[0]
    return text.strip()


def find(text: str, patterns: list[str]) -> list[tuple[str, str]]:
    hits = []
    for pat in patterns:
        for m in re.finditer(pat, text):
            line = text[max(0, m.start() - 12):m.end() + 12].replace("\n", " ")
            hits.append((m.group(), line.strip()))
    return hits


def check_lengths(text: str) -> tuple[list[str], list[str]]:
    flat = text.replace("\n", "")
    long_sentences = [s.strip() for s in re.split(f"[{SENTENCE_END}]", flat)
                      if len(s.strip()) > MAX_SENTENCE]
    long_runs = [s.strip() for s in re.split(f"[{ANY_PUNCT}\n]", text)
                 if len(s.strip()) > MAX_RUN]
    return long_sentences, long_runs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("script", type=Path)
    ap.add_argument("--before", type=Path,
                    help="earlier draft, to verify the de-AI pass only removed text")
    ap.add_argument("--locked", type=Path,
                    help="paragraphs the user has frozen; excluded from checks")
    args = ap.parse_args()

    text = load(args.script)

    # Frozen paragraphs are the user's own wording — report them, don't judge them.
    locked_note = ""
    if args.locked and args.locked.is_file():
        locked = [p.strip() for p in load(args.locked).split("\n\n") if p.strip()]
        kept = [p for p in text.split("\n\n") if p.strip() not in locked]
        skipped = len(text.split("\n\n")) - len(kept)
        text = "\n\n".join(kept)
        locked_note = f"（已排除 {skipped} 段用户定稿内容）"
    chars = len(re.sub(r"\s+", "", text))
    failures = 0

    print(f"检查 {args.script.name} · {chars} 字{locked_note}\n")

    for label, patterns in GROUPS:
        hits = find(text, patterns)
        if hits:
            failures += 1
            print(f"✗ {label}  {len(hits)} 处")
            for phrase, ctx in hits[:5]:
                print(f"    「{phrase}」  …{ctx}…")
        else:
            print(f"✓ {label}  0 命中")

    # A4 allows one negate-then-affirm; more than that is a template.
    na = find(text, NEGATE_AFFIRM)
    if len(na) > 1:
        failures += 1
        print(f"✗ A4 先否定再肯定  {len(na)} 处（上限 1）")
        for phrase, ctx in na:
            print(f"    「{phrase}」")
    else:
        print(f"✓ A4 先否定再肯定  {len(na)} 处（上限 1）")

    print()
    for name, pat in DEVICES.items():
        n = len(re.findall(pat, text))
        limit = DEVICE_LIMIT[name]
        mark = "✓" if n <= limit else "✗"
        if n > limit:
            failures += 1
        print(f"{mark} B3 {name}  {n} 次（上限 {limit}）")

    print()
    long_sentences, long_runs = check_lengths(text)
    if long_sentences:
        failures += 1
        print(f"✗ C1 单句 >{MAX_SENTENCE} 字  {len(long_sentences)} 句")
        for s in long_sentences[:5]:
            print(f"    [{len(s)}字] {s}")
    else:
        print(f"✓ C1 单句 ≤{MAX_SENTENCE} 字")

    if long_runs:
        failures += 1
        print(f"✗ C2 无标点串 >{MAX_RUN} 字  {len(long_runs)} 处（字幕无法断行）")
        for s in long_runs[:5]:
            print(f"    [{len(s)}字] {s}")
    else:
        print(f"✓ C2 无标点串 ≤{MAX_RUN} 字")

    for label, needle, limit in [
        ('C4 半角引号', '"', 0),
        ("C5 长破折号", "——", 0),
    ]:
        n = text.count(needle)
        if n > limit:
            failures += 1
            print(f"✗ {label}  {n} 处")
        else:
            print(f"✓ {label}  0 处")

    colon_runs = len(re.findall(r"：[^。！？]{1,20}。[^。！？]{1,10}：", text))
    if colon_runs:
        failures += 1
        print(f"✗ C6 连环冒号  {colon_runs} 处")
    else:
        print("✓ C6 连环冒号  0 处")

    if args.before and args.before.is_file():
        before_chars = len(re.sub(r"\s+", "", load(args.before)))
        print()
        if chars > before_chars:
            failures += 1
            print(f"✗ E 只删不加  {before_chars} → {chars} 字（增加了 {chars - before_chars} 字）")
        else:
            print(f"✓ E 只删不加  {before_chars} → {chars} 字")

    print("\n" + "-" * 46)
    print("需人工判断：B2 空转过渡 · B4 收束句式雷同 · C3 朗读顺畅 · D4 观点归属")
    if failures:
        print(f"\n{failures} 项未通过，继续改稿，不要进入 TTS。")
        return 1
    print("\n自动检查全部通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
