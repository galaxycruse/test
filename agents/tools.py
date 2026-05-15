import ast
from langchain_core.tools import tool
from rag.retriever import retrieve_with_score_threshold


@tool
def search_python_docs(query: str, topic: str = "") -> str:
    """Python 학습 자료에서 관련 내용을 검색합니다.
    개념 설명, 예시 코드, 함수·클래스 사용법이 필요할 때 호출하세요."""
    full_query = f"Python {topic} {query}".strip() if topic else query
    docs = retrieve_with_score_threshold(full_query, k=6, threshold=1.5)
    if not docs:
        return "관련 자료를 찾을 수 없습니다."
    return "\n\n---\n\n".join(
        f"[출처: {doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in docs
    )


@tool
def check_code_syntax(code: str) -> str:
    """Python 코드의 문법(syntax) 오류를 검사합니다.
    사용자가 코드를 제출했을 때 피드백 전에 반드시 먼저 호출하세요."""
    try:
        ast.parse(code)
        return "문법 오류 없음 ✅ — 올바른 Python 문법입니다."
    except SyntaxError as e:
        return f"문법 오류 ❌: {e.lineno}번 줄 — {e.msg}"


@tool
def get_learning_hints(topic: str, level: str = "beginner") -> str:
    """특정 주제에서 자주 발생하는 실수와 핵심 힌트를 검색합니다.
    설명 보충 또는 오답 패턴 파악이 필요할 때 호출하세요."""
    query = f"Python {topic} 자주 하는 실수 주의사항 {level}"
    docs = retrieve_with_score_threshold(query, k=3, threshold=1.8)
    if not docs:
        return "힌트를 찾을 수 없습니다."
    return "\n\n".join(doc.page_content for doc in docs)


EXPLAINER_TOOLS = [search_python_docs, get_learning_hints]
FEEDBACK_TOOLS = [check_code_syntax, search_python_docs]

TOOLS_MAP = {
    "search_python_docs": search_python_docs,
    "check_code_syntax": check_code_syntax,
    "get_learning_hints": get_learning_hints,
}
