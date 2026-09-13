"""
theme.py
---------
A real, working dark/light mode toggle rendered at the top-right of the
page — in the same spot Streamlit's native "Deploy" button used to sit
(that button is hidden via CSS + .streamlit/config.toml). Dark is the
default theme this app was designed around; light mode re-maps the same
CSS variables to light values.
"""

import streamlit as st

LIGHT_CSS = """
:root{
    --bg-void:        #EEF0F8 !important;
    --bg-base:        #F5F6FB !important;
    --bg-panel:       #FFFFFF !important;
    --bg-panel-alt:   #F0F1F8 !important;
    --border-soft:    rgba(60, 65, 110, 0.14) !important;
    --border-strong:  rgba(60, 65, 110, 0.28) !important;
    --text-primary:   #191C2B !important;
    --text-secondary: #4A4F72 !important;
    --text-muted:     #767CA0 !important;
}
.stApp{
    background:
        radial-gradient(1200px 600px at 15% -10%, rgba(124,58,237,0.07), transparent 60%),
        radial-gradient(1000px 500px at 100% 0%, rgba(37,99,235,0.06), transparent 55%),
        var(--bg-base) !important;
}
section[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #FFFFFF 0%, #F1F2F9 100%) !important;
    border-right: 1px solid var(--border-soft) !important;
}
.hero-wrap{
    background: linear-gradient(135deg, #EDEFFB 0%, #E5EAFB 100%) !important;
    border: 1px solid var(--border-soft) !important;
}
.hero-title{ color: #191C2B !important; }
.hero-sub{ color: var(--text-secondary) !important; }
.topbar-icon{
    background: var(--bg-panel-alt) !important;
    border: 1px solid var(--border-soft) !important;
    color: var(--text-secondary) !important;
}
.sidebar-logo-fallback{ box-shadow: none !important; }
"""


def init_theme():
    st.session_state.setdefault("theme_mode", "dark")


def render_theme_toggle():
    """Renders a small right-aligned toggle button at the very top of the
    page — the spot where Streamlit's native Deploy button used to be."""
    init_theme()
    spacer, toggle_col = st.columns([11, 1])
    with toggle_col:
        is_light = st.session_state["theme_mode"] == "light"
        icon = "☀️" if is_light else "🌙"
        if st.button(icon, key="theme_toggle_btn", help="Switch to light mode" if not is_light else "Switch to dark mode"):
            st.session_state["theme_mode"] = "dark" if is_light else "light"
            st.rerun()


def apply_theme_css():
    """Call AFTER load_css() so the light overrides win when active."""
    init_theme()
    if st.session_state["theme_mode"] == "light":
        st.markdown(f"<style>{LIGHT_CSS}</style>", unsafe_allow_html=True)
