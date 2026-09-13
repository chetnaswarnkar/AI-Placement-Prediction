"""Student Analytics (Admin) — charts computed from live database data.

The original spec calls for "Recharts" (a React charting library). Since
this build is Streamlit-native rather than React, Plotly is used here to
produce equivalent interactive charts from the same underlying data.
"""

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Student Analytics", page_icon="🛡️", layout="wide")

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

st.markdown('<div class="section-heading"><span class="accent-bar"></span>📊 Student Analytics</div>', unsafe_allow_html=True)
st.caption("All charts below are computed live from the database.")

PLOT_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#AEB4CE", family="Inter"), margin=dict(l=20, r=20, t=40, b=20),
)

reg_data = db.registrations_over_time()
pred_data = db.predictions_over_time()
placed, not_placed = db.placement_distribution()
avg_scores = db.average_academic_scores()
career_data = db.career_path_distribution()

row1c1, row1c2 = st.columns(2)
with row1c1:
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📈 Registrations Over Time</div>', unsafe_allow_html=True)
    if reg_data:
        dates = [d for d, _ in reg_data]
        counts = [c for _, c in reg_data]
        fig = go.Figure(go.Scatter(x=dates, y=counts, mode="lines+markers", line=dict(color="#8B5CF6", width=3)))
        fig.update_layout(**PLOT_TEMPLATE, height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No registrations yet.")
    st.markdown("</div>", unsafe_allow_html=True)

with row1c2:
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🎯 Predictions Over Time</div>', unsafe_allow_html=True)
    if pred_data:
        dates = [d for d, _ in pred_data]
        counts = [c for _, c in pred_data]
        fig = go.Figure(go.Scatter(x=dates, y=counts, mode="lines+markers", line=dict(color="#3B82F6", width=3)))
        fig.update_layout(**PLOT_TEMPLATE, height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No predictions logged yet.")
    st.markdown("</div>", unsafe_allow_html=True)

row2c1, row2c2 = st.columns(2)
with row2c1:
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🟢🔴 Placement Prediction Distribution</div>', unsafe_allow_html=True)
    if placed + not_placed > 0:
        fig = go.Figure(go.Pie(
            labels=["Placed", "Not Placed"], values=[placed, not_placed], hole=0.55,
            marker=dict(colors=["#34D399", "#F87171"]), textfont=dict(color="#0B0F1E"),
        ))
        fig.update_layout(**PLOT_TEMPLATE, height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No predictions logged yet.")
    st.markdown("</div>", unsafe_allow_html=True)

with row2c2:
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🗺️ Most Popular Career Paths</div>', unsafe_allow_html=True)
    if career_data:
        names = [c for c, _ in career_data]
        counts = [n for _, n in career_data]
        fig = go.Figure(go.Bar(x=names, y=counts, marker=dict(color="#22D3EE")))
        fig.update_layout(**PLOT_TEMPLATE, height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No career paths selected yet.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="ai-card">', unsafe_allow_html=True)
st.markdown('<div class="card-title">📊 Average Academic & Skill Scores</div>', unsafe_allow_html=True)
fig = go.Figure(go.Bar(
    x=["Avg CGPA (x10)", "Avg DSA Score", "Avg Communication Score"],
    y=[avg_scores["avg_cgpa"] * 10, avg_scores["avg_dsa"], avg_scores["avg_communication"]],
    marker=dict(color=["#8B5CF6", "#3B82F6", "#22D3EE"]),
))
fig.update_layout(**PLOT_TEMPLATE, height=320, yaxis_range=[0, 105])
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
