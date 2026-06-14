"""
CareerPilot AI — Module 5: AI Interview Coach
Practice with AI-generated questions, get evaluated answers, session summary.
"""

import os as _os, sys as _sys
_mod_dir = _os.path.dirname(_os.path.abspath(__file__))
_project_root = _os.path.dirname(_mod_dir)
if _project_root not in _sys.path:
    _sys.path.insert(0, _project_root)


import streamlit as st
from datetime import date

from utils import ai_helpers, db_manager, pdf_generator
from i18n import t

ROLES = [
    "Software Engineer",
    "Data Analyst",
    "Frontend Developer",
    "Backend Developer",
    "AI/ML Engineer",
    "Full Stack Developer",
    "Cloud Engineer",
    "DevOps Engineer",
    "Data Scientist",
    "Cybersecurity Analyst",
]

DIFFICULTIES = ["Entry Level", "Mid Level", "Senior Level"]
QUESTION_TYPES = ["Technical", "HR & Behavioral", "Mixed"]


def show_interview_coach():
    st.markdown(f"""
    <h1 style='font-size:2.4rem;font-weight:800;'>{t("interview_title")}</h1>
    <p style='font-size:1.1rem;color:#555;margin-bottom:1.5rem;'>
        {t("interview_subtitle")}
    </p>
    """, unsafe_allow_html=True)

    # ── Initialise session state ───────────────────────────────────────────────
    if "interview_session" not in st.session_state:
        st.session_state["interview_session"] = []
    if "interview_questions" not in st.session_state:
        st.session_state["interview_questions"] = []
    if "interview_current_q" not in st.session_state:
        st.session_state["interview_current_q"] = 0
    if "interview_active" not in st.session_state:
        st.session_state["interview_active"] = False
    if "interview_role" not in st.session_state:
        st.session_state["interview_role"] = ROLES[0]
    if "interview_done" not in st.session_state:
        st.session_state["interview_done"] = False
    if "current_eval" not in st.session_state:
        st.session_state["current_eval"] = None

    active = st.session_state["interview_active"]
    done = st.session_state["interview_done"]

    # ── Setup screen ───────────────────────────────────────────────────────────
    if not active and not done:
        _show_setup()

    # ── Active session ─────────────────────────────────────────────────────────
    elif active and not done:
        _show_active_session()

    # ── Session summary ────────────────────────────────────────────────────────
    elif done:
        _show_summary()


def _show_setup():
    """Render the session setup form."""
    st.markdown(t("interview_configure"))

    col1, col2, col3 = st.columns(3)
    with col1:
        role = st.selectbox(t("interview_target_role"), ROLES, key="setup_role")
    with col2:
        difficulty = st.selectbox(t("interview_difficulty"), DIFFICULTIES, key="setup_difficulty")
    with col3:
        q_type = st.selectbox(t("interview_q_type"), QUESTION_TYPES, key="setup_qtype")

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="brut-card" style="text-align:center;">
            <div style="font-size:2rem;">❓</div>
            <strong>{t("interview_feat_10q")}</strong><br>
            <span style="font-size:0.85rem;color:#555;">{t("interview_feat_10q_desc")}</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="brut-card" style="text-align:center;">
            <div style="font-size:2rem;">🤖</div>
            <strong>{t("interview_feat_ai")}</strong><br>
            <span style="font-size:0.85rem;color:#555;">{t("interview_feat_ai_desc")}</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="brut-card" style="text-align:center;">
            <div style="font-size:2rem;">📊</div>
            <strong>{t("interview_feat_report")}</strong><br>
            <span style="font-size:0.85rem;color:#555;">{t("interview_feat_report_desc")}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(t("interview_start_btn"), key="btn_start_interview"):
        with st.spinner(t("interview_preparing").format(qtype=q_type, role=role, difficulty=difficulty)):
            result = ai_helpers.generate_interview_questions(role, difficulty, q_type)

        if "error" in result:
            st.error(f"{t('interview_load_failed')}{result['error']}")
            _show_api_key_hint()
            return

        questions = result.get("questions", [])
        if not questions:
            st.error(t("interview_no_questions"))
            return

        st.session_state["interview_questions"] = questions
        st.session_state["interview_current_q"] = 0
        st.session_state["interview_session"] = []
        st.session_state["interview_active"] = True
        st.session_state["interview_done"] = False
        st.session_state["interview_role"] = role
        st.session_state["interview_difficulty"] = difficulty
        st.session_state["current_eval"] = None
        st.rerun()


def _show_active_session():
    """Render the active Q&A interface."""
    questions = st.session_state["interview_questions"]
    current_idx = st.session_state["interview_current_q"]
    role = st.session_state["interview_role"]

    if current_idx >= len(questions):
        st.session_state["interview_done"] = True
        st.session_state["interview_active"] = False
        st.rerun()
        return

    question = questions[current_idx]
    total = len(questions)
    progress = current_idx / total

    # ── Progress bar ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
        <strong>{t("interview_question_label").format(n=current_idx + 1, total=total)}</strong>
        <span style="font-weight:700;color:#0066FF;">{int(progress * 100)}{t("interview_pct_complete")}</span>
    </div>
    <div style="background:#E0E0E0;border:2px solid #000;height:18px;margin-bottom:1.5rem;">
        <div style="background:#0066FF;height:100%;width:{int(progress * 100)}%;transition:width 0.3s;"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Question Card ──────────────────────────────────────────────────────────
    q_type_tag = question.get("type", "General")
    st.markdown(f"""
    <div class="question-card">
        <div style="display:flex;gap:0.5rem;margin-bottom:0.8rem;">
            <span class="tag tag-blue">Q{current_idx + 1}</span>
            <span class="tag tag-orange">{q_type_tag}</span>
        </div>
        <div style="font-size:1.25rem;font-weight:700;line-height:1.5;color:#fff;">
            {question.get('question', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Previous evaluation (if any) ───────────────────────────────────────────
    eval_result = st.session_state.get("current_eval")
    if eval_result and "score" in eval_result:
        _display_evaluation(eval_result)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(t("interview_next_btn"), key="btn_next_q"):
            st.session_state["current_eval"] = None
            st.session_state["interview_current_q"] += 1
            if st.session_state["interview_current_q"] >= total:
                _finalise_session()
            st.rerun()

    else:
        # ── Answer input ───────────────────────────────────────────────────────
        user_answer = st.text_area(
            t("interview_answer_label"),
            placeholder=t("interview_answer_placeholder"),
            height=150,
            key=f"answer_{current_idx}",
        )

        btn_col1, btn_col2 = st.columns([1, 4])
        with btn_col1:
            submit = st.button(t("interview_submit_btn"), key="btn_submit_answer")
        with btn_col2:
            skip = st.button(t("interview_skip_btn"), key="btn_skip_q")

        if submit:
            if not user_answer.strip():
                st.warning(t("interview_write_answer"))
                return
            with st.spinner(t("interview_evaluating")):
                eval_result = ai_helpers.evaluate_answer(
                    question.get("question", ""),
                    user_answer,
                    role,
                )

            if "error" in eval_result:
                st.error(f"{t('interview_eval_failed')}{eval_result['error']}")
                return

            # Store answer + evaluation
            qa_record = {
                "question": question.get("question", ""),
                "type": question.get("type", ""),
                "user_answer": user_answer,
                **eval_result,
            }
            st.session_state["interview_session"].append(qa_record)
            st.session_state["current_eval"] = eval_result
            st.rerun()

        if skip:
            qa_record = {
                "question": question.get("question", ""),
                "type": question.get("type", ""),
                "user_answer": "[Skipped]",
                "score": 0,
                "feedback": "Question was skipped.",
                "model_answer": "",
                "key_points_missed": [],
                "confidence_level": "Low",
            }
            st.session_state["interview_session"].append(qa_record)
            st.session_state["current_eval"] = None
            st.session_state["interview_current_q"] += 1
            if st.session_state["interview_current_q"] >= total:
                _finalise_session()
            st.rerun()

    # ── Quit button ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(t("interview_end_early"), key="btn_end_early"):
        _finalise_session()
        st.rerun()


def _display_evaluation(eval_result: dict):
    """Display evaluation result for one answer."""
    score = eval_result.get("score", 0)
    feedback = eval_result.get("feedback", "")
    model_answer = eval_result.get("model_answer", "")
    key_points_missed = eval_result.get("key_points_missed", [])
    confidence = eval_result.get("confidence_level", "Medium")

    score_color = "#00A651" if score >= 7 else ("#FF9500" if score >= 5 else "#FF3B30")
    confidence_color = {"High": "#00A651", "Medium": "#FF9500", "Low": "#FF3B30"}.get(confidence, "#FF9500")

    st.markdown(f"""
    <div class="eval-card">
        <div style="display:flex;gap:1rem;align-items:center;margin-bottom:1rem;flex-wrap:wrap;">
            <div class="score-badge" style="background:{score_color};font-size:1.5rem;padding:0.4rem 1.2rem;">
                {score}/10
            </div>
            <span style="font-weight:700;font-size:1.1rem;">{t("interview_score_label")}</span>
            <span style="background:{confidence_color};color:#fff;padding:0.2rem 0.7rem;
                         font-weight:700;border:2px solid #000;font-size:0.85rem;">
                {t("interview_confidence")}{confidence}
            </span>
        </div>
        <div style="margin-bottom:0.8rem;">
            <strong>{t("interview_feedback_label")}</strong><br>
            <span style="font-size:0.95rem;">{feedback}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if model_answer:
        with st.expander(t("interview_model_answer")):
            st.markdown(model_answer)

    if key_points_missed:
        st.markdown(t("interview_key_missed"))
        for point in key_points_missed:
            st.markdown(f"• {point}")


def _finalise_session():
    """Calculate final scores and mark session as done."""
    session_data = st.session_state.get("interview_session", [])
    total_score = sum(qa.get("score", 0) for qa in session_data)
    max_score = len(session_data) * 10
    pct = int((total_score / max_score) * 100) if max_score > 0 else 0

    if pct >= 80:
        grade = "A"
    elif pct >= 70:
        grade = "B"
    elif pct >= 60:
        grade = "C"
    elif pct >= 50:
        grade = "D"
    else:
        grade = "F"

    st.session_state["interview_final_score"] = total_score
    st.session_state["interview_max_score"] = max_score
    st.session_state["interview_grade"] = grade
    st.session_state["interview_done"] = True
    st.session_state["interview_active"] = False

    # Save to DB
    try:
        db_manager.save_interview_session({
            "role": st.session_state.get("interview_role", ""),
            "difficulty": st.session_state.get("interview_difficulty", ""),
            "total_score": total_score,
            "max_score": max_score,
            "grade": grade,
            "questions_data": session_data,
        })
    except Exception:
        pass


def _show_summary():
    """Show the final session summary."""
    session_data = st.session_state.get("interview_session", [])
    total_score = st.session_state.get("interview_final_score", 0)
    max_score = st.session_state.get("interview_max_score", 0)
    grade = st.session_state.get("interview_grade", "N/A")
    role = st.session_state.get("interview_role", "")

    pct = int((total_score / max_score) * 100) if max_score > 0 else 0
    badge_color = "#00A651" if pct >= 70 else ("#FF9500" if pct >= 50 else "#FF3B30")

    st.markdown(f"""
    <div style="background:#000;color:#fff;padding:2rem;border:3px solid #000;
                box-shadow:8px 8px 0px #0066FF;margin-bottom:1.5rem;text-align:center;">
        <div style="font-size:1rem;color:#0066FF;font-weight:700;text-transform:uppercase;">
            {t("interview_session_complete")}
        </div>
        <div style="font-size:2.5rem;font-weight:800;margin-top:0.5rem;">{role}</div>
        <div style="display:flex;justify-content:center;gap:1.5rem;margin-top:1rem;flex-wrap:wrap;">
            <div class="score-badge" style="background:{badge_color};">
                {total_score}/{max_score}
            </div>
            <div class="score-badge" style="background:{badge_color};">
                {pct}%
            </div>
            <div class="score-badge" style="background:#0066FF;">
                {t("interview_grade_label")}{grade}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if pct >= 80:
        st.success(t("interview_excellent"))
    elif pct >= 60:
        st.warning(t("interview_good"))
    else:
        st.error(t("interview_needs_improvement"))

    # Per-question breakdown
    if session_data:
        st.markdown(t("interview_breakdown"))
        for i, qa in enumerate(session_data, 1):
            score = qa.get("score", 0)
            sc = "#00A651" if score >= 7 else ("#FF9500" if score >= 5 else "#FF3B30")
            with st.expander(f"Q{i}: {qa.get('question', '')[:70]}..."):
                st.markdown(f"""
                <div style="margin-bottom:0.5rem;">
                    <span class="score-badge" style="background:{sc};font-size:1.2rem;
                          padding:0.3rem 1rem;">{score}/10</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"{t('interview_your_answer')}{qa.get('user_answer', 'N/A')}")
                st.markdown(f"{t('interview_feedback_key')}{qa.get('feedback', '')}")
                if qa.get("model_answer"):
                    st.markdown(f"{t('interview_model_ans_key')}{qa.get('model_answer', '')}")
                missed = qa.get("key_points_missed", [])
                if missed:
                    st.markdown(t("interview_key_missed_key"))
                    for p in missed:
                        st.markdown(f"• {p}")

    st.markdown("<br>", unsafe_allow_html=True)

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button(t("interview_new_session"), key="btn_new_session"):
            for key in ["interview_session", "interview_questions", "interview_current_q",
                        "interview_active", "interview_done", "current_eval"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    with btn_col2:
        try:
            session_for_pdf = {
                "role": role,
                "difficulty": st.session_state.get("interview_difficulty", ""),
                "total_score": total_score,
                "max_score": max_score,
                "grade": grade,
                "questions_data": session_data,
            }
            pdf_bytes = pdf_generator.generate_interview_report(session_for_pdf)
            st.download_button(
                label=t("interview_download_btn"),
                data=pdf_bytes,
                file_name=f"interview_report_{date.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                key="download_interview_pdf",
            )
        except Exception as e:
            st.warning(f"{t('interview_pdf_unavailable')}{e}")


def _show_api_key_hint():
    st.markdown(f"""
    <div class="brut-card" style="border-color:#FF9500;box-shadow:4px 4px 0px #FF9500;">
        <strong>{t("api_key_required")}</strong><br>
        {t("api_key_hint_body")}<br><br>
        {t("api_key_link")} <a href="https://aistudio.google.com/app/apikey" target="_blank">Google AI Studio</a>
    </div>
    """, unsafe_allow_html=True)
