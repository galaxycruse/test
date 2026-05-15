from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from typing import Optional
from agents.state import TutorState
from utils.llm import get_llm
from rag.retriever import retrieve_as_text


class QuizQuestion(BaseModel):
    question: str = Field(description="문제 내용 (코드 포함 가능)")
    expected_answer: str = Field(description="모범 답안 코드 또는 설명")
    hint: str = Field(description="힌트 (바로 답은 아니지만 방향 제시)")
    difficulty: str = Field(description="beginner/intermediate/advanced")
    topic: str = Field(description="문제가 다루는 주제")
    display_message: str = Field(description="사용자에게 보여줄 문제 메시지 (마크다운)")


SYSTEM_PROMPT = """당신은 Python 학습 문제 출제 전문가입니다.
사용자 레벨과 주제에 맞는 코딩 문제를 출제하세요.

문제 유형 (레벨별):
- beginner: 변수/자료형 조작, 간단한 조건문/반복문, 문자열 처리
- intermediate: 함수 작성, 클래스 구현, 파일 처리, 예외 처리
- advanced: 데코레이터 구현, 제너레이터, 컨텍스트 매니저, 메타프로그래밍

문제 형식:
- 실제로 실행 가능한 코드 작성 문제
- 명확한 입출력 예시 포함
- 자연스러운 실무 시나리오 반영

참고 자료:
{context}"""


def quiz_node(state: TutorState) -> TutorState:
    llm = get_llm("mini")
    structured_llm = llm.with_structured_output(QuizQuestion)

    level = state.get("user_level") or "beginner"
    topic = state.get("current_topic") or "Python 기초"
    last_message = state["messages"][-1].content if state["messages"] else ""

    mistake_patterns = state.get("mistake_patterns", [])
    mistake_info = ""
    if mistake_patterns:
        mistake_info = f"\n사용자가 자주 틀리는 패턴: {', '.join(mistake_patterns)}"

    context = retrieve_as_text(f"Python {topic} 문제 예시", k=3)
    prompt = SYSTEM_PROMPT.format(context=context)

    quiz: QuizQuestion = structured_llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"레벨: {level}\n주제: {topic}{mistake_info}\n요청: {last_message}"),
    ])

    return {
        **state,
        "messages": [AIMessage(content=quiz.display_message)],
        "quiz": {
            "question": quiz.question,
            "expected_answer": quiz.expected_answer,
            "hint": quiz.hint,
            "topic": quiz.topic,
        },
        "current_agent": "quiz",
    }
