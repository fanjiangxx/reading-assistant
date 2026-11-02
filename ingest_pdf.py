"""把 PDF / TXT / MD 切成统一合同的块。import 本模块不会打开文件。"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import pymupdf

_ROOT = Path(__file__).resolve().parent
_DATA_DIR = _ROOT / "data"
_DEFAULT_PDF = _DATA_DIR / "2025年美的财务报告.pdf"
_TEXT_SUFFIXES = {".txt", ".md", ".markdown"}
_SUPPORTED_SUFFIXES = {".pdf"} | _TEXT_SUFFIXES


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


def ingest_text(path: str | Path, doc_id: str | None = None) -> list[Chunk]:
    """读一份 TXT/MD，按字符切块。纯文本没有 PDF 页概念，page 固定为 1。"""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"文本不存在: {file_path}")
    suffix = file_path.suffix.lower()
    if suffix not in _TEXT_SUFFIXES:
        raise ValueError(f"需要 .txt/.md 文件，收到: {suffix or '(无后缀)'} ({file_path})")
    if doc_id is None:
        doc_id = file_path.name
    # utf-8-sig：兼容带 BOM 的 Windows 记事本文件
    text = file_path.read_text(encoding="utf-8-sig")
    pieces = split_text(text, size=600, overlap=80)
    result: list[Chunk] = []
    for n, piece in enumerate(pieces, start=1):
        result.append(
            {
                "id": f"{doc_id}_{n:03d}",
                "doc_id": doc_id,
                "page": 1,
                "text": piece,
            }
        )
    return result


def ingest_path(path: str | Path, doc_id: str | None = None) -> list[Chunk]:
    """按后缀分流：pdf → ingest_pdf；txt/md → ingest_text。"""
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return ingest_pdf(file_path, doc_id=doc_id)
    if suffix in _TEXT_SUFFIXES:
        return ingest_text(file_path, doc_id=doc_id)
    raise ValueError(
        f"暂不支持的格式 {suffix or '(无后缀)'}，仅支持: {', '.join(sorted(_SUPPORTED_SUFFIXES))}"
    )


def list_data_files(data_dir: str | Path | None = None) -> list[Path]:
    """列出 data/ 下可入库的文件（pdf/txt/md），按文件名排序。"""
    root = Path(data_dir) if data_dir else _DATA_DIR
    if not root.is_dir():
        return []
    files = [
        p
        for p in root.iterdir()
        if p.is_file() and p.suffix.lower() in _SUPPORTED_SUFFIXES
    ]
    return sorted(files, key=lambda p: p.name.lower())
