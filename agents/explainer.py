from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from agents.state import TutorState
from utils.llm import get_llm
from rag.retriever import retrieve_as_text


SYSTEM_PROMPT = """당신은 친절한 Python 튜터입니다. RAG로 검색된 참고 자료를 바탕으로 개념을 설명하세요.

설명 원칙:
1. 레벨에 맞는 난이도로 설명 (beginner: 쉬운 비유, intermediate: 내부 동작, advanced: 심화 개념)
2. Chain-of-Thought: 개념 → 왜 필요한지 → 실제 예시 → 자주 하는 실수 순서로
3. 코드 예시는 반드시 포함하고, 실행 결과도 주석으로 표시
4. Few-shot 형식: 쉬운 예 → 실용적인 예 순서로 제시
5. 마지막에 "이해되셨나요? 연습 문제를 풀어볼까요?" 로 마무리

참고 자료:
{context}"""


def explainer_node(state: TutorState) -> TutorState:
    llm = get_llm("mini")

    last_message = state["messages"][-1].content if state["messages"] else ""
    topic = state.get("current_topic") or last_message
    level = state.get("user_level") or "beginner"

    context = retrieve_as_text(f"Python {topic}", k=4)

    prompt = SYSTEM_PROMPT.format(context=context)
    level_instruction = f"\n\n사용자 레벨: {level}\n질문: {last_message}"

    response = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=level_instruction),
    ])

    history = list(state.get("learning_history", []))
    history.append({"topic": topic, "action": "explained", "level": level})

    return {
        **state,
        "messages": [AIMessage(content=response.content)],
        "learning_history": history,
        "current_agent": "explainer",
    }
