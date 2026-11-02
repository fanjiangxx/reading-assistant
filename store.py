"""切块名单。import 时不读文件；第一次 load_chunks() 才解析 data/ 下支持的格式。"""

from __future__ import annotations

from ingest_pdf import Chunk, ingest_path, list_data_files

_chunks: list[Chunk] | None = None


def load_chunks() -> list[Chunk]:
    """返回 data/ 下全部 pdf/txt/md 的切块；进程内缓存。

    data/ 里一张支持的文件都没有时直接报错，不再偷偷改去读「默认年报」——
    默认 PDF 若存在，本来就会被 list_data_files 扫到；空目录应明确失败。
    """
    global _chunks
    if _chunks is None:
        files = list_data_files()
        if not files:
            raise FileNotFoundError(
                "在 data/ 下没有找到可入库的 .pdf/.txt/.md。"
                "请把文档放进该文件夹后再提问。"
            )
        merged: list[Chunk] = []
        for path in files:
            merged.extend(ingest_path(path))
        _chunks = merged
    return _chunks


if __name__ == "__main__":
    chunks = load_chunks()
    print(len(chunks))
    docs = sorted({c["doc_id"] for c in chunks})
    print("docs:", ", ".join(docs))
