"""Job Matcher — match a student's profile against common tech job roles."""

from pathlib import Path

import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Job Matcher", page_icon="💼", layout="wide")

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

st.markdown('<div class="section-heading"><span class="accent-bar"></span>💼 Job Matcher</div>', unsafe_allow_html=True)
st.caption("Enter your profile to see which roles fit best, and what to work on for each.")

ROLE_REQUIREMENTS = {
    "AI Engineer": ["python", "machine learning", "deep learning", "nlp", "sql"],
    "Data Scientist": ["python", "statistics", "machine learning", "sql", "data analysis"],
    "ML Engineer": ["python", "machine learning", "deep learning", "git", "sql"],
    "Data Analyst": ["sql", "excel", "data analysis", "statistics", "python"],
    "Python Developer": ["python", "sql", "git", "rest api", "problem solving"],
    "GenAI Engineer": ["python", "machine learning", "nlp", "deep learning", "rest api"],
    "Software Developer": ["python", "java", "git", "data structures", "algorithms"],
}

ALL_SKILLS = sorted({s for reqs in ROLE_REQUIREMENTS.values() for s in reqs} | {
    "communication", "leadership", "teamwork", "aws", "docker",
})

st.markdown('<div class="ai-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">👤 Your Profile</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    student_skills = st.multiselect("Your Skills", options=ALL_SKILLS, default=["python", "sql", "git"])
with col2:
    preferred_role = st.selectbox("Preferred Role", options=["Any"] + list(ROLE_REQUIREMENTS.keys()))

col3, col4 = st.columns(2)
with col3:
    experience_years = st.number_input("Experience (years)", min_value=0.0, max_value=20.0, value=0.5, step=0.5)
with col4:
    projects_done = st.number_input("Projects", min_value=0, max_value=20, value=3, step=1)

internship_done = st.checkbox("I have completed at least one internship")
resume_uploaded_note = st.text_area(
    "Resume Highlights (optional)",
    placeholder="Paste a short summary of your resume — e.g. key projects, tools used.",
    height=80,
)

st.markdown("</div>", unsafe_allow_html=True)

match_clicked = st.button("🔍 Find Matching Jobs", use_container_width=True)

if match_clicked:
    student_skill_set = set(student_skills)

    roles_to_check = (
        list(ROLE_REQUIREMENTS.keys()) if preferred_role == "Any" else [preferred_role]
    )

    rows = []
    for role in roles_to_check:
        required = set(ROLE_REQUIREMENTS[role])
        matched = required & student_skill_set
        missing = required - student_skill_set
        base_score = (len(matched) / len(required)) * 100 if required else 0
        bonus = min(experience_years * 3, 12) + min(projects_done * 1.5, 10) + (6 if internship_done else 0)
        match_score = round(min(base_score * 0.75 + bonus, 100), 1)
        rows.append(
            {
                "role": role,
                "match_score": match_score,
                "required": sorted(required),
                "missing": sorted(missing),
            }
        )

    rows.sort(key=lambda r: r["match_score"], reverse=True)

    st.markdown('<div class="section-heading"><span class="accent-bar"></span>🎯 Matching Roles</div>', unsafe_allow_html=True)

    for r in rows:
        st.markdown('<div class="ai-card">', unsafe_allow_html=True)
        top_col1, top_col2 = st.columns([3, 1])
        with top_col1:
            st.markdown(f"#### {r['role']}")
        with top_col2:
            st.markdown(f"**Match Score:** {r['match_score']}%")
        st.progress(int(r["match_score"]))

        rcol1, rcol2 = st.columns(2)
        with rcol1:
            st.markdown("**Required Skills**")
            st.markdown(
                "".join(f'<span class="tag tag-blue">{s}</span>' for s in r["required"]) or "—",
                unsafe_allow_html=True,
            )
        with rcol2:
            st.markdown("**Missing Skills**")
            if r["missing"]:
                st.markdown(
                    "".join(f'<span class="tag tag-red">{s}</span>' for s in r["missing"]),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown('<span class="tag tag-green">None — fully matched!</span>', unsafe_allow_html=True)

        if r["missing"]:
            st.caption("💡 Preparation suggestion: " + f"Build a small project or take a short course covering {', '.join(r['missing'][:3])}.")
        else:
            st.caption("💡 Preparation suggestion: You're well aligned — focus on interview prep for this role.")

        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Fill in your profile above and click **🔍 Find Matching Jobs** to see recommended roles.")
