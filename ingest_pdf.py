"""把 PDF 切成带页码的块。import 本模块不会打开文件。"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import pymupdf

_ROOT = Path(__file__).resolve().parent
_DEFAULT_PDF = _ROOT / "data" / "2025年美的财务报告.pdf"


class Chunk(TypedDict):
    """一块正文：稳定 id、来源文件名、页码（从 1 起）、文本。"""

    id: str
    doc_id: str
    page: int
    text: str


def split_text(text: str, size: int = 600, overlap: int = 80) -> list[str]:
    """按字符切段，相邻段重叠 overlap 个字符。空段丢掉。"""
    pieces: list[str] = []
    start = 0
    total = len(text)
    while start < total:
        end = start + size
        if end > total:
            end = total
        piece = text[start:end]
        if piece.strip():
            pieces.append(piece)
        if end >= total:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return pieces


def ingest_pdf(pdf_path: str | Path | None = None, doc_id: str | None = None) -> list[Chunk]:
    """打开一份 PDF，按页切块。默认读项目 data/ 下的美的年报。"""
    path = Path(pdf_path) if pdf_path else _DEFAULT_PDF
    if not path.exists():
        raise FileNotFoundError(f"PDF 不存在: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"需要 .pdf 文件，收到: {path.suffix or '(无后缀)'} ({path})")
    if doc_id is None:
        doc_id = path.name
    doc = pymupdf.open(path)
    result: list[Chunk] = []
    n = 0
    try:
        for page_idx, page in enumerate(doc):
            page_text = page.get_text()
            for piece in split_text(page_text, size=600, overlap=80):
                n = n + 1
                result.append(
                    {
                        "id": f"{doc_id}_{n:03d}",
                        "doc_id": doc_id,
                        "page": page_idx + 1,
                        "text": piece,
                    }
                )
    finally:
        doc.close()
    return result
