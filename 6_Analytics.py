"""Analytics — personal profile charts plus an aggregate Admin Dashboard."""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

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


PLOT_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#AEB4CE", family="Inter"),
    margin=dict(l=20, r=20, t=40, b=20),
)

load_css()
theme.render_theme_toggle()
theme.apply_theme_css()
render_sidebar()
auth.require_student()

st.markdown('<div class="section-heading"><span class="accent-bar"></span>📊 Analytics Dashboard</div>', unsafe_allow_html=True)
st.caption("A visual breakdown of your placement profile.")

result = st.session_state.get("last_result")

if not result:
    st.info(
        "No prediction yet. Go to the **Home** page, fill in your details and click "
        "**🚀 Predict Placement** to unlock your personal analytics here."
    )
else:
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Placement Probability", f"{result['probability']}%")
    with m2:
        st.metric("Skill Score", f"{result['skill_score']} / 100")
    with m3:
        st.metric("CGPA", f"{result['cgpa']}")
    with m4:
        st.metric("DSA Score", f"{result['dsa']}")

    st.markdown("<br/>", unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown('<div class="ai-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 Skill Comparison</div>', unsafe_allow_html=True)
        categories = ["CGPA (x10)", "Projects (x20)", "Internships (x33)", "DSA", "Communication"]
        values = [
            result["cgpa"] * 10,
            min(result["projects"] * 20, 100),
            min(result["internships"] * 33, 100),
            result["dsa"],
            result["communication"],
        ]
        fig_bar = go.Figure(
            go.Bar(
                x=categories,
                y=values,
                marker=dict(
                    color=["#8B5CF6", "#7C6CF0", "#5B7CF5", "#3B82F6", "#22D3EE"],
                    line=dict(width=0),
                ),
            )
        )
        fig_bar.update_layout(**PLOT_TEMPLATE, yaxis_range=[0, 105], height=340)
        fig_bar.update_xaxes(showgrid=False)
        fig_bar.update_yaxes(showgrid=True, gridcolor="rgba(148,163,255,0.10)")
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="ai-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🧭 Profile Radar</div>', unsafe_allow_html=True)
        radar_categories = ["CGPA", "Projects", "Internships", "DSA", "Communication"]
        radar_values = [
            result["cgpa"] / 10 * 100,
            min(result["projects"] / 5 * 100, 100),
            min(result["internships"] / 3 * 100, 100),
            result["dsa"],
            result["communication"],
        ]
        fig_radar = go.Figure()
        fig_radar.add_trace(
            go.Scatterpolar(
                r=radar_values + [radar_values[0]],
                theta=radar_categories + [radar_categories[0]],
                fill="toself",
                fillcolor="rgba(139,92,246,0.28)",
                line=dict(color="#8B5CF6", width=2),
            )
        )
        fig_radar.update_layout(
            **PLOT_TEMPLATE,
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(148,163,255,0.15)", color="#7B82A3"),
                angularaxis=dict(gridcolor="rgba(148,163,255,0.15)"),
            ),
            showlegend=False,
            height=340,
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📈 Placement Probability</div>', unsafe_allow_html=True)
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=result["probability"],
            number={"suffix": "%", "font": {"color": "#F5F6FB"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#7B82A3"},
                "bar": {"color": "#8B5CF6"},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "rgba(248,113,113,0.25)"},
                    {"range": [40, 70], "color": "rgba(251,191,36,0.25)"},
                    {"range": [70, 100], "color": "rgba(52,211,153,0.25)"},
                ],
            },
        )
    )
    fig_gauge.update_layout(**PLOT_TEMPLATE, height=280)
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown(
    '<div class="section-heading"><span class="accent-bar"></span>🛡️ Looking for Admin analytics?</div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="ai-card">', unsafe_allow_html=True)
st.write(
    "The full Admin Dashboard (registered students, prediction history, resume analytics, and aggregate charts computed from the real database) now lives in its own role-gated section — only an authenticated administrator can open it."
)
st.page_link("pages/9_Admin_Dashboard.py", label="Go to Admin Dashboard", icon=":material/admin_panel_settings:")
st.markdown('</div>', unsafe_allow_html=True)
