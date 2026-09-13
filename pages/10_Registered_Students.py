"""Registered Students — searchable/sortable table + student detail view +
account status management + CSV export. Also serves as the User Management
page referenced in the admin nav."""

import io
import csv
from pathlib import Path

import streamlit as st

import db
import auth
import theme

st.set_page_config(page_title="Registered Students", page_icon="🛡️", layout="wide")

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

st.markdown('<div class="section-heading"><span class="accent-bar"></span>👥 Registered Students</div>', unsafe_allow_html=True)
st.caption("Search, sort, filter, and manage every student account. Passwords are never displayed — only securely hashed values are stored.")

# ---- Filters ----
st.markdown('<div class="ai-card">', unsafe_allow_html=True)
f1, f2, f3 = st.columns([2, 1, 1])
with f1:
    search_term = st.text_input("Search by name or email", placeholder="e.g. Rahul or rahul@gmail.com")
with f2:
    status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])
with f3:
    sort_by = st.selectbox("Sort by", ["registration_date", "name", "email", "cgpa"])
st.markdown("</div>", unsafe_allow_html=True)

students = db.list_students(search=search_term, status_filter=status_filter, sort_by=sort_by)

st.caption(f"Showing {len(students)} student(s).")

# ---- Export ----
if students:
    export_rows = db.export_students_csv_rows()
    buf = io.StringIO()
    if export_rows:
        writer = csv.DictWriter(buf, fieldnames=export_rows[0].keys())
        writer.writeheader()
        for r in export_rows:
            writer.writerow(dict(r))
    st.download_button(
        "⬇️ Export Students (CSV)",
        data=buf.getvalue(),
        file_name="registered_students.csv",
        mime="text/csv",
        help="Excludes password hashes and any authentication secrets.",
    )

st.markdown("<br/>", unsafe_allow_html=True)

if not students:
    st.info("No students match the current filters.")
else:
    for s in students:
        st.markdown('<div class="ai-card">', unsafe_allow_html=True)
        row1, row2, row3, row4, row5 = st.columns([2, 2, 1.4, 1, 1.6])
        with row1:
            st.markdown(f"**{s['name']}**")
        with row2:
            st.caption(s["email"])
        with row3:
            st.caption(s["registration_date"])
        with row4:
            tag_class = "tag-green" if s["status"] == "active" else "tag-red"
            st.markdown(f'<span class="tag {tag_class}">{s["status"].title()}</span>', unsafe_allow_html=True)
        with row5:
            view_key = f"view_{s['id']}"
            if st.button("View", key=view_key, use_container_width=True):
                st.session_state["viewing_student_id"] = s["id"]

        if st.session_state.get("viewing_student_id") == s["id"]:
            st.markdown("---")
            full = db.get_student_by_id(s["id"])
            dcol1, dcol2, dcol3 = st.columns(3)
            with dcol1:
                st.markdown("**Personal Information**")
                st.write(f"Full Name: {full['name']}")
                st.write(f"Email: {full['email']}")
                st.write(f"Registered: {full['registration_date']}")
                st.write(f"Status: {full['status'].title()}")
            with dcol2:
                st.markdown("**Academic Information**")
                st.write(f"College: {full['college'] or '—'}")
                st.write(f"Branch: {full['branch'] or '—'}")
                st.write(f"Graduation Year: {full['graduation_year'] or '—'}")
                st.write(f"CGPA: {full['cgpa'] if full['cgpa'] is not None else '—'}")
            with dcol3:
                st.markdown("**Skills & Experience**")
                st.write(f"DSA Score: {full['dsa_score'] if full['dsa_score'] is not None else '—'}")
                st.write(f"Communication Score: {full['communication_score'] if full['communication_score'] is not None else '—'}")
                st.write(f"Projects: {full['projects'] if full['projects'] is not None else '—'}")
                st.write(f"Internships: {full['internships'] if full['internships'] is not None else '—'}")

            dcol4, dcol5 = st.columns(2)
            with dcol4:
                st.markdown("**Career**")
                st.write(f"Career Path: {full['career_path'] or '—'}")
                st.write(f"Target Role: {full['target_role'] or '—'}")
            with dcol5:
                st.markdown("**Resume**")
                st.write(f"Resume Uploaded: {'Yes' if full['resume_uploaded'] else 'No'}")
                st.write(f"Resume Score: {full['resume_score'] if full['resume_score'] is not None else '—'}")
                st.write(f"Detected Skills: {full['resume_skills'] or '—'}")

            st.caption("Note: password hashes, tokens and secret keys are never shown here or anywhere in the UI.")

            st.markdown("---")
            acol1, acol2, acol3, acol4 = st.columns(4)
            with acol1:
                if full["status"] == "active":
                    if st.button("Deactivate", key=f"deact_{s['id']}", use_container_width=True):
                        db.update_student_status(s["id"], "inactive")
                        st.rerun()
                else:
                    if st.button("Reactivate", key=f"react_{s['id']}", use_container_width=True):
                        db.update_student_status(s["id"], "active")
                        st.rerun()
            with acol2:
                confirm_key = f"confirm_delete_{s['id']}"
                if st.button("🗑️ Delete Account", key=f"del_{s['id']}", use_container_width=True):
                    st.session_state[confirm_key] = True
            with acol3:
                if st.button("Close", key=f"close_{s['id']}", use_container_width=True):
                    st.session_state["viewing_student_id"] = None
                    st.rerun()

            if st.session_state.get(f"confirm_delete_{s['id']}"):
                st.warning(f"Are you sure you want to delete **{full['name']}**'s account? This cannot be undone.")
                cc1, cc2 = st.columns(2)
                with cc1:
                    if st.button("Yes, delete permanently", key=f"yes_del_{s['id']}", use_container_width=True):
                        db.delete_student(s["id"])
                        st.session_state["viewing_student_id"] = None
                        st.session_state[f"confirm_delete_{s['id']}"] = False
                        st.rerun()
                with cc2:
                    if st.button("Cancel", key=f"cancel_del_{s['id']}", use_container_width=True):
                        st.session_state[f"confirm_delete_{s['id']}"] = False
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
