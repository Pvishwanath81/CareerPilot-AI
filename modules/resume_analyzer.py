"""
CareerPilot AI — Module 1: AI Resume Analyzer
Upload a PDF resume, extract text, get ATS score, skill gap analysis, and recommendations.
"""

import os as _os, sys as _sys
_mod_dir = _os.path.dirname(_os.path.abspath(__file__))
_project_root = _os.path.dirname(_mod_dir)
if _project_root not in _sys.path:
    _sys.path.insert(0, _project_root)


import streamlit as st
import PyPDF2
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import io

from utils import ai_helpers, db_manager, pdf_generator
from i18n import t


def show_resume_analyzer():
    st.markdown(f"""
    <h1 style='font-size:2.4rem;font-weight:800;'>{t("resume_title")}</h1>
    <p style='font-size:1.1rem;color:#555;margin-bottom:1.5rem;'>
        {t("resume_subtitle")}
    </p>
    """, unsafe_allow_html=True)

    # ── File Upload ────────────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        t("resume_upload_label"),
        type=["pdf"],
        help=t("resume_upload_help"),
    )

    if uploaded_file is not None:
        with st.spinner(t("resume_reading")):
            resume_text = _extract_pdf_text(uploaded_file)

        if not resume_text or len(resume_text.strip()) < 50:
            st.error(t("resume_error_extract"))
            return

        st.success(t("resume_loaded").format(n=len(resume_text.split())))

        with st.expander(t("resume_preview_label")):
            st.text(resume_text[:500] + ("..." if len(resume_text) > 500 else ""))

        if st.button(t("resume_analyse_btn"), key="btn_analyse_resume"):
            _run_analysis(resume_text)

    elif st.session_state.get("resume_score", 0) > 0:
        st.info(t("resume_last_result_info"))
        _display_results(st.session_state.get("last_analysis", {}))


def _extract_pdf_text(uploaded_file) -> str:
    """Extract all text from all pages of a PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text_parts = []
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""


def _run_analysis(resume_text: str):
    """Call AI, parse results, display and save."""
    with st.spinner(t("resume_analysing")):
        result = ai_helpers.analyze_resume(resume_text)

    if "error" in result:
        st.error(f"{t('resume_ai_failed')}{result['error']}")
        _show_api_key_hint()
        return

    st.session_state["resume_score"] = result.get("resume_score", 0)
    st.session_state["ats_score"] = result.get("ats_score", 0)
    st.session_state["skills_found"] = result.get("skills_found", [])
    st.session_state["skills_missing"] = result.get("missing_skills", [])
    st.session_state["last_analysis"] = result

    try:
        db_manager.save_resume_analysis(result)
    except Exception:
        pass

    _display_results(result)


def _display_results(result: dict):
    """Render all analysis results."""
    if not result:
        return

    resume_score = result.get("resume_score", 0)
    ats_score = result.get("ats_score", 0)
    exp_level = result.get("experience_level", "N/A")
    skills_found = result.get("skills_found", [])
    missing_skills = result.get("missing_skills", [])
    strengths = result.get("strengths", [])
    weaknesses = result.get("weaknesses", [])
    recommendations = result.get("recommendations", [])

    st.markdown("---")
    st.markdown(f"<h2>📊 {t('resume_results_heading')}</h2>", unsafe_allow_html=True)

    # ── Score Badges ───────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        badge_color = "#00A651" if resume_score >= 70 else ("#FF9500" if resume_score >= 50 else "#FF3B30")
        st.markdown(f"""
        <div class="metric-card" style="border-color:{badge_color};box-shadow:4px 4px 0px {badge_color};">
            <div class="metric-value" style="color:{badge_color};">{resume_score}/100</div>
            <div class="metric-label">{t("resume_score_label")}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        ats_color = "#00A651" if ats_score >= 70 else ("#FF9500" if ats_score >= 50 else "#FF3B30")
        st.markdown(f"""
        <div class="metric-card" style="border-color:{ats_color};box-shadow:4px 4px 0px {ats_color};">
            <div class="metric-value" style="color:{ats_color};">{ats_score}/100</div>
            <div class="metric-label">{t("resume_ats_label")}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="font-size:1.6rem;">{exp_level}</div>
            <div class="metric-label">{t("resume_exp_label")}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row ─────────────────────────────────────────────────────────────
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=resume_score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": t("resume_score_chart_title"),
                   "font": {"family": "Space Grotesk", "size": 16, "color": "#000000"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#000000"},
                "bar": {"color": "#0066FF", "thickness": 0.3},
                "steps": [
                    {"range": [0, 40], "color": "#FFE0DE"},
                    {"range": [40, 70], "color": "#FFF3DE"},
                    {"range": [70, 100], "color": "#DEFFEE"},
                ],
                "threshold": {
                    "line": {"color": "#000000", "width": 3},
                    "thickness": 0.75,
                    "value": resume_score,
                },
                "bordercolor": "#000000",
                "borderwidth": 2,
            },
            number={"font": {"family": "Space Grotesk", "size": 40, "color": "#0066FF"}},
        ))
        fig_gauge.update_layout(
            paper_bgcolor="white", font={"family": "Space Grotesk"},
            margin=dict(t=40, b=20, l=20, r=20), height=280,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with chart_col2:
        found_count = len(skills_found)
        missing_count = len(missing_skills)
        if found_count + missing_count > 0:
            fig_pie = px.pie(
                values=[found_count, missing_count],
                names=[t("dash_skills_found_label"), t("dash_skills_missing_label")],
                color_discrete_sequence=["#0066FF", "#FF3B30"],
                title=t("resume_skills_coverage"),
            )
            fig_pie.update_traces(
                textinfo="label+percent",
                marker=dict(line=dict(color="#000000", width=2)),
            )
            fig_pie.update_layout(
                paper_bgcolor="white", font={"family": "Space Grotesk"},
                title_font=dict(family="Space Grotesk", size=16),
                margin=dict(t=40, b=20, l=20, r=20), height=280,
                legend=dict(font=dict(family="Space Grotesk")),
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info(t("dash_skill_coverage_empty"))

    # ── Skill Bar Chart ────────────────────────────────────────────────────────
    if skills_found or missing_skills:
        found_label = t("dash_skills_found_label")
        missing_label = t("dash_skills_missing_label")
        all_skills = (
            [(s, found_label, "#0066FF") for s in skills_found[:10]] +
            [(s, missing_label, "#FF3B30") for s in missing_skills[:10]]
        )
        df_skills = pd.DataFrame(all_skills, columns=["Skill", "Status", "Color"])
        df_skills["Value"] = 1

        fig_bar = px.bar(
            df_skills,
            x="Value", y="Skill", color="Status",
            orientation="h",
            title=t("resume_skills_overview"),
            color_discrete_map={found_label: "#0066FF", missing_label: "#FF3B30"},
        )
        fig_bar.update_layout(
            paper_bgcolor="white", font={"family": "Space Grotesk"},
            title_font=dict(family="Space Grotesk", size=16),
            xaxis=dict(showticklabels=False, title=""),
            yaxis=dict(title=""),
            margin=dict(t=40, b=20, l=20, r=20), height=350,
            legend=dict(font=dict(family="Space Grotesk")),
        )
        fig_bar.update_traces(marker=dict(line=dict(color="#000000", width=1.5)))
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Strengths / Weaknesses / Missing / Recommendations ────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(t("resume_strengths"))
        for s in strengths:
            st.success(s)

        st.markdown(t("resume_weaknesses"))
        for w in weaknesses:
            st.warning(w)

    with col_b:
        st.markdown(t("resume_missing_skills"))
        if missing_skills:
            chips_html = "".join(
                f'<span class="skill-chip-missing">{skill}</span>'
                for skill in missing_skills
            )
            st.markdown(f'<div style="line-height:2.2;">{chips_html}</div>', unsafe_allow_html=True)
        else:
            st.info(t("resume_no_missing"))

        st.markdown(t("resume_recommendations"))
        for rec in recommendations:
            st.info(rec)

    # ── Detected Skills ────────────────────────────────────────────────────────
    if skills_found:
        st.markdown(t("resume_detected_skills"))
        chips_html = "".join(
            f'<span class="skill-chip">{skill}</span>'
            for skill in skills_found
        )
        st.markdown(f'<div style="line-height:2.4;">{chips_html}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Download Button ────────────────────────────────────────────────────────
    try:
        pdf_bytes = pdf_generator.generate_resume_report(result)
        st.download_button(
            label=t("resume_download_btn"),
            data=pdf_bytes,
            file_name=f"resume_analysis_{_today()}.pdf",
            mime="application/pdf",
            key="download_resume_pdf",
        )
    except Exception as e:
        st.warning(f"{t('resume_pdf_unavailable')}{e}")


def _show_api_key_hint():
    st.markdown(f"""
    <div class="brut-card" style="border-color:#FF9500;box-shadow:4px 4px 0px #FF9500;">
        <strong>{t("api_key_required")}</strong><br>
        {t("api_key_hint_body")}<br><br>
        {t("api_key_link")} <a href="https://aistudio.google.com/app/apikey" target="_blank">Google AI Studio</a>
    </div>
    """, unsafe_allow_html=True)


def _today():
    from datetime import date
    return date.today().strftime("%Y%m%d")
