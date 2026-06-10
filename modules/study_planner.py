"""
CareerPilot AI — Module 2: Smart Study Planner
Enter exams and get a personalised daily/weekly schedule.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta

from utils import ai_helpers, db_manager, pdf_generator


def show_study_planner():
    st.markdown("""
    <h1 style='font-size:2.4rem;font-weight:800;'>📚 Smart Study Planner</h1>
    <p style='font-size:1.1rem;color:#555;margin-bottom:1.5rem;'>
        Enter your subjects and exam dates — get a personalised AI study schedule in seconds.
    </p>
    """, unsafe_allow_html=True)

    # ── Input Form ─────────────────────────────────────────────────────────────
    with st.form("study_plan_form"):
        st.markdown("#### 👤 Student Information")
        student_name = st.text_input("Your Name", placeholder="e.g. Aisha Sharma")

        st.markdown("#### 📖 Subjects")
        subjects_raw = st.text_area(
            "Enter subjects (one per line)",
            placeholder="Mathematics\nPhysics\nComputer Science\nChemistry",
            height=120,
        )

        st.markdown("#### ⏰ Study Preferences")
        col1, col2 = st.columns(2)
        with col1:
            hours_per_day = st.slider("Available study hours per day", 1, 12, 4)
        with col2:
            start_date = st.date_input("Study start date", value=date.today())

        st.markdown("#### 📅 Exam Dates & Difficulty")
        subjects_list = [s.strip() for s in subjects_raw.split("\n") if s.strip()]

        subject_configs = []
        if subjects_list:
            st.markdown("Set difficulty and exam date for each subject:")
            for subj in subjects_list[:8]:  # Cap at 8
                c1, c2, c3 = st.columns([3, 2, 2])
                with c1:
                    st.markdown(f"**{subj}**")
                with c2:
                    difficulty = st.selectbox(
                        "Difficulty",
                        ["Easy", "Medium", "Hard"],
                        key=f"diff_{subj}",
                        index=1,
                    )
                with c3:
                    exam_date = st.date_input(
                        "Exam Date",
                        value=date.today() + timedelta(days=30),
                        key=f"exam_{subj}",
                    )
                subject_configs.append({
                    "subject": subj,
                    "difficulty": difficulty,
                    "exam_date": str(exam_date),
                })
        else:
            st.info("Enter subjects above to configure each one.")

        submitted = st.form_submit_button("📅 Generate My Study Plan", use_container_width=True)

    # ── Generate ───────────────────────────────────────────────────────────────
    if submitted:
        if not student_name.strip():
            st.error("Please enter your name.")
            return
        if not subject_configs:
            st.error("Please enter at least one subject.")
            return

        student_data = {
            "name": student_name,
            "subjects": subject_configs,
            "hours_per_day": hours_per_day,
            "start_date": str(start_date),
        }

        with st.spinner("🤖 Generating your personalised study plan..."):
            result = ai_helpers.generate_study_plan(student_data)

        if "error" in result:
            st.error(f"❌ AI failed: {result['error']}")
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
        st.info("💡 Showing your last study plan. Fill in the form above to regenerate.")
        _display_plan(
            st.session_state["study_plan"],
            st.session_state.get("study_plan_subjects", []),
        )


def _display_plan(result: dict, subject_configs: list):
    """Render the study plan."""
    st.markdown("---")
    st.markdown("<h2>📋 Your Personalised Study Plan</h2>", unsafe_allow_html=True)

    priority = result.get("priority_ranking", [])
    daily = result.get("daily_schedule", [])
    weekly = result.get("weekly_plan", [])
    revision = result.get("revision_plan", [])
    tips = result.get("tips", [])

    # ── Priority Ranking ───────────────────────────────────────────────────────
    if priority:
        st.markdown("### 🎯 Subject Priority Ranking")
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
                    title="Daily Study Hours Distribution",
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
                title="Study Time Distribution",
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
        st.markdown("### 📅 Daily Schedule")
        df_display = pd.DataFrame(daily)
        df_display.columns = [c.replace("_", " ").title() for c in df_display.columns]
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    # ── Weekly Plan ────────────────────────────────────────────────────────────
    if weekly:
        st.markdown("### 📆 Weekly Plan")
        for week in weekly:
            with st.expander(f"Week {week.get('week','?')} — {week.get('focus','')}"):
                subjects_str = ", ".join(week.get("subjects", []))
                st.markdown(f"**📚 Subjects:** {subjects_str}")
                st.markdown(f"**🎯 Goals:** {week.get('goals','')}")

    # ── Revision Plan ──────────────────────────────────────────────────────────
    if revision:
        st.markdown("### 🔄 Revision Schedule")
        df_rev = pd.DataFrame(revision)
        if not df_rev.empty:
            df_rev.columns = [c.replace("_", " ").title() for c in df_rev.columns]
            st.dataframe(df_rev, use_container_width=True, hide_index=True)

    # ── Tips ───────────────────────────────────────────────────────────────────
    if tips:
        st.markdown("### 💡 Study Tips")
        tip_cols = st.columns(min(len(tips), 3))
        for i, tip in enumerate(tips[:6]):
            with tip_cols[i % len(tip_cols)]:
                st.markdown(f"""
                <div class="brut-card" style="min-height:80px;">
                    <strong>Tip {i+1}</strong><br>
                    <span style="font-size:0.9rem;">{tip}</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Download ───────────────────────────────────────────────────────────────
    try:
        pdf_bytes = pdf_generator.generate_study_plan_report(result)
        st.download_button(
            label="📥 Download Study Plan PDF",
            data=pdf_bytes,
            file_name=f"study_plan_{_today()}.pdf",
            mime="application/pdf",
            key="download_study_plan_pdf",
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
