"""
AI Student Placement Prediction System
----------------------------------------
Main entry point. Loads a trained RandomForestClassifier and predicts a
student's placement chances from CGPA, Projects, Internships, DSA and
Communication scores. Also renders profile analytics, recommendations
and an improvement plan.
"""

import pickle
from pathlib import Path

import pandas as pd
import streamlit as st

import db
import auth
import theme

# ----------------------------------------------------------------------
# Page config (must be the first Streamlit command)
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="AI Placement Prediction System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()
auth.init_session()

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
MODEL_PATH = BASE_DIR / "placement_model.pkl"

LOGO_PATH = ASSETS_DIR / "logo.png"
BANNER_PATH = ASSETS_DIR / "banner.jpg"
SIDEBAR_BOTTOM_PATH = ASSETS_DIR / "sidebar-bottom.png"

FEATURE_COLUMNS = ["CGPA", "Projects", "Internships", "DSA", "Communication"]

# ----------------------------------------------------------------------
# Small hand-authored line-icon set (24x24, stroke-based) used throughout
# the UI instead of emoji, for a cleaner SaaS look.
# ----------------------------------------------------------------------
ICONS = {
    "person": '<path d="M12 13a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"/><path d="M4 20c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5"/>',
    "cgpa": '<polyline points="3,17 9,11 13,15 21,7"/><polyline points="15,7 21,7 21,13"/>',
    "folder": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    "code": '<polyline points="8,6 2,12 8,18"/><polyline points="16,6 22,12 16,18"/>',
    "chat": '<path d="M21 11.5a8.38 8.38 0 0 1-8.5 8.5 8.5 8.5 0 0 1-4-1L3 20l1.2-4.3A8.4 8.4 0 0 1 3.5 11.5 8.5 8.5 0 1 1 21 11.5z"/>',
    "rocket": '<path d="M12 2c3 2 5 6 5 10 0 3-2 5-5 7-3-2-5-4-5-7 0-4 2-8 5-10z"/><circle cx="12" cy="9" r="1.5"/><path d="M8.5 15.5 6 18M15.5 15.5 18 18"/>',
    "star": '<polygon points="12,2 15,9 22,9.5 17,14.5 18.5,22 12,18 5.5,22 7,14.5 2,9.5 9,9"/>',
    "moon": '<path d="M21 12.5A9 9 0 1 1 11.5 3a7 7 0 0 0 9.5 9.5z"/>',
    "cap": '<path d="M12 3 2 8l10 5 10-5-10-5z"/><path d="M6 10.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-5.5"/><path d="M22 8v6"/>',
    "check": '<polyline points="20,6 9,17 4,12"/>',
}


def svg(name: str, size: int = 16) -> str:
    inner = ICONS.get(name, "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )


def field_label(icon_name: str, text: str):
    st.markdown(
        f'<div class="field-label">{svg(icon_name, 16)}<span>{text}</span></div>',
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def load_css():
    css_path = BASE_DIR / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def image_exists(path: Path) -> bool:
    """Check an image file exists and looks like a real, non-empty file."""
    try:
        return path.exists() and path.is_file() and path.stat().st_size > 0
    except Exception:
        return False


@st.cache_resource(show_spinner=False)
def load_model():
    """Load the trained RandomForestClassifier. Returns None if unavailable."""
    try:
        if not MODEL_PATH.exists():
            return None
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


def compute_skill_score(cgpa, projects, internships, dsa, communication) -> float:
    """A separate, human-readable profile/skill score (0-100). NOT the ML output."""
    cgpa_pct = min(cgpa / 10, 1.0) * 100
    proj_pct = min(projects / 5, 1.0) * 100
    intern_pct = min(internships / 3, 1.0) * 100
    score = (
        cgpa_pct * 0.25
        + proj_pct * 0.15
        + intern_pct * 0.15
        + dsa * 0.25
        + communication * 0.20
    )
    return round(min(score, 100), 1)


def expected_package(skill_score: float, placement_prob: float):
    """A rough, dashboard-only estimate. Not a guaranteed salary figure."""
    combined = (skill_score * 0.5) + (placement_prob * 0.5)
    if combined >= 80:
        return "₹18 – 30 LPA", "🔥 Excellent", "tag-green"
    elif combined >= 62:
        return "₹9 – 16 LPA", "👍 Good", "tag-blue"
    elif combined >= 42:
        return "₹5 – 8 LPA", "📈 Needs Improvement", "tag-amber"
    else:
        return "₹3 – 5 LPA", "📈 Needs Improvement", "tag-red"


def ai_recommendation(skill_score: float) -> str:
    if skill_score >= 75:
        return "Your profile is strong. Focus on interview preparation and advanced projects."
    elif skill_score >= 50:
        return "Your profile is on the right track. Improve DSA, projects and communication skills."
    else:
        return "Focus on fundamentals, DSA, projects and communication."


def ai_improvement_plan(cgpa, dsa, projects, internships, communication):
    suggestions = []
    if cgpa < 8:
        suggestions.append(("📈", "Improve academic performance."))
    if dsa < 80:
        suggestions.append(("💻", "Practice arrays, strings, trees, graphs and coding problems."))
    if projects < 3:
        suggestions.append(("📁", "Build 2–3 strong real-world projects."))
    if internships < 2:
        suggestions.append(("💼", "Gain practical experience through internships."))
    if communication < 80:
        suggestions.append(("💬", "Practice communication and mock interviews."))

    if not suggestions:
        suggestions.append(("🏆", "Excellent! Your profile is placement ready."))
    return suggestions


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

        if st.button("Home", icon=":material/home:", use_container_width=True):
            st.switch_page("app.py")
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

        st.markdown(
            f"""
            <div class="sidebar-bottom-icons">
                <div class="topbar-icon">{svg("person", 16)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_hero():
    art_html = ""
    if image_exists(BANNER_PATH):
        import base64
        b64 = base64.b64encode(BANNER_PATH.read_bytes()).decode()
        art_html = f'<div class="hero-art-wrap"><img src="data:image/jpeg;base64,{b64}"/></div>'
    else:
        art_html = f'<div class="hero-art-fallback">{svg("cap", 56)}</div>'

    st.markdown(
        f"""
        <div class="hero-wrap">
            <div class="hero-inner">
                <div class="hero-text">
                    <span class="hero-eyebrow">Machine Learning · Career Analytics</span>
                    <div class="hero-title">{svg("cap", 40)} AI Student Placement Prediction System</div>
                    <p class="hero-sub">Predict Placement Chances using Machine Learning</p>
                </div>
                {art_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(text: str):
    st.markdown(
        f'<div class="section-heading"><span class="accent-bar"></span>{text}</div>',
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# App
# ----------------------------------------------------------------------
load_css()
theme.render_theme_toggle()
theme.apply_theme_css()
render_sidebar()
render_hero()

auth.require_student()

model = load_model()
if model is None:
    st.warning(
        "⚠️ The prediction model (`placement_model.pkl`) could not be loaded. "
        "Predictions are temporarily unavailable, but you can still explore the dashboard."
    )

# ---- Student Details form ----
st.markdown('<div class="ai-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">👤 Student Details</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    field_label("person", "Student Name")
    student_name = st.text_input(
        "Student Name",
        value=st.session_state.get("student_name", ""),
        placeholder="Enter student name",
        label_visibility="collapsed",
    )
with col2:
    field_label("cgpa", "CGPA")
    cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, value=7.5, step=0.1, label_visibility="collapsed")

col3, col4 = st.columns(2)
with col3:
    field_label("folder", "Projects")
    projects = st.number_input("Projects", min_value=0, max_value=20, value=3, step=1, label_visibility="collapsed")
with col4:
    field_label("briefcase", "Internships")
    internships = st.number_input("Internships", min_value=0, max_value=10, value=1, step=1, label_visibility="collapsed")

col5, col6 = st.columns(2)
with col5:
    field_label("code", "DSA Score")
    dsa_score = st.slider("DSA Score", min_value=0, max_value=100, value=65, label_visibility="collapsed")
with col6:
    field_label("chat", "Communication Score")
    communication_score = st.slider("Communication Score", min_value=0, max_value=100, value=70, label_visibility="collapsed")

st.markdown("</div>", unsafe_allow_html=True)

predict_clicked = st.button("Predict Placement", icon=":material/rocket_launch:", use_container_width=True)

# ----------------------------------------------------------------------
# Prediction flow
# ----------------------------------------------------------------------
if predict_clicked:
    if not student_name or not student_name.strip():
        st.error("Please enter the student's name before predicting.")
    elif model is None:
        st.error("Prediction model is unavailable. Please add `placement_model.pkl` to the project root.")
    else:
        input_df = pd.DataFrame(
            [[cgpa, projects, internships, dsa_score, communication_score]],
            columns=FEATURE_COLUMNS,
        )

        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1] * 100  # probability of class "1" (placed)

        skill_score = compute_skill_score(cgpa, projects, internships, dsa_score, communication_score)

        st.session_state["last_result"] = {
            "name": student_name,
            "prediction": int(prediction),
            "probability": round(probability, 1),
            "skill_score": skill_score,
            "cgpa": cgpa,
            "projects": projects,
            "internships": internships,
            "dsa": dsa_score,
            "communication": communication_score,
        }

        # Persist to the database (linked to the logged-in student) so the
        # Admin Panel's Prediction History and Dashboard stats are real,
        # not hardcoded — see db.log_prediction() / db.admin_dashboard_stats().
        db.log_prediction(
            student_id=st.session_state.get("student_id"),
            student_name=student_name,
            cgpa=cgpa,
            projects=projects,
            internships=internships,
            dsa_score=dsa_score,
            communication_score=communication_score,
            prediction=int(prediction),
            probability=round(probability, 1),
        )
        if st.session_state.get("student_id"):
            db.update_student_profile(
                st.session_state["student_id"],
                cgpa=cgpa,
                projects=projects,
                internships=internships,
                dsa_score=dsa_score,
                communication_score=communication_score,
            )

# ----------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------
result = st.session_state.get("last_result")

if result:
    section_heading("🎯 Prediction Result")

    if result["prediction"] == 1:
        st.markdown(
            f'<div class="result-banner result-high">🟢 High Placement Chance — {result["name"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="result-banner result-low">🔴 Low Placement Chance — {result["name"]}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("**Placement Probability**")
    st.progress(int(result["probability"]))
    st.caption(f"{result['probability']}% chance of placement, as estimated by the ML model.")

    st.markdown("**⭐ Overall Skill Score**")
    st.progress(int(result["skill_score"]))
    st.caption(f"{result['skill_score']} / 100 — a separate dashboard metric, not the ML prediction.")

    # ---- Result cards ----
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-icon">📈</div>
                <div class="metric-value">{result['probability']}%</div>
                <div class="metric-label">Placement Probability</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-icon">📁</div>
                <div class="metric-value">{result['projects']}</div>
                <div class="metric-label">Projects</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-icon">💼</div>
                <div class="metric-value">{result['internships']}</div>
                <div class="metric-label">Internships</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- Skill breakdown ----
    section_heading("📊 Skill Breakdown")
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    bcol1, bcol2 = st.columns(2)
    with bcol1:
        st.markdown("📈 CGPA")
        st.progress(int(min(result["cgpa"] / 10 * 100, 100)))
        st.markdown("💻 DSA Score")
        st.progress(int(result["dsa"]))
        st.markdown("💬 Communication")
        st.progress(int(result["communication"]))
    with bcol2:
        st.markdown("📁 Projects")
        st.progress(int(min(result["projects"] / 5 * 100, 100)))
        st.markdown("💼 Internships")
        st.progress(int(min(result["internships"] / 3 * 100, 100)))
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Expected package ----
    section_heading("💰 Expected Package")
    ctc, outlook_label, outlook_tag = expected_package(result["skill_score"], result["probability"])
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    ecol1, ecol2 = st.columns(2)
    with ecol1:
        st.markdown('<div class="card-subtle">Expected CTC</div>', unsafe_allow_html=True)
        st.markdown(f"### {ctc}")
    with ecol2:
        st.markdown('<div class="card-subtle">Career Outlook</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="tag {outlook_tag}">{outlook_label}</span>', unsafe_allow_html=True)
    st.caption("This is an estimated dashboard metric, not a guaranteed salary offer.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- AI recommendation ----
    section_heading("🤖 AI Recommendation")
    st.markdown(
        f'<div class="reco-box">{ai_recommendation(result["skill_score"])}</div>',
        unsafe_allow_html=True,
    )

    # ---- AI improvement plan ----
    section_heading("🚀 AI Improvement Plan")
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    plan = ai_improvement_plan(
        result["cgpa"], result["dsa"], result["projects"], result["internships"], result["communication"]
    )
    for icon, tip in plan:
        st.markdown(f'<div class="plan-item">{icon} &nbsp; {tip}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Fill in the student details above and click **🚀 Predict Placement** to see results.")
