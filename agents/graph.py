from langgraph.graph import StateGraph, END
from agents.state import TutorState
from agents.supervisor import supervisor_node
from agents.diagnostic import diagnostic_node
from agents.explainer import explainer_node
from agents.quiz_generator import quiz_node
from agents.feedback import feedback_node


def _route(state: TutorState) -> str:
    return state.get("next", "end")


def build_graph():
    workflow = StateGraph(TutorState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("diagnostic", diagnostic_node)
    workflow.add_node("explainer", explainer_node)
    workflow.add_node("quiz", quiz_node)
    workflow.add_node("feedback", feedback_node)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        _route,
        {
            "diagnostic": "diagnostic",
            "explainer": "explainer",
            "quiz": "quiz",
            "feedback": "feedback",
            "end": END,
        },
    )

    workflow.add_edge("diagnostic", END)
    workflow.add_edge("explainer", END)
    workflow.add_edge("quiz", END)
    workflow.add_edge("feedback", END)

    return workflow.compile()


# 싱글턴 그래프 인스턴스
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
