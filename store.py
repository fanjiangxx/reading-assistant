"""切块名单。import 时不读 PDF；第一次 load_chunks() 才解析。"""

from __future__ import annotations

from ingest_pdf import Chunk, ingest_pdf

_chunks: list[Chunk] | None = None


def load_chunks() -> list[Chunk]:
    """返回年报切块；结果缓存在进程里，避免重复打开 PDF。"""
    global _chunks
    if _chunks is None:
        _chunks = ingest_pdf()
    return _chunks


if __name__ == "__main__":
    print(len(load_chunks()))
