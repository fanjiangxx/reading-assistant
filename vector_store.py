from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
vector_store = Chroma(
    collection_name="finrag_chunks",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)


def ensure_indexed(chunks):
    if vector_store._collection.count() > 0:
        return
    documents = []
    ids = []
    for chunk in chunks:
        doc = Document(
            page_content=chunk["text"],
            metadata = {
                "id": chunk["id"],
                "page": chunk["page"],
                "doc_id": chunk["doc_id"],
            },
        )
        documents.append(doc)
        ids.append(chunk["id"])
    vector_store.add_documents(documents=documents, ids=ids)

def search(query, k=5):
    docs = vector_store.similarity_search(query, k=k)
    hits = []
    for doc in docs:
        hits.append(
            {
                "id": doc.metadata["id"],
                "doc_id": doc.metadata["doc_id"],
                "page": doc.metadata["page"],
                "text": doc.page_content,
            }
        )
    return hits


