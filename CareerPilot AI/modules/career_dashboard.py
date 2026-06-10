"""
CareerPilot AI — Module 3: Career Readiness Dashboard
Displays aggregated metrics, charts, and history from session state and DB.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

from utils import db_manager


def show_career_dashboard():
    st.markdown("""
    <h1 style='font-size:2.4rem;font-weight:800;'>📊 Career Readiness Dashboard</h1>
    <p style='font-size:1.1rem;color:#555;margin-bottom:1.5rem;'>
        Your real-time career metrics, skill coverage, and progress overview.
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
    _metric_card(c1, str(resume_score), "Resume Score", "#0066FF")
    _metric_card(c2, str(ats_score), "ATS Score", "#0066FF")
    _metric_card(c3, str(len(skills_found)), "Skills Found", "#00A651")
    readiness_color = "#00A651" if readiness >= 70 else ("#FF9500" if readiness >= 40 else "#FF3B30")
    _metric_card(c4, f"{readiness}%", "Career Readiness", readiness_color)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Readiness Gauge ────────────────────────────────────────────────────────
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=readiness,
            delta={"reference": 70, "valueformat": ".1f"},
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Career Readiness Score", "font": {"family": "Space Grotesk", "size": 15}},
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
            st.success("🚀 **Job Ready!** You're well-positioned for your target roles.")
        elif readiness >= 40:
            st.warning("📈 **Getting There!** Focus on the missing skills to improve readiness.")
        else:
            st.error("🔧 **Needs Work.** Start with your resume and skill gaps.")

    with chart_col2:
        # Skills donut chart
        if total_skills > 0:
            fig_donut = go.Figure(go.Pie(
                labels=["Skills Found", "Skills Missing"],
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
                title=dict(text="Skills Coverage", font=dict(family="Space Grotesk", size=15)),
                paper_bgcolor="white", font={"family": "Space Grotesk"},
                margin=dict(t=50, b=20, l=20, r=20), height=300,
                annotations=[dict(
                    text=f"<b>{len(skills_found)}<br>Skills</b>",
                    x=0.5, y=0.5, font_size=16, showarrow=False,
                    font=dict(family="Space Grotesk", color="#0066FF"),
                )],
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.markdown("""
            <div class="brut-card" style="text-align:center;padding:2rem;">
                <p style="color:#999;">Analyse your resume to see skill data</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Score Breakdown Bar ────────────────────────────────────────────────────
    st.markdown("### 📈 Score Breakdown")
    fig_bar = go.Figure()
    categories = ["Resume Score", "ATS Score", "Skill Coverage", "Overall Readiness"]
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
                      annotation_text="Target: 70%", annotation_position="right")
    fig_bar.update_layout(
        paper_bgcolor="white", font={"family": "Space Grotesk"},
        yaxis=dict(range=[0, 110], title="Score (%)"),
        xaxis=dict(title=""),
        margin=dict(t=20, b=20, l=20, r=20), height=300,
        showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── History Table ──────────────────────────────────────────────────────────
    st.markdown("### 📋 Analysis History (Last 5)")
    try:
        history = db_manager.get_all_resume_analyses()[:5]
        if history:
            df_hist = pd.DataFrame([{
                "Date": h["date"][:10] if h.get("date") else "N/A",
                "Resume Score": h.get("resume_score", 0),
                "ATS Score": h.get("ats_score", 0),
                "Experience": h.get("experience_level", "N/A"),
                "Skills Found": len(h.get("skills_found", [])),
            } for h in history])
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info("No history yet. Analyse your resume to start tracking.")
    except Exception:
        st.info("History unavailable.")

    # ── Upcoming Exams ─────────────────────────────────────────────────────────
    if study_plan:
        st.markdown("### 📅 Study Plan Overview")
        priority = study_plan.get("priority_ranking", [])
        if priority:
            df_priority = pd.DataFrame(priority)
            df_priority.columns = [c.replace("_", " ").title() for c in df_priority.columns]
            st.dataframe(df_priority, use_container_width=True, hide_index=True)

    # ── Skills Display ─────────────────────────────────────────────────────────
    if skills_found:
        st.markdown("### 🛠️ Your Skills")
        chips_html = "".join(f'<span class="skill-chip">{s}</span>' for s in skills_found)
        st.markdown(f'<div style="line-height:2.4;">{chips_html}</div>', unsafe_allow_html=True)

    if skills_missing:
        st.markdown("### ❌ Skills to Acquire")
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
    st.markdown("""
    <div class="brut-card" style="text-align:center;padding:3rem;box-shadow:8px 8px 0px #0066FF;border-color:#0066FF;">
        <div style="font-size:4rem;">📊</div>
        <h2 style="font-size:1.8rem;font-weight:800;">No Data Yet</h2>
        <p style="color:#555;font-size:1.1rem;">
            Your career dashboard will come alive after you analyse your resume.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📄 Go Analyse My Resume →", key="dash_to_resume"):
        st.session_state["nav_page"] = "📄 Resume Analyzer"
        st.rerun()
