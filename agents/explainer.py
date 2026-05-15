from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from agents.state import TutorState
from agents.tools import EXPLAINER_TOOLS, TOOLS_MAP
from utils.llm import get_llm

SYSTEM_PROMPT = """당신은 친절한 Python 튜터입니다.
개념을 설명하기 전에 반드시 search_python_docs 도구로 관련 자료를 먼저 검색하세요.
추가 맥락이 필요하면 get_learning_hints 도구도 활용하세요.

설명 원칙:
1. [도구 호출] search_python_docs로 공식 자료 검색 → 내용 기반 설명
2. 레벨에 맞는 난이도 (beginner: 쉬운 비유, intermediate: 내부 동작, advanced: 심화)
3. Chain-of-Thought: 개념 → 왜 필요한지 → 실제 예시 → 자주 하는 실수 순서
4. 코드 예시 필수 포함 (실행 결과를 주석으로 표시)
5. 마지막에 "연습 문제를 풀어볼까요? 😊" 로 마무리"""


def _react_loop(llm_with_tools, messages: list, fallback_llm) -> AIMessage:
    """ReAct 루프: 도구 호출 → 결과 반영 → 최종 응답 (최대 3회)"""
    current = list(messages)
    for _ in range(3):
        response = llm_with_tools.invoke(current)
        if not response.tool_calls:
            return response
        current.append(response)
        for tc in response.tool_calls:
            fn = TOOLS_MAP.get(tc["name"])
            result = fn.invoke(tc["args"]) if fn else "도구를 찾을 수 없습니다."
            current.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
    # 최대 반복 후 도구 없이 최종 응답
    return fallback_llm.invoke(current)


def explainer_node(state: TutorState) -> TutorState:
    llm = get_llm("mini")
    llm_with_tools = llm.bind_tools(EXPLAINER_TOOLS)

    last_message = state["messages"][-1].content if state["messages"] else ""
    level = state.get("user_level") or "beginner"
    topic = state.get("current_topic") or last_message

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"레벨: {level}\n주제: {topic}\n질문: {last_message}"),
    ]

    response = _react_loop(llm_with_tools, messages, llm)

    history = list(state.get("learning_history", []))
    topic_already_learned = any(
        h.get("topic") == topic and h.get("action") == "explained"
        for h in history
    )
    history.append({"topic": topic, "action": "explained", "level": level})

    # 첫 설명이고 재시도(retry)가 아닌 경우 → quiz 에이전트로 자동 핸드오프
    retry_count = state.get("retry_count", 0)
    next_agent = "quiz" if not topic_already_learned and retry_count == 0 else None

    return {
        **state,
        "messages": [AIMessage(content=response.content)],
        "learning_history": history,
        "current_agent": "explainer",
        "next": next_agent,
    }
