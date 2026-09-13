"""Interview Preparation — question banks, tips, and a simple mock interview scorer."""

import random
from pathlib import Path

import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Interview Preparation", page_icon="🎤", layout="wide")

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

st.markdown('<div class="section-heading"><span class="accent-bar"></span>🎤 Interview Preparation</div>', unsafe_allow_html=True)
st.caption("Practice across five interview tracks, with tips and a mock scoring tool.")

QUESTION_BANK = {
    "Technical Interview": {
        "tip": "Structure answers with a brief definition, a real example, and trade-offs.",
        "questions": [
            ("Explain the difference between REST and GraphQL APIs.",
             "REST exposes fixed endpoints per resource; GraphQL lets clients request exactly the fields they need in one query, reducing over-fetching."),
            ("What is the difference between SQL and NoSQL databases?",
             "SQL databases are relational with fixed schemas and strong consistency; NoSQL databases are schema-flexible and optimized for scale and varied data shapes."),
            ("How does version control with Git help in team projects?",
             "Git tracks changes, enables branching for parallel work, and supports merging, code review and rollback, which keeps collaborative codebases stable."),
            ("What is the difference between a process and a thread?",
             "A process is an independent program with its own memory space; threads are lightweight units within a process that share memory but run concurrently."),
        ],
    },
    "HR Interview": {
        "tip": "Keep answers honest, specific and tied to real experiences — avoid generic statements.",
        "questions": [
            ("Tell me about yourself.",
             "Give a concise summary: background, key skills, one achievement, and why you're interested in this role."),
            ("Why do you want to work with our company?",
             "Connect the company's mission or products to your own goals and skills, showing you've done research."),
            ("What are your strengths and weaknesses?",
             "Pick a genuine strength relevant to the role, and a real weakness paired with how you're actively improving it."),
            ("Where do you see yourself in five years?",
             "Describe realistic growth — deepening technical skills, taking on more ownership — tied to the company's career path."),
        ],
    },
    "Behavioral Interview": {
        "tip": "Use the STAR method: Situation, Task, Action, Result.",
        "questions": [
            ("Describe a time you faced a conflict in a team project.",
             "Explain the situation briefly, what you personally did to resolve it, and the positive outcome for the team."),
            ("Tell me about a time you failed and what you learned.",
             "Own the failure honestly, focus on the concrete lesson learned, and how you applied it afterward."),
            ("Describe a situation where you had to learn something quickly.",
             "Highlight your learning process — resources used, how you applied it under time pressure, and the result."),
            ("Give an example of when you took initiative.",
             "Describe a problem you noticed, the action you proactively took, and the impact it had."),
        ],
    },
    "DSA Interview": {
        "tip": "Think aloud: clarify constraints, discuss brute force first, then optimize.",
        "questions": [
            ("How would you find duplicate elements in an array efficiently?",
             "Use a hash set to track seen elements in a single pass — O(n) time, O(n) space, versus O(n²) for the naive nested-loop approach."),
            ("Explain the difference between BFS and DFS traversal.",
             "BFS explores level by level using a queue and finds shortest paths in unweighted graphs; DFS explores depth-first using a stack or recursion."),
            ("What is the time complexity of quicksort and when does it degrade?",
             "Average case is O(n log n); it degrades to O(n²) on already sorted data with a poor pivot choice, which random pivot selection helps avoid."),
            ("How would you detect a cycle in a linked list?",
             "Use Floyd's slow and fast pointer technique — if the fast pointer ever meets the slow pointer, a cycle exists."),
        ],
    },
    "AI/ML Interview": {
        "tip": "Relate concepts back to a project you've built to show applied understanding.",
        "questions": [
            ("What is overfitting and how do you prevent it?",
             "Overfitting is when a model memorizes training data instead of generalizing. Prevent it with regularization, cross-validation, more data, or simpler models."),
            ("Explain the bias-variance tradeoff.",
             "High bias means underfitting from overly simple assumptions; high variance means overfitting to noise. Good models balance both for generalization."),
            ("What is the difference between supervised and unsupervised learning?",
             "Supervised learning trains on labeled data to predict outcomes; unsupervised learning finds patterns or clusters in unlabeled data."),
            ("How does a Random Forest model work?",
             "It builds many decision trees on random data and feature subsets, then averages or votes their predictions to reduce overfitting and variance."),
        ],
    },
}

tabs = st.tabs(list(QUESTION_BANK.keys()))

for tab, (track_name, content) in zip(tabs, QUESTION_BANK.items()):
    with tab:
        st.markdown(f'<div class="reco-box">💡 Tip: {content["tip"]}</div>', unsafe_allow_html=True)
        st.markdown("<br/>", unsafe_allow_html=True)

        if st.button(f"🔄 Generate New Questions", key=f"gen_{track_name}"):
            st.session_state[f"qset_{track_name}"] = random.sample(
                content["questions"], k=min(3, len(content["questions"]))
            )

        qset = st.session_state.get(f"qset_{track_name}", content["questions"][:3])

        for i, (q, sample_answer) in enumerate(qset):
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            st.markdown(f"**Q{i+1}. {q}**")
            with st.expander("💬 Show sample answer"):
                st.write(sample_answer)
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-heading"><span class="accent-bar"></span>🎙️ Mock Interview</div>', unsafe_allow_html=True)
st.markdown('<div class="ai-card">', unsafe_allow_html=True)
st.caption("Pick a track, answer the question in your own words, and get a quick response-quality score.")

mock_track = st.selectbox("Choose a track", options=list(QUESTION_BANK.keys()), key="mock_track")

if "mock_q" not in st.session_state or st.session_state.get("mock_track_prev") != mock_track:
    st.session_state["mock_q"], st.session_state["mock_sample"] = random.choice(
        QUESTION_BANK[mock_track]["questions"]
    )
    st.session_state["mock_track_prev"] = mock_track

st.markdown(f"**Question:** {st.session_state['mock_q']}")
user_answer = st.text_area("Your Answer", height=140, placeholder="Type your answer as you would in a real interview...")

if st.button("✅ Score My Response", use_container_width=True):
    if not user_answer.strip():
        st.error("Please type an answer before scoring.")
    else:
        words = user_answer.split()
        word_count = len(words)
        sample_keywords = {w.lower().strip(".,") for w in st.session_state["mock_sample"].split() if len(w) > 4}
        answer_keywords = {w.lower().strip(".,") for w in words}
        overlap = len(sample_keywords & answer_keywords)

        length_score = min(word_count / 60 * 40, 40)  # up to 40 pts for sufficient detail
        keyword_score = min(overlap * 6, 40)          # up to 40 pts for relevant content
        structure_score = 20 if word_count >= 20 else 8  # basic completeness

        total = round(min(length_score + keyword_score + structure_score, 100))

        st.progress(total)
        st.markdown(f"### Response Score: {total} / 100")
        if total >= 75:
            st.success("Strong answer — well detailed and relevant. 🎯")
        elif total >= 50:
            st.warning("Decent start — add more specific detail and examples.")
        else:
            st.error("Too brief or off-topic — review the sample answer and try again.")
        with st.expander("💬 Compare with sample answer"):
            st.write(st.session_state["mock_sample"])

st.markdown("</div>", unsafe_allow_html=True)
