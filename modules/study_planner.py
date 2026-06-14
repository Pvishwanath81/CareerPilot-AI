"""
CareerPilot AI — Module 2: Smart Study Planner
Enter exams and get a personalised daily/weekly schedule.
"""

import os as _os, sys as _sys
_mod_dir = _os.path.dirname(_os.path.abspath(__file__))
_project_root = _os.path.dirname(_mod_dir)
if _project_root not in _sys.path:
    _sys.path.insert(0, _project_root)


import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta

from utils import ai_helpers, db_manager, pdf_generator
from i18n import t


def show_study_planner():
    st.markdown(f"""
    <h1 style='font-size:2.4rem;font-weight:800;'>{t("study_title")}</h1>
    <p style='font-size:1.1rem;color:#555;margin-bottom:1.5rem;'>
        {t("study_subtitle")}
    </p>
    """, unsafe_allow_html=True)

    # ── Input Form ─────────────────────────────────────────────────────────────
    with st.form("study_plan_form"):
        st.markdown(t("study_student_info"))
        student_name = st.text_input(t("study_name_label"), placeholder=t("study_name_placeholder"))

        st.markdown(t("study_subjects_heading"))
        subjects_raw = st.text_area(
            t("study_subjects_label"),
            placeholder=t("study_subjects_placeholder"),
            height=120,
        )

        st.markdown(t("study_prefs_heading"))
        col1, col2 = st.columns(2)
        with col1:
            hours_per_day = st.slider(t("study_hours_label"), 1, 12, 4)
        with col2:
            start_date = st.date_input(t("study_start_label"), value=date.today())

        st.markdown(t("study_exam_heading"))
        subjects_list = [s.strip() for s in subjects_raw.split("\n") if s.strip()]

        subject_configs = []
        if subjects_list:
            st.markdown(t("study_exam_config_hint"))
            for subj in subjects_list[:8]:  # Cap at 8
                c1, c2, c3 = st.columns([3, 2, 2])
                with c1:
                    st.markdown(f"**{subj}**")
                with c2:
                    difficulty = st.selectbox(
                        t("study_difficulty_label"),
                        [t("study_easy"), t("study_medium"), t("study_hard")],
                        key=f"diff_{subj}",
                        index=1,
                    )
                with c3:
                    exam_date = st.date_input(
                        t("study_exam_date_label"),
                        value=date.today() + timedelta(days=30),
                        key=f"exam_{subj}",
                    )
                subject_configs.append({
                    "subject": subj,
                    "difficulty": difficulty,
                    "exam_date": str(exam_date),
                })
        else:
            st.info(t("study_enter_subjects_info"))

        submitted = st.form_submit_button(t("study_generate_btn"), use_container_width=True)

    # ── Generate ───────────────────────────────────────────────────────────────
    if submitted:
        if not student_name.strip():
            st.error(t("study_name_error"))
            return
        if not subject_configs:
            st.error(t("study_subject_error"))
            return

        student_data = {
            "name": student_name,
            "subjects": subject_configs,
            "hours_per_day": hours_per_day,
            "start_date": str(start_date),
        }

        with st.spinner(t("study_generating")):
            result = ai_helpers.generate_study_plan(student_data)

        if "error" in result:
            st.error(f"{t('study_ai_failed')}{result['error']}")
            _show_api_key_hint()
            return

        result["student_name"] = student_name
        result["subjects"] = [s["subject"] for s in subject_configs]

        st.session_state["study_plan"] = result
        st.session_state["study_plan_subjects"] = subject_configs

        try:
            db_manager.save_study_plan(result)
        except Exception:
            pass

        _display_plan(result, subject_configs)

    elif st.session_state.get("study_plan"):
        st.info(t("study_last_plan_info"))
        _display_plan(
            st.session_state["study_plan"],
            st.session_state.get("study_plan_subjects", []),
        )


def _display_plan(result: dict, subject_configs: list):
    """Render the study plan."""
    st.markdown("---")
    st.markdown(f"<h2>📋 {t('study_plan_heading')}</h2>", unsafe_allow_html=True)

    priority = result.get("priority_ranking", [])
    daily = result.get("daily_schedule", [])
    weekly = result.get("weekly_plan", [])
    revision = result.get("revision_plan", [])
    tips = result.get("tips", [])

    # ── Priority Ranking ───────────────────────────────────────────────────────
    if priority:
        st.markdown(t("study_priority_heading"))
        df_priority = pd.DataFrame(priority)
        priority_color_map = {"High": "#FF3B30", "Medium": "#FF9500", "Low": "#00A651"}

        for _, row in df_priority.iterrows():
            color = priority_color_map.get(str(row.get("priority", "Medium")), "#0066FF")
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:1rem;padding:0.7rem 1rem;
                        border:2px solid #000;margin-bottom:0.5rem;background:#fff;">
                <span style="background:{color};color:#fff;font-weight:700;padding:0.2rem 0.8rem;
                             border:2px solid #000;font-size:0.85rem;">
                    {row.get('priority','?')}
                </span>
                <strong style="min-width:150px;">{row.get('subject','')}</strong>
                <span style="color:#555;font-size:0.9rem;">{row.get('reason','')}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────────────────────
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if daily:
            df_daily = pd.DataFrame(daily)
            if "hours" in df_daily.columns and "subject" in df_daily.columns and "day" in df_daily.columns:
                fig = px.bar(
                    df_daily, x="day", y="hours", color="subject",
                    title=t("study_daily_title"),
                    color_discrete_sequence=px.colors.qualitative.Bold,
                    barmode="stack",
                )
                fig.update_layout(
                    paper_bgcolor="white", font={"family": "Space Grotesk"},
                    title_font=dict(family="Space Grotesk", size=14),
                    margin=dict(t=40, b=20, l=20, r=20), height=300,
                )
                fig.update_traces(marker=dict(line=dict(color="#000000", width=1.5)))
                st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        if priority:
            subjects_list = [p.get("subject", "") for p in priority]
            priority_scores = {"High": 3, "Medium": 2, "Low": 1}
            weights = [priority_scores.get(p.get("priority", "Medium"), 2) for p in priority]
            fig_dist = px.pie(
                values=weights,
                names=subjects_list,
                title=t("study_time_dist_title"),
                color_discrete_sequence=["#0066FF", "#FF3B30", "#00A651", "#FF9500", "#9B59B6", "#E67E22"],
            )
            fig_dist.update_traces(
                textinfo="label+percent",
                marker=dict(line=dict(color="#000000", width=2)),
            )
            fig_dist.update_layout(
                paper_bgcolor="white", font={"family": "Space Grotesk"},
                title_font=dict(family="Space Grotesk", size=14),
                margin=dict(t=40, b=20, l=20, r=20), height=300,
            )
            st.plotly_chart(fig_dist, use_container_width=True)

    # ── Daily Schedule Table ───────────────────────────────────────────────────
    if daily:
        st.markdown(t("study_daily_heading"))
        df_display = pd.DataFrame(daily)
        df_display.columns = [c.replace("_", " ").title() for c in df_display.columns]
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ── Weekly Plan ────────────────────────────────────────────────────────────
    if weekly:
        st.markdown(t("study_weekly_heading"))
        for week in weekly:
            with st.expander(f"{t('study_week_label')} {week.get('week','?')} — {week.get('focus','')}"):
                subjects_str = ", ".join(week.get("subjects", []))
                st.markdown(f"**📚 {t('study_subjects_label2')}:** {subjects_str}")
                st.markdown(f"**🎯 {t('study_goals_label')}:** {week.get('goals','')}")

    # ── Revision Plan ──────────────────────────────────────────────────────────
    if revision:
        st.markdown(t("study_revision_heading"))
        df_rev = pd.DataFrame(revision)
        if not df_rev.empty:
            df_rev.columns = [c.replace("_", " ").title() for c in df_rev.columns]
            st.dataframe(df_rev, use_container_width=True, hide_index=True)

    # ── Tips ───────────────────────────────────────────────────────────────────
    if tips:
        st.markdown(t("study_tips_heading"))
        tip_cols = st.columns(min(len(tips), 3))
        for i, tip in enumerate(tips[:6]):
            with tip_cols[i % len(tip_cols)]:
                st.markdown(f"""
                <div class="brut-card" style="min-height:80px;">
                    <strong>{t('study_tip_prefix')} {i+1}</strong><br>
                    <span style="font-size:0.9rem;">{tip}</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Download ───────────────────────────────────────────────────────────────
    try:
        pdf_bytes = pdf_generator.generate_study_plan_report(result)
        st.download_button(
            label=t("study_download_btn"),
            data=pdf_bytes,
            file_name=f"study_plan_{_today()}.pdf",
            mime="application/pdf",
            key="download_study_plan_pdf",
        )
    except Exception as e:
        st.warning(f"{t('study_pdf_unavailable')}{e}")


def _show_api_key_hint():
    st.markdown(f"""
    <div class="brut-card" style="border-color:#FF9500;box-shadow:4px 4px 0px #FF9500;">
        <strong>{t("api_key_required")}</strong><br>
        {t("api_key_hint_body")}<br><br>
        {t("api_key_link")} <a href="https://aistudio.google.com/app/apikey" target="_blank">Google AI Studio</a>
    </div>
    """, unsafe_allow_html=True)


def _today():
    return date.today().strftime("%Y%m%d")
