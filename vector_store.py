"""向量索引。import 时不加载嵌入模型；第一次 ensure_indexed / search 才创建。"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env", override=True)

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

_store: Chroma | None = None


def _get_store() -> Chroma:
    """惰性创建 Chroma。路径绑项目根，避免在子目录跑脚本时写出第二套库。"""
    global _store
    if _store is not None:
        return _store
    model_name = (
        os.getenv("FINRAG_EMBEDDING_MODEL")
        or "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ).strip()
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    _store = Chroma(
        collection_name="finrag_chunks",
        embedding_function=embeddings,
        persist_directory=str(_ROOT / "chroma_db"),
    )
    return _store


def _indexed_count() -> int:
    # 公开 get；ids 总会返回。不要用 vector_store._collection（私有）。
    return len(_get_store().get(include=[])["ids"])


def ensure_indexed(chunks: list[dict], rebuild: bool | None = None) -> None:
    """库空则写入；FINRAG_REBUILD_INDEX=1 或 rebuild=True 时先清空再写。"""
    store = _get_store()
    if rebuild is None:
        rebuild = (os.environ.get("FINRAG_REBUILD_INDEX") or "").strip().lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
    if rebuild:
        store.reset_collection()
    elif _indexed_count() > 0:
        return
    documents = []
    ids = []
    for chunk in chunks:
        documents.append(
            Document(
                page_content=chunk["text"],
                metadata={
                    "id": chunk["id"],
                    "page": chunk["page"],
                    "doc_id": chunk["doc_id"],
                },
            )
        )
        ids.append(chunk["id"])
    store.add_documents(documents=documents, ids=ids)


def search(query: str, k: int = 5) -> list[dict]:
    """返回带 distance 的命中。Chroma 距离越小越相似。

    FINRAG_MAX_DISTANCE：超过该距离的命中丢弃（本项目约定）。
    本库实测：相关问句 top 距离常在约 4～9；明显乱问可到 15+。
    默认 12：挡住明显不相关，不挡同域跨公司题（拒答仍靠题型与提示词）。
    """
    raw = (os.environ.get("FINRAG_MAX_DISTANCE") or "12").strip()
    max_distance = float(raw)
    pairs = _get_store().similarity_search_with_score(query, k=k)
    hits = []
    for doc, distance in pairs:
        if distance > max_distance:
            continue
        hits.append(
            {
                "id": doc.metadata["id"],
                "doc_id": doc.metadata["doc_id"],
                "page": doc.metadata["page"],
                "text": doc.page_content,
                "distance": float(distance),
            }
        )
    return hits
