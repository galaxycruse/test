from typing import TypedDict, List, Optional, Literal, Annotated
from langchain_core.messages import BaseMessage
import operator


class TutorState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_level: Optional[Literal["beginner", "intermediate", "advanced"]]
    current_topic: Optional[str]
    learning_history: List[dict]      # [{"topic": ..., "action": ..., "score": ...}]
    mistake_patterns: List[str]       # 자주 틀리는 패턴
    current_agent: Optional[str]
    user_code: Optional[str]
    quiz: Optional[dict]
    next: Optional[str]
    retry_count: int                  # 피드백 실패 후 재시도 횟수 (무한 루프 방지)
