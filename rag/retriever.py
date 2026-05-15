from typing import List
from langchain_core.documents import Document
from rag.indexer import get_vectorstore

_vectorstore = None


def _get_store():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = get_vectorstore()
    return _vectorstore


def retrieve(query: str, k: int = 4) -> List[Document]:
    store = _get_store()
    return store.similarity_search(query, k=k)


def retrieve_as_text(query: str, k: int = 4) -> str:
    docs = retrieve(query, k=k)
    return "\n\n---\n\n".join(
        f"[{doc.metadata.get('source', '')}]\n{doc.page_content}" for doc in docs
    )


def reload_index():
    global _vectorstore
    _vectorstore = get_vectorstore(force_rebuild=True)
