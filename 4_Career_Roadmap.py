"""Career Roadmap — stage-by-stage learning paths for popular tech careers."""

from pathlib import Path

import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Career Roadmap", page_icon="🗺️", layout="wide")

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

st.markdown('<div class="section-heading"><span class="accent-bar"></span>🗺️ Career Roadmap</div>', unsafe_allow_html=True)
st.caption("Pick a career track to see a structured beginner-to-advanced learning path.")

ROADMAPS = {
    "AI Engineer": {
        "Beginner": ["Python fundamentals", "Math for ML (linear algebra, probability)", "Data structures basics"],
        "Intermediate": ["Supervised & unsupervised learning", "Neural networks", "Model evaluation & tuning"],
        "Advanced": ["Transformers & LLMs", "MLOps & model deployment", "Distributed training"],
        "Projects": ["Image classifier", "Chatbot with an LLM API", "End-to-end ML pipeline"],
        "Tools": ["Python", "PyTorch / TensorFlow", "Docker", "MLflow"],
        "Skills": ["Problem solving", "Statistics", "Experiment design"],
        "Interview Prep": ["ML fundamentals", "System design for ML", "Coding rounds (DSA)"],
    },
    "Data Scientist": {
        "Beginner": ["Statistics & probability", "SQL basics", "Python for data analysis"],
        "Intermediate": ["Exploratory data analysis", "Feature engineering", "Regression & classification models"],
        "Advanced": ["A/B testing & experimentation", "Time series forecasting", "Advanced visualization storytelling"],
        "Projects": ["Sales forecasting dashboard", "Customer churn model", "A/B test analysis report"],
        "Tools": ["Python / R", "SQL", "Tableau / Power BI", "Pandas"],
        "Skills": ["Statistical reasoning", "Business communication", "Data storytelling"],
        "Interview Prep": ["Case studies", "SQL queries", "Statistics questions"],
    },
    "Machine Learning Engineer": {
        "Beginner": ["Python & software engineering basics", "Data structures & algorithms", "Linear algebra"],
        "Intermediate": ["ML model training pipelines", "Feature stores & data pipelines", "Model serving APIs"],
        "Advanced": ["Scalable ML infrastructure", "CI/CD for ML", "Monitoring & drift detection"],
        "Projects": ["Deploy a model as a REST API", "Build a feature pipeline", "Automate retraining workflow"],
        "Tools": ["Docker", "Kubernetes", "FastAPI", "Airflow"],
        "Skills": ["Software engineering", "System design", "Debugging production issues"],
        "Interview Prep": ["System design", "Coding rounds", "ML fundamentals"],
    },
    "Data Analyst": {
        "Beginner": ["Excel & spreadsheets", "SQL basics", "Data visualization fundamentals"],
        "Intermediate": ["Dashboarding (Power BI/Tableau)", "Statistical analysis", "Python/R for analysis"],
        "Advanced": ["Advanced SQL & query optimization", "Predictive analytics basics", "Stakeholder reporting"],
        "Projects": ["Sales performance dashboard", "Customer segmentation analysis", "KPI tracking report"],
        "Tools": ["SQL", "Excel", "Power BI / Tableau", "Python"],
        "Skills": ["Attention to detail", "Business acumen", "Communication"],
        "Interview Prep": ["SQL queries", "Case studies", "Dashboard walkthroughs"],
    },
    "GenAI Engineer": {
        "Beginner": ["Python fundamentals", "NLP basics", "APIs & prompt basics"],
        "Intermediate": ["Prompt engineering", "Retrieval-augmented generation (RAG)", "Vector databases"],
        "Advanced": ["Fine-tuning LLMs", "Agentic workflows", "LLM evaluation & guardrails"],
        "Projects": ["RAG-based Q&A app", "AI agent with tool use", "Custom chatbot with memory"],
        "Tools": ["Python", "LangChain / LlamaIndex", "Vector DB (e.g. FAISS)", "LLM APIs"],
        "Skills": ["Prompt design", "System integration", "Evaluation design"],
        "Interview Prep": ["LLM concepts", "System design for GenAI apps", "Coding rounds"],
    },
}

selected_role = st.selectbox("Select a career track", options=list(ROADMAPS.keys()))
roadmap = ROADMAPS[selected_role]

stage_icons = {
    "Beginner": "🟢",
    "Intermediate": "🟡",
    "Advanced": "🔴",
    "Projects": "📁",
    "Tools": "🛠️",
    "Skills": "🧠",
    "Interview Prep": "🎤",
}

st.markdown('<div class="ai-card">', unsafe_allow_html=True)
st.markdown(f'<div class="card-title">{stage_icons["Beginner"]} Learning Progress — {selected_role}</div>', unsafe_allow_html=True)

progress_col1, progress_col2, progress_col3 = st.columns(3)
with progress_col1:
    st.markdown("**Beginner**")
    st.progress(100)
with progress_col2:
    st.markdown("**Intermediate**")
    st.progress(60)
with progress_col3:
    st.markdown("**Advanced**")
    st.progress(25)
st.caption("Progress shown is illustrative — track your own milestones as you complete each stage.")
st.markdown("</div>", unsafe_allow_html=True)

for stage in ["Beginner", "Intermediate", "Advanced", "Projects", "Tools", "Skills", "Interview Prep"]:
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">{stage_icons[stage]} {stage}</div>', unsafe_allow_html=True)
    for item in roadmap[stage]:
        st.markdown(f'<div class="plan-item">✅ &nbsp; {item}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
