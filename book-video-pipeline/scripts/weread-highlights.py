#!/usr/bin/env python3
"""weread-highlights.py — 微信读书全书热门划线 Top20 获取

用法:
    python3 weread-highlights.py --book "一生 莫泊桑" --output quotes-top20.json
    python3 weread-highlights.py --book-id 3300038408 --output quotes-top20.json

调微信读书 Agent API Gateway:
    POST https://i.weread.qq.com/api/agent/gateway
    Header: Authorization: Bearer $WEREAD_API_KEY

流程:
    1. (可选) /store/search 搜书名 → bookId
    2. /book/bestbookmarks 获取全书热门划线 Top20（含划线原文+划线人数+章节）

输出 JSON:
    [{"rank":1, "markText":"...", "totalCount":1320, "chapterUid":16, "chapterTitle":"..."}, ...]
"""

import argparse
import json
import os
import sys
import urllib.request

API_URL = "https://i.weread.qq.com/api/agent/gateway"
SKILL_VERSION = "1.0.4"


def load_key() -> str:
    key = os.environ.get("WEREAD_API_KEY", "")
    if not key:
        sys.exit("WEREAD_API_KEY 未设置。export WEREAD_API_KEY=wrk-xxxxxxxx")
    return key


def api_call(api_name: str, key: str, **params) -> dict:
    body = {"api_name": api_name, "skill_version": SKILL_VERSION, **params}
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def search_book(keyword: str, key: str) -> list[dict]:
    """搜书，返回 [{bookId, title, author}] 列表。"""
    data = api_call("/store/search", key, keyword=keyword, count=5)
    results = []
    for group in data.get("results", []):
        for book in group.get("books", []):
            info = book.get("bookInfo", {})
            results.append({
                "bookId": info.get("bookId", ""),
                "title": info.get("title", ""),
                "author": info.get("author", ""),
            })
    return results


def get_best_bookmarks(book_id: str, key: str) -> list[dict]:
    """获取全书热门划线 Top20。"""
    data = api_call("/book/bestbookmarks", key, bookId=book_id, chapterUid=0)
    items = data.get("items", [])
    # 章节映射
    chapters = {}
    for ch in data.get("chapters", []):
        chapters[ch.get("chapterUid")] = ch.get("title", "")
    results = []
    for i, item in enumerate(items):
        results.append({
            "rank": i + 1,
            "markText": item.get("markText", ""),
            "totalCount": item.get("totalCount", 0),
            "chapterUid": item.get("chapterUid", 0),
            "chapterTitle": chapters.get(item.get("chapterUid", 0), ""),
        })
    return results


def main() -> int:
    p = argparse.ArgumentParser(description="微信读书全书热门划线 Top20")
    p.add_argument("--book", help="书名搜索关键词（如 '一生 莫泊桑'）")
    p.add_argument("--book-id", help="直接指定 bookId（跳过搜索）")
    p.add_argument("--output", required=True, help="输出 JSON 文件路径")
    args = p.parse_args()

    key = load_key()

    if args.book_id:
        book_id = args.book_id
        print(f"使用指定 bookId: {book_id}")
    elif args.book:
        print(f"搜索 '{args.book}'…")
        books = search_book(args.book, key)
        if not books:
            print("未找到书籍。")
            return 1
        if len(books) == 1:
            book_id = books[0]["bookId"]
            print(f"  → {books[0]['title']} | {books[0]['author']} | {book_id}")
        else:
            print("找到多本书，请选择:")
            for i, b in enumerate(books):
                print(f"  [{i}] {b['title']} | {b['author']} | {b['bookId']}")
            choice = input("输入序号（默认0）: ").strip()
            idx = int(choice) if choice.isdigit() else 0
            book_id = books[idx]["bookId"]
    else:
        p.error("需要 --book 或 --book-id")

    print(f"获取热门划线 Top20…")
    bookmarks = get_best_bookmarks(book_id, key)
    print(f"  → 共 {len(bookmarks)} 条\n")

    for bm in bookmarks:
        print(f"[{bm['rank']}] 划线{bm['totalCount']}人 | {bm['chapterTitle']}")
        print(f"    {bm['markText'][:70]}")
        print()

    import pathlib
    out = pathlib.Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(bookmarks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已保存: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
