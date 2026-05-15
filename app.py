import sys
import os
import uuid
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agents.graph import get_graph
from agents.state import TutorState

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="Python AI 튜터",
    page_icon="🐍",
    layout="wide",
)

# ── 세션 상태 초기화 ─────────────────────────────────────────
def _initial_tutor_state() -> TutorState:
    return {
        "messages": [],
        "user_level": None,
        "current_topic": None,
        "learning_history": [],
        "mistake_patterns": [],
        "current_agent": None,
        "user_code": None,
        "quiz": None,
        "next": None,
        "retry_count": 0,
    }

def init_session():
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())   # LangGraph 멀티턴 식별자
    if "tutor_state" not in st.session_state:
        st.session_state.tutor_state = _initial_tutor_state()
    if "chat_display" not in st.session_state:
        st.session_state.chat_display = []

init_session()

# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.title("🐍 Python AI 튜터")
    st.divider()

    level = st.session_state.tutor_state.get("user_level")
    level_color = {"beginner": "🟢", "intermediate": "🟡", "advanced": "🔴"}.get(level, "⚪")
    level_label = {"beginner": "입문자", "intermediate": "중급자", "advanced": "고급자"}.get(level, "미파악")
    st.metric("내 레벨", f"{level_color} {level_label}")

    st.divider()

    st.subheader("📚 주제 선택")
    topics = ["변수와 자료형", "조건문/반복문", "함수", "클래스/OOP", "예외처리", "파일 입출력"]
    selected_topic = st.selectbox("학습할 주제", ["직접 입력"] + topics)

    st.divider()

    st.subheader("📈 학습 이력")
    history = st.session_state.tutor_state.get("learning_history", [])
    if history:
        for item in history[-5:]:
            icon = {"explained": "📖", "feedback": "✅" if item.get("is_correct") else "❌"}.get(item.get("action"), "•")
            st.write(f"{icon} {item.get('topic', '')}")
    else:
        st.caption("아직 학습 이력이 없습니다.")

    st.divider()

    mistakes = st.session_state.tutor_state.get("mistake_patterns", [])
    if mistakes:
        st.subheader("⚠️ 주의할 패턴")
        for m in mistakes[-3:]:
            st.warning(m, icon="⚠️")

    st.divider()

    if st.button("🔄 학습 초기화", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())   # 새 thread → 체크포인터 리셋
        st.session_state.tutor_state = _initial_tutor_state()
        st.session_state.chat_display = []
        st.rerun()

# ── 메인 영역 ────────────────────────────────────────────────
st.title("Python 학습 튜터 💬")

col_chat, col_code = st.columns([3, 2])

with col_chat:
    st.subheader("대화")

    chat_container = st.container(height=480)
    with chat_container:
        if not st.session_state.chat_display:
            st.info("안녕하세요! Python을 함께 공부해봐요. 먼저 본인의 Python 수준을 알려주세요 😊")
        else:
            for role, content in st.session_state.chat_display:
                with st.chat_message(role):
                    st.markdown(content)

    placeholder = f"{selected_topic}에 대해 알려줘" if selected_topic != "직접 입력" else "질문하거나 '문제 내줘'라고 말해보세요!"
    user_input = st.chat_input(placeholder)

with col_code:
    st.subheader("코드 제출")

    current_quiz = st.session_state.tutor_state.get("quiz")
    if current_quiz:
        with st.expander("📝 현재 문제", expanded=True):
            st.markdown(f"**주제:** {current_quiz.get('topic', '')}")
            st.markdown(current_quiz.get("question", ""))
            if st.button("💡 힌트 보기"):
                st.info(current_quiz.get("hint", ""))

    code_input = st.text_area(
        "코드를 여기에 작성하세요",
        height=260,
        placeholder="# 여기에 Python 코드를 작성하세요\n\ndef solution():\n    pass",
        key="code_editor",
    )

    submit_code = st.button("✅ 코드 제출 및 피드백 받기", use_container_width=True, type="primary")


# ── 메시지 처리 ───────────────────────────────────────────────
def run_tutor(user_message: str, user_code: str = None):
    graph = get_graph()
    # LangGraph Checkpointer용 thread_id — 멀티턴 상태 자동 복원
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    is_first = len(st.session_state.chat_display) == 0

    if is_first:
        # 첫 메시지: 전체 초기 상태를 함께 전달
        inputs = {
            **_initial_tutor_state(),
            "messages": [HumanMessage(content=user_message)],
        }
    else:
        # 이후 메시지: 새 메시지만 전달 (나머지는 checkpointer가 복원)
        inputs = {"messages": [HumanMessage(content=user_message)]}

    if user_code:
        inputs["user_code"] = user_code
    if selected_topic != "직접 입력":
        inputs["current_topic"] = selected_topic

    with st.spinner("튜터가 생각 중..."):
        result = graph.invoke(inputs, config=config)

    st.session_state.tutor_state = result

    # 마지막 HumanMessage 이후의 AI 메시지를 모두 수집 (Multi-Agent 연속 응답 지원)
    messages = result.get("messages", [])
    last_human_idx = max(
        (i for i, m in enumerate(messages) if isinstance(m, HumanMessage)),
        default=-1,
    )
    new_ai_msgs = [m for m in messages[last_human_idx + 1:] if isinstance(m, AIMessage)]

    if new_ai_msgs:
        st.session_state.chat_display.append(("user", user_message))
        for ai_msg in new_ai_msgs:
            st.session_state.chat_display.append(("assistant", ai_msg.content))

    st.rerun()


if user_input:
    run_tutor(user_input)

if submit_code:
    if code_input.strip():
        run_tutor("제출한 코드를 검토해주세요.", user_code=code_input)
    else:
        st.warning("코드를 입력해주세요!")
