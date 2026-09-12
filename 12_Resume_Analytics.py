"""Resume Analytics — aggregate stats across every resume ever analyzed."""

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Resume Analytics", page_icon="🛡️", layout="wide")

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

st.markdown('<div class="section-heading"><span class="accent-bar"></span>📄 Resume Analytics</div>', unsafe_allow_html=True)
st.caption("Aggregate statistics across every resume analyzed via the Resume Analyzer page.")

stats = db.resume_analytics_stats()

if stats["total"] == 0:
    st.info("No resumes have been analyzed yet.")
else:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-icon">📄</div><div class="metric-value">{stats["total"]}</div><div class="metric-label">Total Resumes Analyzed</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-icon">⭐</div><div class="metric-value">{stats["avg_score"]}</div><div class="metric-label">Average Score</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-icon">🏆</div><div class="metric-value">{stats["highest"]}</div><div class="metric-label">Highest Score</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-icon">📉</div><div class="metric-value">{stats["lowest"]}</div><div class="metric-label">Lowest Score</div></div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    plot_template = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#AEB4CE", family="Inter"), margin=dict(l=20, r=20, t=40, b=20),
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="ai-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🧠 Most Common Skills Detected</div>', unsafe_allow_html=True)
        if stats["common_skills"]:
            names = [s for s, _ in stats["common_skills"]]
            counts = [c for _, c in stats["common_skills"]]
            fig = go.Figure(go.Bar(x=counts, y=names, orientation="h", marker=dict(color="#34D399")))
            fig.update_layout(**plot_template, height=320)
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No skills detected yet.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="ai-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">⚠️ Most Common Missing Skills</div>', unsafe_allow_html=True)
        if stats["common_missing"]:
            names = [s for s, _ in stats["common_missing"]]
            counts = [c for _, c in stats["common_missing"]]
            fig = go.Figure(go.Bar(x=counts, y=names, orientation="h", marker=dict(color="#F87171")))
            fig.update_layout(**plot_template, height=320)
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No missing-skill gaps recorded yet.")
        st.markdown("</div>", unsafe_allow_html=True)
