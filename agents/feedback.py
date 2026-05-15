from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing import List, Optional
from agents.state import TutorState
from utils.llm import get_llm


class FeedbackResult(BaseModel):
    is_correct: bool = Field(description="코드가 문제를 올바르게 풀었는지 여부")
    score: int = Field(description="0~100점 점수")
    good_points: List[str] = Field(description="잘한 점 목록")
    improvements: List[str] = Field(description="개선할 점 목록")
    mistake_pattern: Optional[str] = Field(None, description="반복될 수 있는 실수 패턴 (없으면 None)")
    corrected_code: Optional[str] = Field(None, description="개선된 코드 (필요한 경우)")
    display_message: str = Field(description="사용자에게 보여줄 피드백 메시지 (마크다운)")


SYSTEM_PROMPT = """당신은 친절하고 꼼꼼한 Python 코드 리뷰어입니다.
사용자가 제출한 코드를 분석하고 건설적인 피드백을 주세요.

피드백 원칙:
1. 먼저 잘한 점을 칭찬 (긍정적 강화)
2. 개선점은 "왜 이게 문제인지" 설명과 함께 제시
3. 코드 스타일, 효율성, 정확성 모두 검토
4. 레벨에 맞는 수준으로 피드백 (beginner에게 고급 최적화 요구 X)
5. 틀렸더라도 격려하며 힌트 제공

퀴즈 문제가 주어진 경우 모범 답안과 비교하여 채점하세요."""


def feedback_node(state: TutorState) -> TutorState:
    llm = get_llm("mini")
    structured_llm = llm.with_structured_output(FeedbackResult)

    user_code = state.get("user_code", "")
    quiz = state.get("quiz")
    level = state.get("user_level") or "beginner"
    last_message = state["messages"][-1].content if state["messages"] else ""

    if not user_code and not last_message:
        return {
            **state,
            "messages": [AIMessage(content="코드를 입력해주세요! 코드 입력창에 작성하거나, 채팅창에 코드를 붙여넣어 주세요.")],
            "current_agent": "feedback",
        }

    code_to_review = user_code or last_message
    quiz_context = ""
    if quiz:
        quiz_context = f"\n\n[출제된 문제]\n{quiz.get('question', '')}\n\n[모범 답안]\n{quiz.get('expected_answer', '')}"

    result: FeedbackResult = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"레벨: {level}{quiz_context}\n\n[제출된 코드]\n```python\n{code_to_review}\n```"),
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

    return {
        **state,
        "messages": [AIMessage(content=result.display_message)],
        "mistake_patterns": mistake_patterns,
        "learning_history": history,
        "user_code": None,
        "current_agent": "feedback",
    }
