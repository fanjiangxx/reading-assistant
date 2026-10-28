"""检索入口：保证已建索引，再按问题取 top-k。"""

from __future__ import annotations

from store import load_chunks
from vector_store import ensure_indexed, search


def retrieve(problem: str, k: int = 5) -> list[dict]:
    """返回通过距离门槛的命中列表；每项含 id、doc_id、page、text、distance。"""
    ensure_indexed(load_chunks())
    return search(problem, k=k)
