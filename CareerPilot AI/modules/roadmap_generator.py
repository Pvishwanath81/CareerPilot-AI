"""
CareerPilot AI — Module 4: Career Roadmap Generator
AI-powered month-by-month career roadmap for your target role.
"""

import streamlit as st
import pandas as pd
from datetime import date

from utils import ai_helpers, db_manager, pdf_generator

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
    st.markdown("""
    <h1 style='font-size:2.4rem;font-weight:800;'>🎯 Career Roadmap Generator</h1>
    <p style='font-size:1.1rem;color:#555;margin-bottom:1.5rem;'>
        Get a personalised, month-by-month roadmap to reach your target career role.
    </p>
    """, unsafe_allow_html=True)

    # ── Input Form ─────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        career_goal = st.selectbox("🎯 Target Career Role", CAREER_GOALS)
        experience = st.selectbox("📊 Current Experience Level", EXPERIENCE_LEVELS)
    with col2:
        timeline = st.selectbox("📅 Target Timeline", list(TIMELINES.keys()), index=1)
        current_skills = st.text_area(
            "🛠️ Your Current Skills (comma-separated)",
            placeholder="Python, SQL, Excel, Git...",
            height=100,
        )

    generate_btn = st.button("🚀 Generate My Career Roadmap", key="btn_gen_roadmap", use_container_width=False)

    if generate_btn:
        career_data = {
            "career_goal": career_goal,
            "experience_level": experience,
            "current_skills": [s.strip() for s in current_skills.split(",") if s.strip()],
            "timeline": timeline,
            "timeline_months": TIMELINES[timeline],
        }

        with st.spinner(f"🤖 Building your {timeline} {career_goal} roadmap..."):
            result = ai_helpers.generate_roadmap(career_data)

        if "error" in result:
            st.error(f"❌ Roadmap generation failed: {result['error']}")
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
        st.info("💡 Showing your last roadmap. Change settings above and regenerate.")
        _display_roadmap(
            st.session_state["roadmap"],
            meta.get("career_goal", ""),
            meta.get("experience_level", ""),
            meta.get("timeline", ""),
        )


def _display_roadmap(result: dict, career_goal: str, experience: str, timeline: str):
    """Render the roadmap."""
    st.markdown("---")

    # Header
    st.markdown(f"""
    <div style="background:#000;color:#fff;padding:1.5rem 2rem;
                border:3px solid #000;box-shadow:6px 6px 0px #0066FF;margin-bottom:1.5rem;">
        <div style="font-size:0.85rem;font-weight:700;color:#0066FF;text-transform:uppercase;
                    letter-spacing:0.1em;">Career Roadmap</div>
        <div style="font-size:2rem;font-weight:800;margin-top:0.3rem;">{career_goal}</div>
        <div style="color:#ccc;margin-top:0.3rem;">{experience} · {timeline} Plan</div>
    </div>
    """, unsafe_allow_html=True)

    months_data = result.get("roadmap", [])

    # ── Month Cards ────────────────────────────────────────────────────────────
    if months_data:
        st.markdown("### 📅 Month-by-Month Roadmap")
        for m in months_data:
            month_num = m.get("month", "?")
            title = m.get("title", "")
            skills = m.get("skills_to_learn", [])
            projects = m.get("projects_to_build", [])
            courses = m.get("courses", [])
            certs = m.get("certifications", [])
            milestone = m.get("milestones", "")

            with st.expander(f"📅 Month {month_num} — {title}", expanded=(month_num == 1)):
                grid_col1, grid_col2 = st.columns(2)

                with grid_col1:
                    if skills:
                        st.markdown("**🧠 Skills to Learn**")
                        chips_html = "".join(f'<span class="skill-chip-neutral">{s}</span>' for s in skills)
                        st.markdown(f'<div style="line-height:2.2;margin-bottom:0.8rem;">{chips_html}</div>',
                                    unsafe_allow_html=True)

                    if projects:
                        st.markdown("**💻 Projects to Build**")
                        for p in projects:
                            st.markdown(f"→ {p}")

                with grid_col2:
                    if courses:
                        st.markdown("**📖 Courses**")
                        for c in courses:
                            st.markdown(f"• {c}")

                    if certs:
                        st.markdown("**🏆 Certifications**")
                        for cert in certs:
                            st.markdown(f"🎓 {cert}")

                if milestone:
                    st.markdown(f"""
                    <div style="background:#F0FFF6;border:2px solid #00A651;padding:0.8rem 1rem;
                                margin-top:0.8rem;box-shadow:3px 3px 0px #00A651;">
                        <strong>🏁 Milestone:</strong> {milestone}
                    </div>
                    """, unsafe_allow_html=True)

    # ── Job Prep ───────────────────────────────────────────────────────────────
    job_prep = result.get("job_prep", {})
    if job_prep:
        st.markdown("### 💼 Job Preparation")
        jp_col1, jp_col2, jp_col3 = st.columns(3)

        with jp_col1:
            st.markdown("**📝 Resume Tips**")
            for tip in job_prep.get("resume_tips", []):
                st.markdown(f"• {tip}")

        with jp_col2:
            st.markdown("**🎤 Interview Topics**")
            for topic in job_prep.get("interview_topics", []):
                st.markdown(f"• {topic}")

        with jp_col3:
            st.markdown("**🌐 Platforms**")
            for platform in job_prep.get("platforms", []):
                st.markdown(f"""
                <span style="background:#0066FF;color:#fff;padding:0.2rem 0.7rem;
                             font-weight:700;border:2px solid #000;display:inline-block;
                             margin:0.2rem;font-size:0.85rem;">{platform}</span>
                """, unsafe_allow_html=True)

    # ── Resources Table ────────────────────────────────────────────────────────
    resources = result.get("resources", [])
    if resources:
        st.markdown("### 📚 Learning Resources")
        df_res = pd.DataFrame([{
            "Resource": r.get("name", ""),
            "Type": r.get("type", ""),
            "URL": r.get("url", ""),
            "Cost": "✅ Free" if r.get("free") else "💰 Paid",
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
            label="📥 Download Roadmap PDF",
            data=pdf_bytes,
            file_name=f"career_roadmap_{career_goal.replace(' ', '_').lower()}_{_today()}.pdf",
            mime="application/pdf",
            key="download_roadmap_pdf",
        )
    except Exception as e:
        st.warning(f"PDF generation unavailable: {e}")


def _show_api_key_hint():
    st.markdown("""
    <div class="brut-card" style="border-color:#FF9500;box-shadow:4px 4px 0px #FF9500;">
        <strong>🔑 API Key Required</strong><br>
        Set <code>GOOGLE_API_KEY</code> in your <code>.env</code> file.<br>
        Get a free key at <a href="https://aistudio.google.com/app/apikey" target="_blank">Google AI Studio</a>
    </div>
    """, unsafe_allow_html=True)


def _today():
    return date.today().strftime("%Y%m%d")
