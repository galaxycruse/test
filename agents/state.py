from typing import TypedDict, List, Optional, Literal, Annotated
from langchain_core.messages import BaseMessage
import operator


class TutorState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_level: Optional[Literal["beginner", "intermediate", "advanced"]]
    current_topic: Optional[str]
    learning_history: List[dict]      # [{"topic": ..., "understood": bool}]
    mistake_patterns: List[str]       # 자주 틀리는 패턴 목록
    current_agent: Optional[str]
    user_code: Optional[str]          # 사용자가 제출한 코드
    quiz: Optional[dict]              # {"question": ..., "answer": ..., "hint": ...}
    next: Optional[str]               # 다음 라우팅 대상
