"""AI Career Assistant — a rule-based chat fallback for placement/career questions."""

import os
import random
import re
from pathlib import Path

import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

db.init_db()
auth.init_session()

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"
SIDEBAR_BOTTOM_PATH = ASSETS_DIR / "sidebar-bottom.png"


def image_exists(path: Path) -> bool:
    try:
        return path.exists() and path.is_file() and path.stat().st_size > 0
    except Exception:
        return False


def load_css():
    css_path = BASE_DIR / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


ICONS = {
    "person": '<path d="M12 13a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"/><path d="M4 20c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5"/>',
    "cap": '<path d="M12 3 2 8l10 5 10-5-10-5z"/><path d="M6 10.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-5.5"/><path d="M22 8v6"/>',
    "check": '<polyline points="20,6 9,17 4,12"/>',
    "star": '<polygon points="12,2 15,9 22,9.5 17,14.5 18.5,22 12,18 5.5,22 7,14.5 2,9.5 9,9"/>',
    "moon": '<path d="M21 12.5A9 9 0 1 1 11.5 3a7 7 0 0 0 9.5 9.5z"/>',
}


def svg(name: str, size: int = 16) -> str:
    inner = ICONS.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )


def render_topbar():
    st.markdown('<div class="topbar">', unsafe_allow_html=True)
    tcol1, tcol2, tcol3 = st.columns([10, 1, 1])
    with tcol2:
        st.markdown(f'<div class="topbar-icon">{svg("moon", 18)}</div>', unsafe_allow_html=True)
    with tcol3:
        st.markdown('<div class="topbar-avatar">🧑</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">', unsafe_allow_html=True)
        if image_exists(LOGO_PATH):
            st.image(str(LOGO_PATH), width=56)
        else:
            st.markdown(f'<div class="sidebar-logo-fallback">{svg("cap", 26)}</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="brand-title">AI PLACEMENT<br/>PREDICTION SYSTEM</div>
            <div class="brand-version">{svg("check", 12)} VERSION 1.8</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.page_link("app.py", label="Home", icon=":material/home:")
        st.page_link("pages/1_Resume_Analyzer.py", label="Resume Analyzer", icon=":material/description:")
        st.page_link("pages/2_Job_Matcher.py", label="Job Matcher", icon=":material/work:")
        st.page_link("pages/3_Interview_Preparation.py", label="Interview Preparation", icon=":material/mic:")
        st.page_link("pages/4_Career_Roadmap.py", label="Career Roadmap", icon=":material/map:")
        st.page_link("pages/5_AI_Chatbot.py", label="AI Chatbot", icon=":material/smart_toy:")
        st.page_link("pages/6_Analytics.py", label="Analytics", icon=":material/bar_chart:")
        st.page_link("pages/9_Admin_Dashboard.py", label="Admin Dashboard", icon=":material/verified_user:")

        if auth.is_student_logged_in():
            name = st.session_state.get("student_name") or "Student"
            initials = "".join(w[0] for w in name.split()[:2]).upper() or "S"
            st.markdown(
                f"""
                <div class="sidebar-user-chip">
                    <div class="chip-avatar">{initials}</div>
                    <div>
                        <div class="chip-name">{name}</div>
                        <div class="chip-role">Student</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Logout", icon=":material/logout:", use_container_width=True, key="student_logout"):
                auth.logout()
                st.switch_page("pages/7_Login.py")
        else:
            st.page_link("pages/7_Login.py", label="Login", icon=":material/person:")

        cta_art = ""
        if image_exists(SIDEBAR_BOTTOM_PATH):
            import base64
            b64 = base64.b64encode(SIDEBAR_BOTTOM_PATH.read_bytes()).decode()
            cta_art = f'<img class="sidebar-cta-art" src="data:image/png;base64,{b64}"/>'

        st.markdown(
            f"""
            <div class="sidebar-cta">
                {cta_art}
                <div class="sidebar-cta-content">
                    <div class="cta-star">{svg("star", 18)}</div>
                    <div class="cta-title">AI-Powered Placement</div>
                    <div class="cta-sub">Predict. Prepare. Achieve.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        svg_person = svg("person", 16)
        st.markdown(
            f"""
            <div class="sidebar-bottom-icons">
                <div class="topbar-icon">{svg_person}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


load_css()
theme.render_theme_toggle()
theme.apply_theme_css()
render_sidebar()
auth.require_student()

st.markdown('<div class="section-heading"><span class="accent-bar"></span>🤖 AI Career Assistant</div>', unsafe_allow_html=True)
st.caption("Ask about placements, resumes, DSA, AI/ML, data science, interviews, career roadmap or projects.")

# ----------------------------------------------------------------------
# Rule-based fallback knowledge base (used when no external LLM API key
# is configured, so the chatbot never crashes and always responds).
# ----------------------------------------------------------------------
KNOWLEDGE_BASE = [
    (r"\b(placement|placed|hire|hiring)\b",
     ["Placements depend on a mix of academics, projects, DSA skills and communication. "
      "Use the Home page's Predict Placement tool to see your estimated chances and a tailored improvement plan."]),
    (r"\bresume\b",
     ["A strong resume highlights 2–3 solid projects, quantifies your impact, and lists relevant skills clearly. "
      "Try the Resume Analyzer page to get an ATS-style score and specific suggestions."]),
    (r"\b(dsa|data structures?|algorithms?)\b",
     ["For DSA, focus on arrays, strings, linked lists, trees, graphs and dynamic programming. "
      "Practice consistently on a platform of your choice, and revisit weak topics using the Interview Preparation page's DSA track."]),
    (r"\b(ai|ml|machine learning|deep learning)\b",
     ["Start with Python, statistics and core ML algorithms (regression, classification, clustering), then move into "
      "neural networks and specialized areas like NLP or computer vision. Check the Career Roadmap page for a full path."]),
    (r"\bdata science\b",
     ["Data Science combines statistics, SQL, Python and visualization to extract insights from data. "
      "The Career Roadmap page has a beginner-to-advanced path for Data Scientists."]),
    (r"\binterview\b",
     ["Interviews usually cover technical/DSA rounds, an HR round, and sometimes a behavioral round. "
      "Visit the Interview Preparation page to practice questions and try the mock interview scorer."]),
    (r"\b(career|roadmap|path)\b",
     ["Career roadmaps break a field into beginner, intermediate and advanced stages with projects and tools for each. "
      "See the Career Roadmap page to explore tracks like AI Engineer, Data Scientist and more."]),
    (r"\bproject(s)?\b",
     ["Projects should solve a real problem end-to-end — data collection, modeling or building, and deployment or a clear demo. "
      "2–3 well-documented projects are usually stronger than many shallow ones."]),
    (r"\b(hi|hello|hey)\b",
     ["Hi there! 👋 I can help with placements, resumes, DSA, AI/ML, data science, interviews, career roadmaps and projects. What would you like to know?"]),
]

FALLBACK_RESPONSES = [
    "I'm best at answering questions about placements, resumes, DSA, AI/ML, data science, interviews, career roadmaps and projects — could you rephrase your question around one of these?",
    "I don't have a specific answer for that yet, but I can help with placement prep, resumes, DSA, interviews, or career roadmaps. Try asking about one of those!",
]


def get_bot_response(user_message: str) -> str:
    """Rule-based responder. Safe fallback if no external LLM API is configured."""
    api_key_configured = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY"))

    if not api_key_configured:
        text = user_message.lower()
        for pattern, responses in KNOWLEDGE_BASE:
            if re.search(pattern, text):
                return random.choice(responses)
        return random.choice(FALLBACK_RESPONSES)

    # Placeholder for a real LLM-backed response if an API key is present.
    # Intentionally not calling an external API here — this keeps the app
    # self-contained and crash-safe without requiring live credentials.
    return random.choice(FALLBACK_RESPONSES)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hi! I'm your AI Career Assistant. Ask me about placements, resumes, DSA, AI/ML, interviews, or career roadmaps."}
    ]

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Ask about placements, resumes, DSA, interviews, career roadmap...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    try:
        reply = get_bot_response(user_input)
    except Exception:
        reply = "Sorry, something went wrong on my end — please try asking that again."

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)

st.markdown("<br/>", unsafe_allow_html=True)
if st.button("🗑️ Clear Conversation"):
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hi! I'm your AI Career Assistant. Ask me about placements, resumes, DSA, AI/ML, interviews, or career roadmaps."}
    ]
    st.rerun()
