from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from agents.state import TutorState
from agents.supervisor import supervisor_node
from agents.diagnostic import diagnostic_node
from agents.explainer import explainer_node
from agents.quiz_generator import quiz_node
from agents.feedback import feedback_node


def _supervisor_route(state: TutorState) -> str:
    return state.get("next") or "end"


def _explainer_route(state: TutorState) -> str:
    """설명 후 quiz로 자동 핸드오프하거나 종료"""
    return state.get("next") or "end"


def _feedback_route(state: TutorState) -> str:
    """점수 미달 시 explainer로 재라우팅, 그 외 종료"""
    return state.get("next") or "end"


def build_graph():
    workflow = StateGraph(TutorState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("diagnostic", diagnostic_node)
    workflow.add_node("explainer", explainer_node)
    workflow.add_node("quiz", quiz_node)
    workflow.add_node("feedback", feedback_node)

    workflow.set_entry_point("supervisor")

    # Supervisor → 전문 에이전트 라우팅
    workflow.add_conditional_edges(
        "supervisor",
        _supervisor_route,
        {
            "diagnostic": "diagnostic",
            "explainer": "explainer",
            "quiz": "quiz",
            "feedback": "feedback",
            "end": END,
        },
    )

    workflow.add_edge("diagnostic", END)

    # Explainer → Quiz (첫 설명 후 자동 문제 출제) 또는 END
    workflow.add_conditional_edges(
        "explainer",
        _explainer_route,
        {"quiz": "quiz", "end": END},
    )

    workflow.add_edge("quiz", END)

    # Feedback → Explainer (점수 60 미만 첫 실패 시 재설명) 또는 END
    workflow.add_conditional_edges(
        "feedback",
        _feedback_route,
        {"explainer": "explainer", "end": END},
    )

    # MemorySaver: LangGraph 기반 멀티턴 상태 영속화
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
