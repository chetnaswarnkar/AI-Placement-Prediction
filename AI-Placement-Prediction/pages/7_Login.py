"""Student Login / Register — creates or authenticates a student account."""

from pathlib import Path

import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Login", page_icon="🔐", layout="wide")

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
    '<div class="section-heading"><span class="accent-bar"></span>🔐 Student Login</div>',
    unsafe_allow_html=True,
)

if auth.is_student_logged_in():
    st.success(f"You're already logged in as **{st.session_state['student_name']}**.")
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("app.py", label="Go to Home", icon=":material/home:")
    with col2:
        if st.button("Logout", icon=":material/logout:"):
            auth.logout()
            st.rerun()
    st.stop()

left, mid, right = st.columns([1, 2, 1])
with mid:
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        st.markdown('<div class="ai-card">', unsafe_allow_html=True)
        login_email = st.text_input("Email", key="login_email", placeholder="you@example.com")
        login_password = st.text_input("Password", key="login_password", type="password")
        if st.button("Login", icon=":material/login:", use_container_width=True, key="do_login"):
            if not login_email or not login_password:
                st.error("Please enter both email and password.")
            else:
                row = db.authenticate_student(login_email, login_password)
                if row is None:
                    st.error("Invalid email/password, or this account is inactive.")
                else:
                    auth.login_student(row)
                    st.success(f"Welcome back, {row['name']}!")
                    st.switch_page("app.py")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_register:
        st.markdown('<div class="ai-card">', unsafe_allow_html=True)
        reg_name = st.text_input("Full Name", key="reg_name", placeholder="e.g. Aarav Sharma")
        reg_email = st.text_input("Email", key="reg_email", placeholder="you@example.com")
        reg_password = st.text_input("Password", key="reg_password", type="password", help="At least 6 characters.")
        reg_password_confirm = st.text_input("Confirm Password", key="reg_password_confirm", type="password")
        if st.button("Create Account", icon=":material/person_add:", use_container_width=True, key="do_register"):
            if reg_password != reg_password_confirm:
                st.error("Passwords do not match.")
            else:
                ok, message = db.create_student(reg_name, reg_email, reg_password)
                if ok:
                    st.success(message)
                    st.info("Switch to the **Login** tab above to sign in.")
                else:
                    st.error(message)
        st.caption("New accounts are always created with the **student** role — there is no self-service admin signup.")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)
st.page_link("pages/8_Admin_Login.py", label="Administrator? Go to Admin Login", icon=":material/admin_panel_settings:")
