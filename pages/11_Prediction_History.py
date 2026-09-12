"""Prediction History — every placement prediction ever run, searchable/sortable."""

from pathlib import Path

import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Prediction History", page_icon="🛡️", layout="wide")

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

st.markdown('<div class="section-heading"><span class="accent-bar"></span>🎯 Prediction History</div>', unsafe_allow_html=True)
st.caption("Every placement prediction ever run through the model, logged with full inputs.")

st.markdown('<div class="ai-card">', unsafe_allow_html=True)
f1, f2, f3 = st.columns([2, 1, 1])
with f1:
    search_term = st.text_input("Search by student name", placeholder="e.g. Rahul")
with f2:
    prediction_filter = st.selectbox("Prediction", ["All", "Placed", "Not Placed"])
with f3:
    sort_by = st.selectbox("Sort by", ["created_at", "probability", "student_name"])
st.markdown("</div>", unsafe_allow_html=True)

preds = db.get_predictions(search=search_term, prediction_filter=prediction_filter, sort_by=sort_by)
st.caption(f"Showing {len(preds)} prediction(s).")

if not preds:
    st.info("No predictions logged yet. Predictions are recorded automatically from the Home page.")
else:
    for p in preds:
        st.markdown('<div class="ai-card">', unsafe_allow_html=True)
        c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 1, 1, 1.4])
        with c1:
            st.markdown(f"**{p['student_name']}**")
            st.caption(p["created_at"])
        with c2:
            st.metric("CGPA", p["cgpa"])
        with c3:
            st.metric("Projects", p["projects"])
        with c4:
            st.metric("Internships", p["internships"])
        with c5:
            st.metric("DSA", p["dsa_score"])
        with c6:
            tag_class = "tag-green" if p["prediction"] == 1 else "tag-red"
            label = "🟢 Placed" if p["prediction"] == 1 else "🔴 Not Placed"
            st.markdown(f'<span class="tag {tag_class}">{label}</span>', unsafe_allow_html=True)
            st.caption(f"Probability: {p['probability']}%")
        st.markdown("</div>", unsafe_allow_html=True)
