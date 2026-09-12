"""Resume Analyzer — upload a PDF resume, extract text, and get ATS-style feedback."""

import re
from pathlib import Path

import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")

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

st.markdown('<div class="section-heading"><span class="accent-bar"></span>📄 Resume Analyzer</div>', unsafe_allow_html=True)
st.caption("Upload your resume as a PDF to get an ATS-style analysis of skills, gaps and recommendations.")

# Skill keyword bank used for lightweight keyword-based detection
SKILL_BANK = [
    "python", "java", "c++", "sql", "machine learning", "deep learning", "nlp",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "data structures",
    "algorithms", "aws", "azure", "docker", "kubernetes", "git", "react", "django",
    "flask", "power bi", "tableau", "excel", "communication", "leadership",
    "teamwork", "problem solving", "data analysis", "statistics", "html", "css",
    "javascript", "rest api", "linux", "agile",
]

CORE_SKILLS_FOR_TECH_ROLE = [
    "python", "sql", "machine learning", "data structures", "algorithms",
    "git", "communication", "problem solving",
]

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

st.markdown("<br/>", unsafe_allow_html=True)

if uploaded_file is None:
    st.info("👆 Upload a PDF resume above to run the analysis. No file uploaded yet.")
else:
    resume_text = ""
    try:
        import pypdf

        reader = pypdf.PdfReader(uploaded_file)
        for page in reader.pages:
            extracted = page.extract_text() or ""
            resume_text += extracted + "\n"
    except Exception:
        resume_text = ""

    if not resume_text.strip():
        st.warning(
            "⚠️ Could not extract readable text from this PDF (it may be a scanned image). "
            "Try uploading a text-based PDF resume."
        )
    else:
        text_lower = resume_text.lower()

        detected = sorted({s for s in SKILL_BANK if s in text_lower})
        missing = sorted(set(CORE_SKILLS_FOR_TECH_ROLE) - set(detected))

        word_count = len(re.findall(r"\w+", resume_text))
        has_email = bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text))
        has_phone = bool(re.search(r"(\+?\d[\d\-\s]{8,}\d)", resume_text))
        has_projects_section = "project" in text_lower
        has_education_section = "education" in text_lower or "degree" in text_lower or "cgpa" in text_lower

        # Simple ATS-style scoring heuristic
        score = 0
        score += min(len(detected) * 4, 40)
        score += 15 if has_email else 0
        score += 10 if has_phone else 0
        score += 15 if has_projects_section else 0
        score += 10 if has_education_section else 0
        score += 10 if 200 <= word_count <= 1200 else 5
        resume_score = min(score, 100)

        db.log_resume(
            student_id=st.session_state.get("student_id"),
            student_name=st.session_state.get("student_name") or "Unknown",
            resume_score=resume_score,
            detected_skills=detected,
            missing_skills=missing,
        )

        section_heading = '<div class="section-heading"><span class="accent-bar"></span>'
        st.markdown(section_heading + "📄 Resume Score</div>", unsafe_allow_html=True)
        st.markdown('<div class="ai-card">', unsafe_allow_html=True)
        st.progress(resume_score)
        st.markdown(f"### {resume_score} / 100")
        st.caption(f"Based on detected skills, contact details, structure and word count ({word_count} words).")
        st.markdown("</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(section_heading + "🧠 Skills Detected</div>", unsafe_allow_html=True)
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            if detected:
                st.markdown(
                    "".join(f'<span class="tag tag-green">{s}</span>' for s in detected),
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No known skill keywords were detected.")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(section_heading + "⚠️ Missing Skills</div>", unsafe_allow_html=True)
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            if missing:
                st.markdown(
                    "".join(f'<span class="tag tag-red">{s}</span>' for s in missing),
                    unsafe_allow_html=True,
                )
            else:
                st.caption("Great! Your resume covers all core placement-ready skills.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(section_heading + "💡 Recommendations</div>", unsafe_allow_html=True)
        st.markdown('<div class="ai-card">', unsafe_allow_html=True)
        tips = []
        if not has_email:
            tips.append("Add a professional email address near the top of your resume.")
        if not has_phone:
            tips.append("Include a contact phone number for recruiters to reach you.")
        if not has_projects_section:
            tips.append("Add a dedicated Projects section highlighting 2–3 strong builds.")
        if not has_education_section:
            tips.append("Clearly list your Education details, including CGPA.")
        if missing:
            tips.append(f"Strengthen these core skills: {', '.join(missing)}.")
        if word_count < 200:
            tips.append("Your resume looks too short — add more detail on projects and experience.")
        if word_count > 1200:
            tips.append("Your resume is quite long — trim it to 1–2 pages of the most relevant content.")
        if not tips:
            tips.append("🏆 Your resume looks placement-ready. Keep it updated with new projects.")

        for tip in tips:
            st.markdown(f'<div class="plan-item">💡 &nbsp; {tip}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
