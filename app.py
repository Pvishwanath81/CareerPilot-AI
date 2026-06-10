"""
CareerPilot AI — Main Entry Point
AI-Powered Career & Academic Success Platform
Built by Team Trident
Run: streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "CareerPilot AI — Built by Team Trident",
    },
)

# ── Load CSS ───────────────────────────────────────────────────────────────────
def _load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# ── Load Google Fonts ──────────────────────────────────────────────────────────
def _load_fonts():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&display=swap"
          rel="stylesheet">
    """, unsafe_allow_html=True)

_load_fonts()
_load_css()

# ── Init DB ────────────────────────────────────────────────────────────────────
from utils import db_manager
try:
    db_manager.init_db()
except Exception as e:
    st.error(f"Database initialisation failed: {e}")

# ── Init Session State ─────────────────────────────────────────────────────────
_defaults = {
    "resume_score": 0,
    "ats_score": 0,
    "skills_found": [],
    "skills_missing": [],
    "study_plan": None,
    "roadmap": None,
    "interview_session": [],
    "last_analysis": {},
    "nav_page": "🏠 Home",
}
for key, val in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Import modules ─────────────────────────────────────────────────────────────
from modules.resume_analyzer import show_resume_analyzer
from modules.study_planner import show_study_planner
from modules.career_dashboard import show_career_dashboard
from modules.roadmap_generator import show_roadmap_generator
from modules.interview_coach import show_interview_coach
from modules.reports import show_reports

# ── Navigation options ─────────────────────────────────────────────────────────
NAV_OPTIONS = [
    "🏠 Home",
    "📄 Resume Analyzer",
    "📚 Study Planner",
    "📊 Career Dashboard",
    "🎯 Career Roadmap",
    "🎤 Interview Coach",
    "📥 Reports",
    "ℹ️ About",
]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo / Branding
    st.markdown("""
    <div style="padding:1rem 0;border-bottom:2px solid #0066FF;margin-bottom:1rem;">
        <div style="font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-0.02em;">
            🚀 CareerPilot <span style="color:#0066FF;">AI</span>
        </div>
        <div style="font-size:0.75rem;color:#888;margin-top:0.2rem;font-weight:500;">
            AI-Powered Career Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if api_key:
        st.markdown("""
        <div style="background:#00A651;color:#fff;padding:0.4rem 0.8rem;
                    font-size:0.8rem;font-weight:700;border:2px solid #fff;margin-bottom:1rem;">
            ✅ AI Connected
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#FF9500;color:#fff;padding:0.4rem 0.8rem;
                    font-size:0.8rem;font-weight:700;border:2px solid #fff;margin-bottom:1rem;">
            ⚠️ API Key Missing
        </div>
        """, unsafe_allow_html=True)

    # Navigation
    st.markdown("<div style='color:#888;font-size:0.75rem;font-weight:700;text-transform:uppercase;"
                "letter-spacing:0.08em;margin-bottom:0.5rem;'>Navigation</div>",
                unsafe_allow_html=True)

    selected_page = st.radio(
        "Navigation",
        NAV_OPTIONS,
        index=NAV_OPTIONS.index(st.session_state.get("nav_page", "🏠 Home")),
        label_visibility="collapsed",
        key="sidebar_nav",
    )
    st.session_state["nav_page"] = selected_page

    # Quick stats in sidebar
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.get("resume_score", 0) > 0:
        st.markdown("""
        <div style="border-top:1px solid #333;padding-top:1rem;margin-top:0.5rem;">
            <div style="color:#888;font-size:0.75rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.08em;margin-bottom:0.5rem;">Quick Stats</div>
        </div>
        """, unsafe_allow_html=True)

        rs = st.session_state.get("resume_score", 0)
        ats = st.session_state.get("ats_score", 0)
        skills_n = len(st.session_state.get("skills_found", []))
        st.markdown(f"""
        <div style="color:#ccc;font-size:0.85rem;line-height:1.9;">
            📄 Resume: <strong style="color:#0066FF;">{rs}/100</strong><br>
            🎯 ATS: <strong style="color:#0066FF;">{ats}/100</strong><br>
            🛠️ Skills: <strong style="color:#0066FF;">{skills_n}</strong>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="position:fixed;bottom:0;left:0;width:inherit;padding:1rem;
                border-top:2px solid #222;background:#000;">
        <div style="color:#555;font-size:0.72rem;line-height:1.5;">
            Built by <strong style="color:#0066FF;">Team Trident</strong><br>
            CareerPilot AI © 2024
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Home Page ──────────────────────────────────────────────────────────────────
def _show_home():
    # Hero
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">
            Career<span class="hero-accent">Pilot</span> AI
        </div>
        <div class="hero-subtitle">
            AI-powered platform helping students ace resumes, exams, and placements
        </div>
        <div style="margin-top:0.8rem;">
            <span class="tag tag-blue">Gemini AI</span>&nbsp;
            <span class="tag tag-black">Team Trident</span>&nbsp;
            <span class="tag" style="background:#FF9500;color:#fff;border:2px solid #000;">
                6 AI Modules
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA Buttons
    cta_col1, cta_col2, cta_col3 = st.columns([2, 2, 6])
    with cta_col1:
        if st.button("📄 Analyze My Resume →", key="home_to_resume"):
            st.session_state["nav_page"] = "📄 Resume Analyzer"
            st.rerun()
    with cta_col2:
        if st.button("📚 Generate Study Plan →", key="home_to_study"):
            st.session_state["nav_page"] = "📚 Study Planner"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature Cards
    st.markdown("### 🔧 Everything You Need to Land Your Dream Job")
    st.markdown("<br>", unsafe_allow_html=True)

    features = [
        ("📄", "AI Resume Analyzer",
         "Upload your resume and get ATS score, skill gap analysis, and personalised AI recommendations instantly."),
        ("📚", "Smart Study Planner",
         "Enter your exams and get a personalised daily and weekly study schedule tailored to your pace."),
        ("📊", "Career Dashboard",
         "Track your resume score, skill coverage, and overall career readiness in one unified view."),
        ("🎯", "Career Roadmap",
         "Get a month-by-month action plan with courses, projects, and certifications for your target role."),
        ("🎤", "Interview Coach",
         "Practice with AI-generated role-specific questions and receive detailed scored feedback instantly."),
        ("📥", "Reports & History",
         "Download professional PDF reports for all your analyses and track progress over time."),
    ]

    for i in range(0, len(features), 2):
        col1, col2 = st.columns(2)
        for col, (icon, title, desc) in zip([col1, col2], features[i:i+2]):
            with col:
                st.markdown(f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Stats Row
    st.markdown("---")
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("6", "AI Modules"),
        ("100%", "Free to Use"),
        ("Instant", "AI Analysis"),
        ("PDF", "Download Reports"),
    ]
    for col, (val, label) in zip([s1, s2, s3, s4], stats):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="app-footer">
        Built with ❤️ by <strong>Team Trident</strong> | CareerPilot AI
    </div>
    """, unsafe_allow_html=True)


def _show_about():
    st.markdown("""
    <h1 style='font-size:2.4rem;font-weight:800;'>ℹ️ About CareerPilot AI</h1>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="brut-card" style="box-shadow:8px 8px 0px #0066FF;border-color:#0066FF;margin-bottom:1.5rem;">
        <h2 style="font-size:1.6rem;font-weight:800;margin-bottom:0.5rem;">The Project</h2>
        <p style="font-size:1.05rem;line-height:1.7;color:#333;">
            CareerPilot AI is a comprehensive career and academic success platform designed specifically
            for students entering the job market. Using the power of Google's Gemini AI, it provides
            instant, personalised feedback on resumes, generates smart study schedules, creates detailed
            career roadmaps, and coaches candidates through mock interview sessions — all in one place.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Modules
    st.markdown("### 🔧 Platform Modules")
    modules = [
        ("📄", "AI Resume Analyzer", "Upload PDF resume → ATS score, skill gap analysis, AI recommendations"),
        ("📚", "Smart Study Planner", "Enter subjects & exams → personalised daily + weekly AI study schedule"),
        ("📊", "Career Dashboard", "Real-time metrics, charts, skill coverage, and analysis history"),
        ("🎯", "Career Roadmap", "Month-by-month roadmap with skills, projects, courses, and certifications"),
        ("🎤", "Interview Coach", "AI-generated Q&A sessions with scored feedback and model answers"),
        ("📥", "Reports & History", "Full PDF download for all analyses, plans, roadmaps, and sessions"),
    ]
    for icon, title, desc in modules:
        st.markdown(f"""
        <div style="display:flex;gap:1rem;align-items:flex-start;padding:0.8rem 1rem;
                    border:2px solid #000;margin-bottom:0.5rem;background:#fff;">
            <span style="font-size:1.5rem;">{icon}</span>
            <div>
                <strong style="font-size:1rem;">{title}</strong><br>
                <span style="font-size:0.9rem;color:#555;">{desc}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Tech Stack
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🛠️ Technology Stack")
    stack = [
        ("⚡", "Streamlit", "Python web framework"),
        ("🤖", "Google Gemini 1.5 Flash", "AI backbone for all analysis"),
        ("📄", "PyPDF2", "PDF text extraction"),
        ("📑", "ReportLab", "Professional PDF generation"),
        ("📊", "Plotly", "Interactive charts and visualisations"),
        ("🐼", "Pandas", "Data manipulation"),
        ("🗄️", "SQLite3", "Lightweight persistent storage"),
        ("🎨", "Space Grotesk", "Modern brutalism typography"),
    ]
    tech_col1, tech_col2 = st.columns(2)
    for i, (icon, name, desc) in enumerate(stack):
        with (tech_col1 if i % 2 == 0 else tech_col2):
            st.markdown(f"""
            <div style="display:flex;gap:0.8rem;align-items:center;padding:0.6rem 0.8rem;
                        border:2px solid #000;margin-bottom:0.4rem;background:#F0F4FF;">
                <span style="font-size:1.3rem;">{icon}</span>
                <div>
                    <strong style="font-size:0.9rem;">{name}</strong><br>
                    <span style="font-size:0.8rem;color:#555;">{desc}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Team
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="brut-card" style="background:#000;color:#fff;text-align:center;padding:2rem;
                                   box-shadow:8px 8px 0px #0066FF;">
        <div style="font-size:0.85rem;color:#0066FF;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.1em;">Built By</div>
        <div style="font-size:2.5rem;font-weight:800;margin:0.5rem 0;">Team Trident</div>
        <div style="color:#888;font-size:0.95rem;">
            CareerPilot AI — Empowering the next generation of professionals
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Fix: move home/about to top before router ──────────────────────────────────
# (Python functions must be defined before use — restructure call order)
# Re-route after definitions:
page = st.session_state.get("nav_page", "🏠 Home")

if page == "🏠 Home":
    _show_home()
elif page == "📄 Resume Analyzer":
    show_resume_analyzer()
elif page == "📚 Study Planner":
    show_study_planner()
elif page == "📊 Career Dashboard":
    show_career_dashboard()
elif page == "🎯 Career Roadmap":
    show_roadmap_generator()
elif page == "🎤 Interview Coach":
    show_interview_coach()
elif page == "📥 Reports":
    show_reports()
elif page == "ℹ️ About":
    _show_about()