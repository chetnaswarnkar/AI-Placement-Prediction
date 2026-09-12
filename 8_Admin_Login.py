"""Admin Login — authenticates against ADMIN_EMAIL / ADMIN_PASSWORD(_HASH)
environment variables only. Credentials are never hardcoded in this file."""

from pathlib import Path

import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Admin Login", page_icon="🛡️", layout="wide")

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
st.markdown(
    '<div class="section-heading"><span class="accent-bar"></span>🛡️ Admin Login</div>',
    unsafe_allow_html=True,
)
st.caption("Restricted access. Only the configured administrator account can sign in here.")

if auth.is_admin_logged_in():
    st.success(f"You're already logged in as admin (**{st.session_state.get('student_email')}**).")
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/9_Admin_Dashboard.py", label="Go to Admin Dashboard", icon=":material/dashboard:")
    with col2:
        if st.button("Logout", icon=":material/logout:"):
            auth.logout()
            st.rerun()
    st.stop()

if not db.admin_env_configured():
    st.warning(
        "⚠️ No admin credentials are configured yet. Set the environment variables "
        "`ADMIN_EMAIL` and either `ADMIN_PASSWORD_HASH` (recommended, a bcrypt hash) "
        "or `ADMIN_PASSWORD` (dev-only, plaintext) before starting the app, e.g.:\n\n"
        "```bash\n"
        "export ADMIN_EMAIL=\"admin@yourcompany.com\"\n"
        "export ADMIN_PASSWORD=\"choose-a-strong-password\"\n"
        "streamlit run app.py\n"
        "```"
    )

left, mid, right = st.columns([1, 2, 1])
with mid:
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    admin_email = st.text_input("Admin Email", placeholder="admin@yourcompany.com")
    admin_password = st.text_input("Admin Password", type="password")
    if st.button("Login as Admin", icon=":material/lock_open:", use_container_width=True):
        if not admin_email or not admin_password:
            st.error("Please enter both the admin email and password.")
        elif db.verify_admin(admin_email, admin_password):
            auth.login_admin(admin_email)
            st.success("Admin login successful.")
            st.switch_page("pages/9_Admin_Dashboard.py")
        else:
            st.error("Invalid admin credentials.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)
st.page_link("pages/7_Login.py", label="Not an admin? Go to Student Login", icon=":material/school:")
