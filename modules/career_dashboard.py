"""
CareerPilot AI — Module 3: Career Readiness Dashboard
Displays aggregated metrics, charts, and history from session state and DB.
"""

import os as _os, sys as _sys
_mod_dir = _os.path.dirname(_os.path.abspath(__file__))
_project_root = _os.path.dirname(_mod_dir)
if _project_root not in _sys.path:
    _sys.path.insert(0, _project_root)


import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

from utils import db_manager
from i18n import t


def show_career_dashboard():
    st.markdown(f"""
    <h1 style='font-size:2.4rem;font-weight:800;'>{t("dash_title")}</h1>
    <p style='font-size:1.1rem;color:#555;margin-bottom:1.5rem;'>
        {t("dash_subtitle")}
    </p>
    """, unsafe_allow_html=True)

    # ── Load data ──────────────────────────────────────────────────────────────
    resume_score = st.session_state.get("resume_score", 0)
    ats_score = st.session_state.get("ats_score", 0)
    skills_found = st.session_state.get("skills_found", [])
    skills_missing = st.session_state.get("skills_missing", [])
    study_plan = st.session_state.get("study_plan", None)

    # Try loading from DB if session is empty
    if resume_score == 0:
        latest = db_manager.get_latest_analysis()
        if latest:
            resume_score = latest.get("resume_score", 0)
            ats_score = latest.get("ats_score", 0)
            skills_found = latest.get("skills_found", [])
            skills_missing = latest.get("missing_skills", [])

    # ── Empty state ────────────────────────────────────────────────────────────
    if resume_score == 0:
        _empty_state()
        return

    # ── Readiness Formula ──────────────────────────────────────────────────────
    total_skills = len(skills_found) + len(skills_missing)
    skill_coverage = (len(skills_found) / total_skills * 100) if total_skills > 0 else 0
    readiness = (resume_score * 0.4) + (ats_score * 0.3) + (skill_coverage * 0.3)
    readiness = round(min(readiness, 100), 1)

    # ── Metric Cards Row ───────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    _metric_card(c1, str(resume_score), t("dash_resume_score"), "#0066FF")
    _metric_card(c2, str(ats_score), t("dash_ats_score"), "#0066FF")
    _metric_card(c3, str(len(skills_found)), t("dash_skills_found"), "#00A651")
    readiness_color = "#00A651" if readiness >= 70 else ("#FF9500" if readiness >= 40 else "#FF3B30")
    _metric_card(c4, f"{readiness}%", t("dash_readiness"), readiness_color)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Readiness Gauge ────────────────────────────────────────────────────────
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=readiness,
            delta={"reference": 70, "valueformat": ".1f"},
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": t("dash_gauge_title"), "font": {"family": "Space Grotesk", "size": 15}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#000"},
                "bar": {"color": readiness_color, "thickness": 0.3},
                "steps": [
                    {"range": [0, 40], "color": "#FFE0DE"},
                    {"range": [40, 70], "color": "#FFF3DE"},
                    {"range": [70, 100], "color": "#DEFFEE"},
                ],
                "threshold": {
                    "line": {"color": "#000000", "width": 3},
                    "thickness": 0.75,
                    "value": 70,
                },
                "bordercolor": "#000000",
                "borderwidth": 2,
            },
            number={"suffix": "%", "font": {"family": "Space Grotesk", "size": 36, "color": readiness_color}},
        ))
        fig_gauge.update_layout(
            paper_bgcolor="white", font={"family": "Space Grotesk"},
            margin=dict(t=50, b=20, l=20, r=20), height=300,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Readiness label
        if readiness >= 70:
            st.success(t("dash_job_ready"))
        elif readiness >= 40:
            st.warning(t("dash_getting_there"))
        else:
            st.error(t("dash_needs_work"))

    with chart_col2:
        # Skills donut chart
        if total_skills > 0:
            fig_donut = go.Figure(go.Pie(
                labels=[t("dash_skills_found_label"), t("dash_skills_missing_label")],
                values=[len(skills_found), len(skills_missing)],
                hole=0.5,
                marker=dict(
                    colors=["#0066FF", "#FF3B30"],
                    line=dict(color="#000000", width=2),
                ),
                textinfo="label+percent",
                textfont=dict(family="Space Grotesk", size=12),
            ))
            fig_donut.update_layout(
                title=dict(text=t("dash_donut_title"), font=dict(family="Space Grotesk", size=15)),
                paper_bgcolor="white", font={"family": "Space Grotesk"},
                margin=dict(t=50, b=20, l=20, r=20), height=300,
                annotations=[dict(
                    text=f"<b>{len(skills_found)}<br>{t('dash_skills_center')}</b>",
                    x=0.5, y=0.5, font_size=16, showarrow=False,
                    font=dict(family="Space Grotesk", color="#0066FF"),
                )],
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.markdown(f"""
            <div class="brut-card" style="text-align:center;padding:2rem;">
                <p style="color:#999;">{t("dash_no_skill_data")}</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Score Breakdown Bar ────────────────────────────────────────────────────
    st.markdown(t("dash_bar_title"))
    fig_bar = go.Figure()
    categories = [t("dash_bar_resume"), t("dash_bar_ats"), t("dash_bar_skill"), t("dash_bar_readiness")]
    values = [resume_score, ats_score, round(skill_coverage, 1), readiness]
    colors = ["#0066FF", "#0055DD", "#0044BB", "#FF9500"]
    fig_bar.add_trace(go.Bar(
        x=categories, y=values,
        marker=dict(color=colors, line=dict(color="#000000", width=2)),
        text=[f"{v}%" for v in values],
        textposition="outside",
        textfont=dict(family="Space Grotesk", size=12, color="#000000"),
    ))
    fig_bar.add_hline(y=70, line_dash="dash", line_color="#00A651", line_width=2,
                      annotation_text=t("dash_bar_target"), annotation_position="right")
    fig_bar.update_layout(
        paper_bgcolor="white", font={"family": "Space Grotesk"},
        yaxis=dict(range=[0, 110], title=t("dash_bar_y_label")),
        xaxis=dict(title=""),
        margin=dict(t=20, b=20, l=20, r=20), height=300,
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── History Table ──────────────────────────────────────────────────────────
    st.markdown(t("dash_history_heading"))
    try:
        history = db_manager.get_all_resume_analyses()[:5]
        if history:
            df_hist = pd.DataFrame([{
                t("dash_history_date"): h["date"][:10] if h.get("date") else "N/A",
                t("dash_history_resume"): h.get("resume_score", 0),
                t("dash_history_ats"): h.get("ats_score", 0),
                t("dash_history_exp"): h.get("experience_level", "N/A"),
                t("dash_history_skills"): len(h.get("skills_found", [])),
            } for h in history])
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info(t("dash_history_empty"))
    except Exception:
        st.info(t("dash_history_unavailable"))

    # ── Upcoming Exams ─────────────────────────────────────────────────────────
    if study_plan:
        st.markdown(t("dash_study_overview"))
        priority = study_plan.get("priority_ranking", [])
        if priority:
            df_priority = pd.DataFrame(priority)
            df_priority.columns = [c.replace("_", " ").title() for c in df_priority.columns]
            st.dataframe(df_priority, use_container_width=True, hide_index=True)

    # ── Skills Display ─────────────────────────────────────────────────────────
    if skills_found:
        st.markdown(t("dash_your_skills"))
        chips_html = "".join(f'<span class="skill-chip">{s}</span>' for s in skills_found)
        st.markdown(f'<div style="line-height:2.4;">{chips_html}</div>', unsafe_allow_html=True)

    if skills_missing:
        st.markdown(t("dash_skills_to_acquire"))
        chips_html = "".join(f'<span class="skill-chip-missing">{s}</span>' for s in skills_missing)
        st.markdown(f'<div style="line-height:2.4;">{chips_html}</div>', unsafe_allow_html=True)


def _metric_card(col, value: str, label: str, color: str):
    with col:
        st.markdown(f"""
        <div class="metric-card" style="border-color:{color};box-shadow:4px 4px 0px {color};">
            <div class="metric-value" style="color:{color};">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)


def _empty_state():
    st.markdown(f"""
    <div class="brut-card" style="text-align:center;padding:3rem;box-shadow:8px 8px 0px #0066FF;border-color:#0066FF;">
        <div style="font-size:4rem;">📊</div>
        <h2 style="font-size:1.8rem;font-weight:800;">{t("dash_no_data_title")}</h2>
        <p style="color:#555;font-size:1.1rem;">
            {t("dash_no_data_body")}
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(t("dash_go_analyse"), key="dash_to_resume"):
        st.session_state["nav_page"] = "📄 Resume Analyzer"
        st.rerun()
