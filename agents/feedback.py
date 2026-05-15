from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from pydantic import BaseModel, Field
from typing import List, Optional
from agents.state import TutorState
from agents.tools import FEEDBACK_TOOLS, TOOLS_MAP
from utils.llm import get_llm


class FeedbackResult(BaseModel):
    is_correct: bool = Field(description="코드가 문제를 올바르게 풀었는지 여부")
    score: int = Field(description="0~100점 점수")
    good_points: List[str] = Field(description="잘한 점 목록")
    improvements: List[str] = Field(description="개선할 점 목록")
    mistake_pattern: Optional[str] = Field(None, description="반복될 수 있는 실수 패턴")
    display_message: str = Field(description="사용자에게 보여줄 피드백 메시지 (마크다운)")


SYSTEM_PROMPT = """당신은 꼼꼼한 Python 코드 리뷰어입니다.
코드를 받으면 반드시 check_code_syntax 도구로 문법을 먼저 확인하세요.
필요하다면 search_python_docs 도구로 올바른 패턴을 검색해 비교하세요.

피드백 원칙:
1. [도구 호출] check_code_syntax 먼저 → 문법 오류 확인
2. 잘한 점 먼저 칭찬 (긍정적 강화)
3. 개선점은 "왜 이게 문제인지" 설명과 함께 제시
4. 레벨에 맞는 수준으로 피드백"""


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
    return fallback_llm.invoke(current)


def feedback_node(state: TutorState) -> TutorState:
    llm = get_llm("mini")
    llm_with_tools = llm.bind_tools(FEEDBACK_TOOLS)

    user_code = state.get("user_code", "")
    quiz = state.get("quiz")
    level = state.get("user_level") or "beginner"
    last_message = state["messages"][-1].content if state["messages"] else ""

    if not user_code and not last_message:
        return {
            **state,
            "messages": [AIMessage(content="코드를 입력해주세요! 코드 입력창에 작성하거나 채팅창에 붙여넣어 주세요.")],
            "current_agent": "feedback",
        }

    code_to_review = user_code or last_message
    quiz_context = ""
    if quiz:
        quiz_context = f"\n\n[출제된 문제]\n{quiz.get('question', '')}\n[모범 답안]\n{quiz.get('expected_answer', '')}"

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"레벨: {level}{quiz_context}\n\n[제출 코드]\n```python\n{code_to_review}\n```"),
    ]

    # ReAct 루프로 도구 활용 후 리뷰 텍스트 생성
    review_response = _react_loop(llm_with_tools, messages, llm)

    # 리뷰 내용을 구조화된 출력으로 변환
    structured_llm = llm.with_structured_output(FeedbackResult)
    result: FeedbackResult = structured_llm.invoke([
        SystemMessage(content="아래 코드 리뷰 내용을 바탕으로 구조화된 피드백을 작성하세요."),
        HumanMessage(content=f"리뷰 내용:\n{review_response.content}\n\n코드:\n{code_to_review}"),
    ])

    mistake_patterns = list(state.get("mistake_patterns", []))
    if result.mistake_pattern and result.mistake_pattern not in mistake_patterns:
        mistake_patterns.append(result.mistake_pattern)

    history = list(state.get("learning_history", []))
    history.append({
        "topic": state.get("current_topic", "코드 리뷰"),
        "action": "feedback",
        "score": result.score,
        "is_correct": result.is_correct,
    })

    retry_count = state.get("retry_count", 0)

    # 점수 60점 미만 + 첫 번째 실패 → explainer 에이전트로 재라우팅 (Multi-Agent 협업)
    if not result.is_correct and result.score < 60 and retry_count == 0:
        next_agent = "explainer"
        new_retry_count = 1
    else:
        next_agent = None
        new_retry_count = 0

    return {
        **state,
        "messages": [AIMessage(content=result.display_message)],
        "mistake_patterns": mistake_patterns,
        "learning_history": history,
        "user_code": None,
        "current_agent": "feedback",
        "next": next_agent,
        "retry_count": new_retry_count,
    }
