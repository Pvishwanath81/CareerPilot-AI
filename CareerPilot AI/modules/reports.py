"""
CareerPilot AI — Module 6: Reports
History of all saved analyses with PDF download per row.
"""

import streamlit as st
import pandas as pd
from datetime import date

from utils import db_manager, pdf_generator


def show_reports():
    st.markdown("""
    <h1 style='font-size:2.4rem;font-weight:800;'>📥 Reports & History</h1>
    <p style='font-size:1.1rem;color:#555;margin-bottom:1.5rem;'>
        Download PDF reports for any of your saved analyses, study plans, roadmaps, and interview sessions.
    </p>
    """, unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Resume Analyses",
        "📚 Study Plans",
        "🎯 Career Roadmaps",
        "🎤 Interview Sessions",
    ])

    with tab1:
        _show_resume_history()

    with tab2:
        _show_study_plans_history()

    with tab3:
        _show_roadmaps_history()

    with tab4:
        _show_interview_history()

    # ── Clear All ──────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚠️ Danger Zone")
    with st.expander("🗑️ Clear All History"):
        st.warning("This will permanently delete all saved analyses, plans, roadmaps, and sessions.")
        confirm = st.checkbox("I understand, delete everything")
        if confirm:
            if st.button("🗑️ Delete All Data", key="btn_delete_all"):
                try:
                    db_manager.delete_all_data()
                    # Clear session state
                    for key in ["resume_score", "ats_score", "skills_found", "skills_missing",
                                "study_plan", "roadmap", "last_analysis"]:
                        st.session_state[key] = 0 if key in ["resume_score", "ats_score"] else \
                                               [] if "skills" in key else None
                    st.success("✅ All history cleared.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear data: {e}")


def _show_resume_history():
    """Display resume analysis history."""
    st.markdown("### 📄 Resume Analysis History")
    try:
        analyses = db_manager.get_all_resume_analyses()
    except Exception as e:
        st.error(f"Could not load history: {e}")
        return

    if not analyses:
        _empty_state("No resume analyses yet. Go to Resume Analyzer to get started!")
        return

    for i, analysis in enumerate(analyses):
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1])
            with col1:
                st.markdown(f"**{analysis.get('date', 'N/A')[:10]}**")
                st.markdown(f"<small>{analysis.get('experience_level', 'N/A')}</small>",
                            unsafe_allow_html=True)
            with col2:
                score = analysis.get("resume_score", 0)
                color = "#00A651" if score >= 70 else ("#FF9500" if score >= 50 else "#FF3B30")
                st.markdown(f"<span style='color:{color};font-weight:800;font-size:1.2rem;'>{score}/100</span>",
                            unsafe_allow_html=True)
                st.markdown("<small>Resume</small>", unsafe_allow_html=True)
            with col3:
                ats = analysis.get("ats_score", 0)
                color2 = "#00A651" if ats >= 70 else ("#FF9500" if ats >= 50 else "#FF3B30")
                st.markdown(f"<span style='color:{color2};font-weight:800;font-size:1.2rem;'>{ats}/100</span>",
                            unsafe_allow_html=True)
                st.markdown("<small>ATS</small>", unsafe_allow_html=True)
            with col4:
                skills = analysis.get("skills_found", [])
                st.markdown(f"**{len(skills)}** skills found")
            with col5:
                try:
                    pdf_bytes = pdf_generator.generate_resume_report(analysis)
                    st.download_button(
                        "📥 PDF",
                        data=pdf_bytes,
                        file_name=f"resume_{analysis.get('date','')[:10]}.pdf",
                        mime="application/pdf",
                        key=f"dl_resume_{i}_{analysis.get('id', i)}",
                    )
                except Exception:
                    st.markdown("—")
        st.divider()


def _show_study_plans_history():
    """Display study plan history."""
    st.markdown("### 📚 Study Plans History")
    try:
        plans = db_manager.get_all_study_plans()
    except Exception as e:
        st.error(f"Could not load history: {e}")
        return

    if not plans:
        _empty_state("No study plans yet. Go to Study Planner to create one!")
        return

    for i, plan in enumerate(plans):
        with st.container():
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                st.markdown(f"**{plan.get('student_name', 'N/A')}**")
                st.markdown(f"<small>{plan.get('date', 'N/A')[:10]}</small>",
                            unsafe_allow_html=True)
            with col2:
                subjects = plan.get("subjects", [])
                subjects_str = ", ".join(subjects[:3]) if subjects else "N/A"
                if len(subjects) > 3:
                    subjects_str += f" +{len(subjects)-3} more"
                st.markdown(f"📚 {subjects_str}")
            with col3:
                try:
                    pdf_bytes = pdf_generator.generate_study_plan_report(plan)
                    st.download_button(
                        "📥 PDF",
                        data=pdf_bytes,
                        file_name=f"study_plan_{plan.get('date','')[:10]}.pdf",
                        mime="application/pdf",
                        key=f"dl_plan_{i}_{plan.get('id', i)}",
                    )
                except Exception:
                    st.markdown("—")
        st.divider()


def _show_roadmaps_history():
    """Display career roadmaps history."""
    st.markdown("### 🎯 Career Roadmaps History")
    try:
        roadmaps = db_manager.get_all_roadmaps()
    except Exception as e:
        st.error(f"Could not load history: {e}")
        return

    if not roadmaps:
        _empty_state("No roadmaps yet. Go to Career Roadmap to generate one!")
        return

    for i, rm in enumerate(roadmaps):
        with st.container():
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                st.markdown(f"**{rm.get('career_goal', 'N/A')}**")
                st.markdown(f"<small>{rm.get('date', 'N/A')[:10]}</small>",
                            unsafe_allow_html=True)
            with col2:
                st.markdown(f"📊 {rm.get('experience_level', 'N/A')}")
            with col3:
                try:
                    roadmap_for_pdf = {
                        "career_goal": rm.get("career_goal", ""),
                        "experience_level": rm.get("experience_level", ""),
                        "roadmap_data": rm.get("roadmap_data", {}),
                    }
                    pdf_bytes = pdf_generator.generate_roadmap_report(roadmap_for_pdf)
                    st.download_button(
                        "📥 PDF",
                        data=pdf_bytes,
                        file_name=f"roadmap_{rm.get('career_goal','').replace(' ','_')}_{rm.get('date','')[:10]}.pdf",
                        mime="application/pdf",
                        key=f"dl_roadmap_{i}_{rm.get('id', i)}",
                    )
                except Exception:
                    st.markdown("—")
        st.divider()


def _show_interview_history():
    """Display interview sessions history."""
    st.markdown("### 🎤 Interview Sessions History")
    try:
        sessions = db_manager.get_all_interview_sessions()
    except Exception as e:
        st.error(f"Could not load history: {e}")
        return

    if not sessions:
        _empty_state("No interview sessions yet. Go to Interview Coach to start practising!")
        return

    for i, sess in enumerate(sessions):
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            with col1:
                st.markdown(f"**{sess.get('role', 'N/A')}**")
                st.markdown(f"<small>{sess.get('date', 'N/A')[:10]}</small>",
                            unsafe_allow_html=True)
            with col2:
                st.markdown(f"📊 {sess.get('difficulty', 'N/A')}")
            with col3:
                ts = sess.get("total_score", 0)
                ms = sess.get("max_score", 100)
                pct = int((ts / ms) * 100) if ms > 0 else 0
                sc_color = "#00A651" if pct >= 70 else ("#FF9500" if pct >= 50 else "#FF3B30")
                st.markdown(f"<span style='color:{sc_color};font-weight:800;'>{ts}/{ms}</span>",
                            unsafe_allow_html=True)
            with col4:
                grade = sess.get("grade", "N/A")
                st.markdown(f"**Grade: {grade}**")
            with col5:
                try:
                    pdf_bytes = pdf_generator.generate_interview_report(sess)
                    st.download_button(
                        "📥 PDF",
                        data=pdf_bytes,
                        file_name=f"interview_{sess.get('role','').replace(' ','_')}_{sess.get('date','')[:10]}.pdf",
                        mime="application/pdf",
                        key=f"dl_interview_{i}_{sess.get('id', i)}",
                    )
                except Exception:
                    st.markdown("—")
        st.divider()


def _empty_state(message: str):
    st.markdown(f"""
    <div class="brut-card" style="text-align:center;padding:2.5rem;color:#555;">
        <div style="font-size:3rem;margin-bottom:0.5rem;">📭</div>
        <p style="font-size:1rem;">{message}</p>
    </div>
    """, unsafe_allow_html=True)
