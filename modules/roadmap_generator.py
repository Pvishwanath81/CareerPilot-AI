"""
CareerPilot AI — Module 4: Career Roadmap Generator
AI-powered month-by-month career roadmap for your target role.
"""

import os as _os, sys as _sys
_mod_dir = _os.path.dirname(_os.path.abspath(__file__))
_project_root = _os.path.dirname(_mod_dir)
if _project_root not in _sys.path:
    _sys.path.insert(0, _project_root)


import streamlit as st
import pandas as pd
from datetime import date

from utils import ai_helpers, db_manager, pdf_generator
from i18n import t

CAREER_GOALS = [
    "Software Engineer",
    "Data Scientist",
    "AI/ML Engineer",
    "Cloud Engineer",
    "Cybersecurity Analyst",
    "Full Stack Developer",
    "DevOps Engineer",
    "Mobile App Developer",
    "Product Manager",
    "Data Analyst",
]

EXPERIENCE_LEVELS = [
    "Fresher (0-1 yr)",
    "Junior (1-2 yrs)",
    "Mid-Level (2-4 yrs)",
]

TIMELINES = {
    "3 months": 3,
    "6 months": 6,
    "1 year": 12,
}


def show_roadmap_generator():
    st.markdown(f"""
    <h1 style='font-size:2.4rem;font-weight:800;'>{t("roadmap_title")}</h1>
    <p style='font-size:1.1rem;color:#555;margin-bottom:1.5rem;'>
        {t("roadmap_subtitle")}
    </p>
    """, unsafe_allow_html=True)

    # ── Input Form ─────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        career_goal = st.selectbox(t("roadmap_target_role"), CAREER_GOALS)
        experience = st.selectbox(t("roadmap_exp_level"), EXPERIENCE_LEVELS)
    with col2:
        timeline = st.selectbox(t("roadmap_timeline"), list(TIMELINES.keys()), index=1)
        current_skills = st.text_area(
            t("roadmap_skills_label"),
            placeholder=t("roadmap_skills_placeholder"),
            height=100,
        )

    generate_btn = st.button(t("roadmap_generate_btn"), key="btn_gen_roadmap")

    if generate_btn:
        career_data = {
            "career_goal": career_goal,
            "experience_level": experience,
            "current_skills": [s.strip() for s in current_skills.split(",") if s.strip()],
            "timeline": timeline,
            "timeline_months": TIMELINES[timeline],
        }

        with st.spinner(t("roadmap_generating").format(timeline=timeline, goal=career_goal)):
            result = ai_helpers.generate_roadmap(career_data)

        if "error" in result:
            st.error(f"{t('roadmap_ai_failed')}{result['error']}")
            _show_api_key_hint()
            return

        # Save to session & DB
        st.session_state["roadmap"] = result
        st.session_state["roadmap_meta"] = {
            "career_goal": career_goal,
            "experience_level": experience,
            "timeline": timeline,
        }
        try:
            db_manager.save_career_roadmap({
                "career_goal": career_goal,
                "experience_level": experience,
                "roadmap_data": result,
            })
        except Exception:
            pass

        _display_roadmap(result, career_goal, experience, timeline)

    elif st.session_state.get("roadmap"):
        meta = st.session_state.get("roadmap_meta", {})
        st.info(t("roadmap_last_info"))
        _display_roadmap(
            st.session_state["roadmap"],
            meta.get("career_goal", ""),
            meta.get("experience_level", ""),
            meta.get("timeline", ""),
        )


def _display_roadmap(result: dict, career_goal: str, experience: str, timeline: str):
    """Render the roadmap."""
    st.markdown("---")

    # Header banner
    st.markdown(f"""
    <div style="background:#000;color:#fff;padding:1.5rem 2rem;
                border:3px solid #000;box-shadow:6px 6px 0px #0066FF;margin-bottom:1.5rem;">
        <div style="font-size:0.85rem;font-weight:700;color:#0066FF;text-transform:uppercase;
                    letter-spacing:0.1em;">{t("roadmap_label")}</div>
        <div style="font-size:2rem;font-weight:800;margin-top:0.3rem;">{career_goal}</div>
        <div style="color:#ccc;margin-top:0.3rem;">{experience} · {timeline} {t("roadmap_plan_suffix")}</div>
    </div>
    """, unsafe_allow_html=True)

    months_data = result.get("roadmap", [])

    # ── Month Cards ────────────────────────────────────────────────────────────
    if months_data:
        st.markdown(t("roadmap_monthly_heading"))
        for m in months_data:
            month_num = m.get("month", "?")
            title = m.get("title", "")
            skills = m.get("skills_to_learn", [])
            projects = m.get("projects_to_build", [])
            courses = m.get("courses", [])
            certs = m.get("certifications", [])
            milestone = m.get("milestones", "")

            with st.expander(
                f"📅 {t('roadmap_month_label')} {month_num} — {title}",
                expanded=(month_num == 1),
            ):
                grid_col1, grid_col2 = st.columns(2)

                with grid_col1:
                    if skills:
                        st.markdown(t("roadmap_skills_to_learn"))
                        chips_html = "".join(
                            f'<span class="skill-chip-neutral">{s}</span>' for s in skills
                        )
                        st.markdown(
                            f'<div style="line-height:2.2;margin-bottom:0.8rem;">{chips_html}</div>',
                            unsafe_allow_html=True,
                        )

                    if projects:
                        st.markdown(t("roadmap_projects"))
                        for p in projects:
                            st.markdown(f"→ {p}")

                with grid_col2:
                    if courses:
                        st.markdown(t("roadmap_courses"))
                        for c in courses:
                            st.markdown(f"• {c}")

                    if certs:
                        st.markdown(t("roadmap_certs"))
                        for cert in certs:
                            st.markdown(f"🎓 {cert}")

                if milestone:
                    st.markdown(f"""
                    <div style="background:#F0FFF6;border:2px solid #00A651;padding:0.8rem 1rem;
                                margin-top:0.8rem;box-shadow:3px 3px 0px #00A651;">
                        {t("roadmap_milestone")} {milestone}
                    </div>
                    """, unsafe_allow_html=True)

    # ── Job Prep ───────────────────────────────────────────────────────────────
    job_prep = result.get("job_prep", {})
    if job_prep:
        st.markdown(t("roadmap_job_prep"))
        jp_col1, jp_col2, jp_col3 = st.columns(3)

        with jp_col1:
            st.markdown(t("roadmap_resume_tips"))
            for tip in job_prep.get("resume_tips", []):
                st.markdown(f"• {tip}")

        with jp_col2:
            st.markdown(t("roadmap_interview_topics"))
            for topic in job_prep.get("interview_topics", []):
                st.markdown(f"• {topic}")

        with jp_col3:
            st.markdown(t("roadmap_platforms"))
            for platform in job_prep.get("platforms", []):
                st.markdown(f"""
                <span style="background:#0066FF;color:#fff;padding:0.2rem 0.7rem;
                             font-weight:700;border:2px solid #000;display:inline-block;
                             margin:0.2rem;font-size:0.85rem;">{platform}</span>
                """, unsafe_allow_html=True)

    # ── Resources Table ────────────────────────────────────────────────────────
    resources = result.get("resources", [])
    if resources:
        st.markdown(t("roadmap_resources_heading"))
        df_res = pd.DataFrame([{
            t("roadmap_resource_col_name"): r.get("name", ""),
            t("roadmap_resource_col_type"): r.get("type", ""),
            t("roadmap_resource_col_url"): r.get("url", ""),
            t("roadmap_resource_col_cost"): (
                t("roadmap_resource_free") if r.get("free") else t("roadmap_resource_paid")
            ),
        } for r in resources])
        st.dataframe(df_res, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Download ───────────────────────────────────────────────────────────────
    try:
        roadmap_for_pdf = {
            "career_goal": career_goal,
            "experience_level": experience,
            "roadmap_data": result,
        }
        pdf_bytes = pdf_generator.generate_roadmap_report(roadmap_for_pdf)
        st.download_button(
            label=t("roadmap_download_btn"),
            data=pdf_bytes,
            file_name=f"career_roadmap_{career_goal.replace(' ', '_').lower()}_{_today()}.pdf",
            mime="application/pdf",
            key="download_roadmap_pdf",
        )
    except Exception as e:
        st.warning(f"{t('roadmap_pdf_unavailable')}{e}")


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
