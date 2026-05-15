from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from typing import Literal
from agents.state import TutorState
from utils.llm import get_llm


class RouteDecision(BaseModel):
    destination: Literal["diagnostic", "explainer", "quiz", "feedback", "end"] = Field(
        description="라우팅할 에이전트"
    )
    topic: str = Field(description="감지된 학습 주제 (없으면 빈 문자열)")
    reasoning: str = Field(description="라우팅 이유")


SYSTEM_PROMPT = """당신은 Python 학습 튜터의 슈퍼바이저입니다.
사용자 메시지를 분석하여 아래 에이전트 중 하나로 라우팅하세요.

에이전트 종류:
- diagnostic: 사용자 레벨 파악 요청, 처음 오는 사용자, 수준 테스트 요청
- explainer: 개념 설명, "~이 뭐야?", "~를 알려줘", "~를 이해 못하겠어" 등
- quiz: 문제 요청, "문제 풀고 싶어", "연습하고 싶어", "퀴즈 내줘" 등
- feedback: 코드를 보내며 검토/피드백 요청, 코드 오류 질문
- end: 종료 인사, 감사 인사

사용자 레벨이 None이면 diagnostic으로 먼저 보내세요."""


def supervisor_node(state: TutorState) -> TutorState:
    llm = get_llm("mini")
    structured_llm = llm.with_structured_output(RouteDecision)

    last_message = state["messages"][-1].content if state["messages"] else ""
    level_info = f"현재 레벨: {state.get('user_level') or '미파악'}"

    response: RouteDecision = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"{level_info}\n\n사용자 메시지: {last_message}"),
    ])

    return {
        **state,
        "next": response.destination,
        "current_topic": response.topic or state.get("current_topic"),
        "current_agent": "supervisor",
    }
