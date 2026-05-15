from typing import List, Optional
from langchain_core.documents import Document
from rag.indexer import get_vectorstore

_vectorstore = None


def _get_store():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = get_vectorstore()
    return _vectorstore


def retrieve(query: str, k: int = 4) -> List[Document]:
    return _get_store().similarity_search(query, k=k)


def retrieve_with_score_threshold(
    query: str, k: int = 6, threshold: float = 1.5
) -> List[Document]:
    """
    FAISS L2 거리 기반 score threshold 필터링.
    threshold 이하인 문서만 반환하고, 결과가 2개 미만이면 완화된 조건으로 재검색.
    """
    store = _get_store()
    docs_with_scores = store.similarity_search_with_score(query, k=k)

    # L2 distance: 낮을수록 유사도 높음 (0=동일, 2=반대)
    filtered = [doc for doc, score in docs_with_scores if score <= threshold]

    if len(filtered) < 2:
        # 1차 재검색: 임계값 완화 (threshold * 1.5)
        filtered = [doc for doc, score in docs_with_scores if score <= threshold * 1.5]

    if len(filtered) < 2:
        # 2차 재검색: threshold 무시하고 상위 3개 반환
        filtered = [doc for doc, _ in docs_with_scores[:3]]

    return filtered


def retrieve_with_metadata_filter(
    query: str, source_filter: Optional[str] = None, k: int = 4
) -> List[Document]:
    """특정 소스 파일(topic)로 범위를 좁혀 검색. 결과 부족 시 전체 검색으로 폴백."""
    store = _get_store()
    if source_filter:
        candidates = store.similarity_search(query, k=k * 3)
        filtered = [d for d in candidates if d.metadata.get("source") == source_filter]
        return filtered[:k] if len(filtered) >= 2 else store.similarity_search(query, k=k)
    return store.similarity_search(query, k=k)


def retrieve_as_text(query: str, k: int = 4) -> str:
    docs = retrieve_with_score_threshold(query, k=k + 2, threshold=1.5)
    return "\n\n---\n\n".join(
        f"[{doc.metadata.get('source', '')}]\n{doc.page_content}" for doc in docs
    )


def reload_index():
    global _vectorstore
    _vectorstore = get_vectorstore(force_rebuild=True)
