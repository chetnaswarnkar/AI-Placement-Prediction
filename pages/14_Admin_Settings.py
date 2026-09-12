"""Admin Settings — read-only view of environment-based configuration and
system status. Admin credentials are never edited here (they live in
environment variables only, never in the database or source code)."""

from pathlib import Path

import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Admin Settings", page_icon="🛡️", layout="wide")

db.init_db()
auth.init_session()

BASE_DIR = Path(__file__).resolve().parent.parent


def load_css():
    css_path = BASE_DIR / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


load_css()
theme.render_theme_toggle()
theme.apply_theme_css()
auth.require_admin()


def render_admin_sidebar():
    with st.sidebar:
        st.markdown('<div class="admin-badge">🛡️ ADMIN PANEL</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="sidebar-user-chip">
                <div class="chip-avatar">A</div>
                <div>
                    <div class="chip-name">{st.session_state.get("student_email", "Admin")}</div>
                    <div class="chip-role">Administrator</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/9_Admin_Dashboard.py", label="Dashboard", icon=":material/dashboard:")
        st.page_link("pages/10_Registered_Students.py", label="Registered Students", icon=":material/group:")
        st.page_link("pages/11_Prediction_History.py", label="Predictions", icon=":material/insights:")
        st.page_link("pages/12_Resume_Analytics.py", label="Resume Analytics", icon=":material/description:")
        st.page_link("pages/13_Admin_Analytics.py", label="Student Analytics", icon=":material/bar_chart:")
        st.page_link("pages/10_Registered_Students.py", label="User Management", icon=":material/manage_accounts:")
        st.page_link("pages/14_Admin_Settings.py", label="Settings", icon=":material/settings:")
        st.markdown("---")
        if st.button("Logout", icon=":material/logout:", use_container_width=True, key="admin_logout"):
            auth.logout()
            st.switch_page("app.py")


render_admin_sidebar()

st.markdown('<div class="section-heading"><span class="accent-bar"></span>⚙️ Settings</div>', unsafe_allow_html=True)
st.caption("Read-only system status. Admin credentials live only in environment variables — never here, and never in the database.")

st.markdown('<div class="ai-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">🔐 Admin Credential Source</div>', unsafe_allow_html=True)
if db.admin_env_configured():
    st.markdown('<span class="tag tag-green">Configured via environment variables</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="tag tag-red">Not configured</span>', unsafe_allow_html=True)
st.caption(
    "Set `ADMIN_EMAIL` plus `ADMIN_PASSWORD_HASH` (a bcrypt hash — recommended) "
    "or `ADMIN_PASSWORD` (plaintext, dev-only) before starting the app. "
    "This page never displays the password itself, hashed or otherwise."
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="ai-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">🗄️ Database</div>', unsafe_allow_html=True)
db_size_kb = round(db.DB_PATH.stat().st_size / 1024, 1) if db.DB_PATH.exists() else 0
st.write(f"File: `{db.DB_PATH.name}`")
st.write(f"Size: {db_size_kb} KB")
st.write(f"Password hashing: {'bcrypt' if db._HAS_BCRYPT else 'PBKDF2-SHA256 (bcrypt not installed — run `pip install bcrypt`)'}")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="ai-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">📋 Role-Based Access</div>', unsafe_allow_html=True)
st.write("Every student account is created with role = **student**. There is no self-service admin registration path.")
st.write("Every admin page calls `auth.require_admin()` at the top of its script, independent of whether the admin nav links are visible — changing the URL directly does not bypass this check.")
st.markdown("</div>", unsafe_allow_html=True)
