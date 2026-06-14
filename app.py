"""
CareerPilot AI — Main Entry Point
AI-Powered Career & Academic Success Platform
Run: streamlit run app.py
"""

import os
import sys

# ── Ensure project root is always on sys.path ──────────────────────────────────
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

from requests.packages import target
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="CareerPilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "CareerPilot AI — AI-Powered Career & Academic Platform",
    },
)

# ── Load CSS ───────────────────────────────────────────────────────────────────
def _load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

def _load_fonts():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&display=swap"
          rel="stylesheet">
    """, unsafe_allow_html=True)

_load_fonts()
_load_css()

# ── Sidebar toggle CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
footer                             { visibility: hidden !important; }
[data-testid="stToolbar"]          { visibility: hidden !important; }
[data-testid="stDecoration"]       { display: none !important; }
[data-testid="stStatusWidget"]     { visibility: hidden !important; }
#MainMenu                          { visibility: hidden !important; }

header, [data-testid="stHeader"]   {
    visibility: visible !important;
    background: transparent !important;
    pointer-events: auto !important;
}

[data-testid="stExpandSidebarButton"],
[data-testid="stExpandSidebarButton"] button {
    visibility: visible !important;
    display: flex       !important;
    opacity: 1          !important;
    pointer-events: auto !important;
}
[data-testid="stExpandSidebarButton"] button {
    background: #0066FF  !important;
    border-radius: 6px   !important;
    padding: 6px         !important;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.5) !important;
}
[data-testid="stExpandSidebarButton"] button svg {
    fill: #fff   !important;
    color: #fff  !important;
    stroke: #fff !important;
}

[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] button {
    visibility: visible !important;
    display: flex       !important;
    opacity: 1          !important;
    pointer-events: auto !important;
}
</style>
""", unsafe_allow_html=True)

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
    "ai_provider": "BYOK",
    "byok_api_key": "",
    "ollama_model": "llama3",
    # i18n default
    "language": "en",
}
for key, val in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── i18n ───────────────────────────────────────────────────────────────────────
from i18n import t, LANGUAGES, get_language, set_language

# ── Import modules ─────────────────────────────────────────────────────────────
from modules.resume_analyzer import show_resume_analyzer
from modules.study_planner import show_study_planner
from modules.career_dashboard import show_career_dashboard
from modules.roadmap_generator import show_roadmap_generator
from modules.interview_coach import show_interview_coach
from modules.reports import show_reports
from services.ai_provider import (
    check_ollama_running,
    get_byok_api_key,
    OLLAMA_MODELS,
)

# ── Navigation options (always use English keys for routing) ───────────────────
# These are the internal routing values — we display translated labels separately.
NAV_KEYS = [
    "nav_home",
    "nav_resume",
    "nav_study",
    "nav_dashboard",
    "nav_roadmap",
    "nav_interview",
    "nav_reports",
    "nav_about",
]

# English strings are used as routing values to keep routing language-agnostic.
NAV_ROUTES = [
    "🏠 Home",
    "📄 Resume Analyzer",
    "📚 Study Planner",
    "📊 Career Dashboard",
    "🎯 Career Roadmap",
    "🎤 Interview Coach",
    "📥 Reports",
    "ℹ️ About",
]

def _nav_labels():
    """Return translated navigation labels in the same order as NAV_ROUTES."""
    return [t(k) for k in NAV_KEYS]


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo / Branding
    st.markdown(f"""
    <div style="padding:1rem 0;border-bottom:2px solid #0066FF;margin-bottom:1rem;">
        <div style="font-size:1.6rem;font-weight:800;color:#fff;letter-spacing:-0.02em;">
            🚀 CareerPilot <span style="color:#0066FF;">AI</span>
        </div>
        <div style="font-size:0.75rem;color:#888;margin-top:0.2rem;font-weight:500;">
            {t("app_tagline")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── AI Settings Section ────────────────────────────────────────────────────
    st.markdown(f"## {t('ai_settings')}")

    provider = st.selectbox(
        t("ai_provider"),
        ["BYOK", "Ollama (Local)"],
        index=0 if st.session_state["ai_provider"] == "BYOK" else 1,
        key="ai_provider_select",
    )
    st.session_state["ai_provider"] = provider

    if provider == "BYOK":
        user_key = st.text_input(
            t("enter_gemini_key"),
            value=st.session_state.get("byok_api_key", ""),
            type="password",
            placeholder="AIza...",
            key="byok_key_input",
        )
        st.session_state["byok_api_key"] = user_key

        effective_key = get_byok_api_key()
        if effective_key:
            st.markdown(f"""
            <div style="background:#00A651;color:#fff;padding:0.4rem 0.8rem;
                        font-size:0.8rem;font-weight:700;border:2px solid #fff;margin-bottom:0.5rem;">
                {t("byok_connected")}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#FF9500;color:#fff;padding:0.4rem 0.8rem;
                        font-size:0.8rem;font-weight:700;border:2px solid #fff;margin-bottom:0.5rem;">
                {t("enter_key_warning")}
            </div>
            """, unsafe_allow_html=True)
            st.warning(t("paste_key_warning"))

    else:  # Ollama (Local)
        selected_model = st.selectbox(
            t("ollama_model"),
            OLLAMA_MODELS,
            index=OLLAMA_MODELS.index(st.session_state.get("ollama_model", "llama3")),
            key="ollama_model_select",
        )
        st.session_state["ollama_model"] = selected_model

        if check_ollama_running():
            st.markdown(f"""
            <div style="background:#00A651;color:#fff;padding:0.4rem 0.8rem;
                        font-size:0.8rem;font-weight:700;border:2px solid #fff;margin-bottom:0.5rem;">
                {t("ollama_connected")}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#FF4444;color:#fff;padding:0.4rem 0.8rem;
                        font-size:0.8rem;font-weight:700;border:2px solid #fff;margin-bottom:0.5rem;">
                {t("ollama_not_running")}
            </div>
            """, unsafe_allow_html=True)
            st.warning(t("ollama_start_hint"))

    st.markdown("<hr style='border-color:#333;margin:1rem 0;'>", unsafe_allow_html=True)

    # ── Navigation ─────────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='color:#888;font-size:0.75rem;font-weight:700;text-transform:uppercase;"
        f"letter-spacing:0.08em;margin-bottom:0.5rem;'>{t('navigation')}</div>",
        unsafe_allow_html=True,
    )

    nav_labels = _nav_labels()
    current_route = st.session_state.get("nav_page", "🏠 Home")
    # Map current route → translated label for the radio default
    try:
        current_idx = NAV_ROUTES.index(current_route)
    except ValueError:
        current_idx = 0

    selected_label = st.radio(
        t("navigation"),
        nav_labels,
        index=current_idx,
        label_visibility="collapsed",
        key="sidebar_nav",
    )
    # Map translated label back → routing key
    try:
        selected_route = NAV_ROUTES[nav_labels.index(selected_label)]
    except (ValueError, IndexError):
        selected_route = "🏠 Home"
    st.session_state["nav_page"] = selected_route

    # ── Quick stats ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.session_state.get("resume_score", 0) > 0:
        st.markdown(f"""
        <div style="border-top:1px solid #333;padding-top:1rem;margin-top:0.5rem;">
            <div style="color:#888;font-size:0.75rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.08em;margin-bottom:0.5rem;">{t("quick_stats")}</div>
        </div>
        """, unsafe_allow_html=True)

        rs = st.session_state.get("resume_score", 0)
        ats = st.session_state.get("ats_score", 0)
        skills_n = len(st.session_state.get("skills_found", []))
        st.markdown(f"""
        <div style="color:#ccc;font-size:0.85rem;line-height:1.9;">
            📄 {t("dash_resume_score")}: <strong style="color:#0066FF;">{rs}/100</strong><br>
            🎯 {t("dash_ats_score")}: <strong style="color:#0066FF;">{ats}/100</strong><br>
            🛠️ {t("dash_skills_found")}: <strong style="color:#0066FF;">{skills_n}</strong>
        </div>
        """, unsafe_allow_html=True)

    # ── Language selector (below About / quick stats) ──────────────────────────
    st.markdown("<hr style='border-color:#333;margin:1rem 0;'>", unsafe_allow_html=True)
    lang_names = list(LANGUAGES.keys())
    lang_codes = list(LANGUAGES.values())
    current_lang_code = get_language()
    try:
        current_lang_idx = lang_codes.index(current_lang_code)
    except ValueError:
        current_lang_idx = 0

    selected_lang_name = st.selectbox(
        t("language_selector_label"),
        lang_names,
        index=current_lang_idx,
        key="language_select",
    )
    new_lang_code = LANGUAGES[selected_lang_name]
    if new_lang_code != current_lang_code:
        set_language(new_lang_code)
        st.rerun()

    # ── Sidebar footer ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="position:fixed;bottom:0;left:0;width:inherit;padding:1rem;
                border-top:2px solid #222;background:#000;">
        <div style="color:#555;font-size:0.72rem;line-height:1.5;">
            CareerPilot AI Platform<br>
            © 2024 CareerPilot AI
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Home Page ──────────────────────────────────────────────────────────────────
def _show_home():
    # Hero
    st.markdown(f"""
    <div class="hero-section">
        <div class="hero-title">
            Career<span class="hero-accent">Pilot</span> AI
        </div>
        <div class="hero-subtitle">
            {t("home_hero_subtitle")}
        </div>
        <div style="margin-top:0.8rem;">
            <span class="tag tag-blue">Gemini AI</span>&nbsp;
            <span class="tag tag-black">BYOK + Ollama</span>&nbsp;
            <span class="tag" style="background:#FF9500;color:#fff;border:2px solid #000;">
                6 AI {t("home_stat_modules")}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    def _nav_to(target_route: str):
        st.session_state["sidebar_nav"] = target_route
        st.session_state["nav_page"] = target_route

    # CTA Buttons
    cta_col1, cta_col2, cta_col3 = st.columns([2, 2, 6])
    with cta_col1:
        st.button(t("home_cta_resume"), key="home_to_resume",
                  on_click=_nav_to, args=("📄 Resume Analyzer",))
    with cta_col2:
        st.button(t("home_cta_study"), key="home_to_study",
                  on_click=_nav_to, args=("📚 Study Planner",))

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature Cards
    st.markdown(f"### {t('home_features_heading')}")
    st.markdown("<br>", unsafe_allow_html=True)

    features = [
        ("📄", t("feat_resume_title"), "📄 Resume Analyzer",  t("feat_resume_desc")),
        ("📚", t("feat_study_title"),  "📚 Study Planner",    t("feat_study_desc")),
        ("📊", t("feat_dashboard_title"), "📊 Career Dashboard", t("feat_dashboard_desc")),
        ("🎯", t("feat_roadmap_title"), "🎯 Career Roadmap",  t("feat_roadmap_desc")),
        ("🎤", t("feat_interview_title"), "🎤 Interview Coach", t("feat_interview_desc")),
        ("📥", t("feat_reports_title"), "📥 Reports",         t("feat_reports_desc")),
    ]

    for i in range(0, len(features), 2):
        col1, col2 = st.columns(2)
        for col, (icon, title, nav_target, desc) in zip([col1, col2], features[i:i+2]):
            with col:
                st.markdown(f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
                st.button(
                    f"{t('home_open')} {title} {t('home_open_arrow')}",
                    key=f"card_{nav_target}",
                    on_click=_nav_to,
                    args=(nav_target,),
                )
        st.markdown("<br>", unsafe_allow_html=True)

    # Stats Row
    st.markdown("---")
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("6",        t("home_stat_modules")),
        ("100%",     t("home_stat_free")),
        (t("home_stat_instant"), t("home_stat_instant_label")),
        (t("home_stat_pdf"),     t("home_stat_pdf_label")),
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
    st.markdown(f"""
    <div class="app-footer">
        {t("home_footer")}
    </div>
    """, unsafe_allow_html=True)


def _show_about():
    st.markdown(f"""
    <h1 style='font-size:2.4rem;font-weight:800;'>{t("about_title")}</h1>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="brut-card" style="box-shadow:8px 8px 0px #0066FF;border-color:#0066FF;margin-bottom:1.5rem;">
        <h2 style="font-size:1.6rem;font-weight:800;margin-bottom:0.5rem;">{t("about_project_heading")}</h2>
        <p style="font-size:1.05rem;line-height:1.7;color:#333;">
            {t("about_project_body")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # AI Providers
    st.markdown(f"### {t('about_ai_providers')}")
    st.markdown(f"""
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem;">
        <div style="flex:1;min-width:200px;border:2px solid #0066FF;padding:1rem;background:#F0F4FF;">
            <strong>{t("about_byok_title")}</strong><br>
            <span style="font-size:0.9rem;color:#555;">{t("about_byok_desc")}</span>
        </div>
        <div style="flex:1;min-width:200px;border:2px solid #00A651;padding:1rem;background:#F0FFF4;">
            <strong>{t("about_ollama_title")}</strong><br>
            <span style="font-size:0.9rem;color:#555;">{t("about_ollama_desc")}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Modules
    st.markdown(f"### {t('about_modules_heading')}")
    modules = [
        ("📄", t("feat_resume_title"),   t("about_mod_resume_desc")),
        ("📚", t("feat_study_title"),    t("about_mod_study_desc")),
        ("📊", t("feat_dashboard_title"),t("about_mod_dashboard_desc")),
        ("🎯", t("feat_roadmap_title"),  t("about_mod_roadmap_desc")),
        ("🎤", t("feat_interview_title"),t("about_mod_interview_desc")),
        ("📥", t("feat_reports_title"),  t("about_mod_reports_desc")),
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
    st.markdown(f"### {t('about_tech_heading')}")
    stack = [
        ("⚡", "Streamlit",               t("tech_streamlit_desc")),
        ("🤖", "Google Gemini 1.5 Flash", t("tech_gemini_desc")),
        ("🦙", "Ollama",                  t("tech_ollama_desc")),
        ("📄", "PyPDF2",                  t("tech_pypdf2_desc")),
        ("📑", "ReportLab",               t("tech_reportlab_desc")),
        ("📊", "Plotly",                  t("tech_plotly_desc")),
        ("🐼", "Pandas",                  t("tech_pandas_desc")),
        ("🗄️", "SQLite3",                 t("tech_sqlite_desc")),
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

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="brut-card" style="background:#000;color:#fff;text-align:center;padding:2rem;
                                   box-shadow:8px 8px 0px #0066FF;">
        <div style="font-size:0.85rem;color:#0066FF;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.1em;">{t("about_platform_label")}</div>
        <div style="font-size:2.5rem;font-weight:800;margin:0.5rem 0;">CareerPilot AI</div>
        <div style="color:#888;font-size:0.95rem;">
            {t("about_empowering")}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Router ─────────────────────────────────────────────────────────────────────
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
