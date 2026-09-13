"""Admin Dashboard — summary cards computed live from the database."""

from pathlib import Path

import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Admin Dashboard", page_icon="🛡️", layout="wide")

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
auth.require_admin()  # stops rendering here if the caller isn't an authenticated admin


def render_admin_sidebar(active: str = ""):
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


render_admin_sidebar("Dashboard")

st.markdown('<div class="section-heading"><span class="accent-bar"></span>🛡️ Admin Dashboard</div>', unsafe_allow_html=True)
st.caption("Live figures computed from the database — nothing on this page is hardcoded.")

stats = db.admin_dashboard_stats()

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-icon">🎓</div>'
        f'<div class="metric-value">{stats["total_students"]}</div>'
        f'<div class="metric-label">Total Registered Students</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-icon">🟢</div>'
        f'<div class="metric-value">{stats["active_students"]}</div>'
        f'<div class="metric-label">Active Students</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-icon">🎯</div>'
        f'<div class="metric-value">{stats["total_predictions"]}</div>'
        f'<div class="metric-label">Total Predictions</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br/>", unsafe_allow_html=True)
c4, c5, c6 = st.columns(3)
with c4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-icon">📄</div>'
        f'<div class="metric-value">{stats["total_resumes"]}</div>'
        f'<div class="metric-label">Total Resume Analyses</div></div>',
        unsafe_allow_html=True,
    )
with c5:
    st.markdown(
        f'<div class="metric-card"><div class="metric-icon">📈</div>'
        f'<div class="metric-value">{stats["avg_probability"]}%</div>'
        f'<div class="metric-label">Average Placement Probability</div></div>',
        unsafe_allow_html=True,
    )
with c6:
    st.markdown(
        f'<div class="metric-card"><div class="metric-icon">🗺️</div>'
        f'<div class="metric-value" style="font-size:1.1rem;">{stats["most_selected_career_path"]}</div>'
        f'<div class="metric-label">Most Selected Career Path</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br/>", unsafe_allow_html=True)
st.markdown('<div class="ai-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">🔎 Quick Links</div>', unsafe_allow_html=True)
q1, q2, q3 = st.columns(3)
with q1:
    st.page_link("pages/10_Registered_Students.py", label="View Registered Students", icon=":material/group:")
with q2:
    st.page_link("pages/11_Prediction_History.py", label="View Prediction History", icon=":material/insights:")
with q3:
    st.page_link("pages/13_Admin_Analytics.py", label="View Student Analytics", icon=":material/bar_chart:")
st.markdown("</div>", unsafe_allow_html=True)
