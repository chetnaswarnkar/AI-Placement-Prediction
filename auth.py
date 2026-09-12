"""
auth.py
--------
Streamlit session-state auth helpers. This is the "authorization
middleware" for this single-process app: every admin page calls
require_admin() at the very top, and every student-only page calls
require_student() at the very top. Access is re-checked on every page
load — a student can never reach admin content just by typing a URL,
because the admin pages themselves refuse to render without
st.session_state["role"] == "admin".
"""

import streamlit as st

import db


def init_session():
    st.session_state.setdefault("role", None)          # None | "student" | "admin"
    st.session_state.setdefault("student_id", None)
    st.session_state.setdefault("student_name", None)
    st.session_state.setdefault("student_email", None)


def login_student(row):
    st.session_state["role"] = "student"
    st.session_state["student_id"] = row["id"]
    st.session_state["student_name"] = row["name"]
    st.session_state["student_email"] = row["email"]


def login_admin(email: str):
    st.session_state["role"] = "admin"
    st.session_state["student_id"] = None
    st.session_state["student_name"] = None
    st.session_state["student_email"] = email


def logout():
    st.session_state["role"] = None
    st.session_state["student_id"] = None
    st.session_state["student_name"] = None
    st.session_state["student_email"] = None


def is_student_logged_in() -> bool:
    init_session()
    return st.session_state.get("role") == "student"


def is_admin_logged_in() -> bool:
    init_session()
    return st.session_state.get("role") == "admin"


def require_student(login_page: str = "pages/7_Login.py"):
    """Block rendering unless a student is logged in. Call at the top of
    any student-only page (e.g. Home, Resume Analyzer)."""
    init_session()
    if st.session_state.get("role") != "student":
        st.warning("🔒 Please log in as a student to access this page.")
        st.page_link(login_page, label="Go to Login / Register", icon=":material/login:")
        st.stop()


def require_admin(login_page: str = "pages/8_Admin_Login.py"):
    """Block rendering unless an authenticated admin session is active.
    This check re-runs on every page load, independent of whether the
    admin nav links are visible — a student changing the URL still hits
    this guard and is refused."""
    init_session()
    if st.session_state.get("role") != "admin":
        st.error("⛔ Access denied. This page is restricted to authenticated administrators.")
        st.page_link(login_page, label="Go to Admin Login", icon=":material/admin_panel_settings:")
        st.stop()
