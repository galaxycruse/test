from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Literal, Optional
from agents.state import TutorState
from utils.llm import get_llm


class DiagnosticResult(BaseModel):
    level: Optional[Literal["beginner", "intermediate", "advanced"]] = Field(
        None, description="판별된 레벨. 아직 판단 불가면 None"
    )
    response: str = Field(description="사용자에게 보낼 응답 메시지")
    need_more_info: bool = Field(
        description="레벨 판단을 위해 추가 질문이 필요한지 여부"
    )


SYSTEM_PROMPT = """당신은 Python 학습 튜터입니다. 사용자의 Python 수준을 파악하세요.

레벨 기준:
- beginner: 변수, 자료형, 조건문/반복문 기초 단계
- intermediate: 함수, 클래스, 파일 입출력, 예외처리 가능
- advanced: 데코레이터, 제너레이터, 비동기, 메타클래스 등 고급 개념

진단 방법:
1. 사용자가 자신의 수준을 말하면 그에 맞게 판단
2. 불명확하면 1~2개의 간단한 질문으로 확인
3. 친근하고 격려적인 톤을 유지

레벨이 확정되면 "beginner/intermediate/advanced 레벨이시군요! 앞으로 함께 열심히 공부해봐요!" 형식으로 응답."""


def diagnostic_node(state: TutorState) -> TutorState:
    llm = get_llm("mini")
    structured_llm = llm.with_structured_output(DiagnosticResult)

    last_message = state["messages"][-1].content if state["messages"] else "안녕하세요"

    result: DiagnosticResult = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=last_message),
    ])

    new_level = result.level if result.level else state.get("user_level")

    return {
        **state,
        "messages": [AIMessage(content=result.response)],
        "user_level": new_level,
        "current_agent": "diagnostic",
    }
