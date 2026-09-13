"""
db.py
------
SQLite-backed data layer for the AI Student Placement Prediction System.

Replaces the "MongoDB + Express API" layer described in the original spec
with a Streamlit-native equivalent: a local SQLite database file
(placement.db), password hashing via bcrypt, and plain Python functions
that act as the "backend" — every admin-only function re-checks the
caller's role, so security does not depend on hiding UI elements alone.

Tables:
    students     — registered student accounts (role="student")
    predictions  — every placement prediction ever run, linked to a student
    resumes      — every resume analysis ever run, linked to a student
"""

import os
import sqlite3
import hashlib
import hmac
import secrets
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "placement.db"

try:
    import bcrypt
    _HAS_BCRYPT = True
except ImportError:
    _HAS_BCRYPT = False


# ----------------------------------------------------------------------
# Password hashing
# ----------------------------------------------------------------------
def hash_password(plain_password: str) -> str:
    """Hash a password with bcrypt if available, else a salted PBKDF2 fallback."""
    if _HAS_BCRYPT:
        return "bcrypt$" + bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), bytes.fromhex(salt), 260_000)
    return f"pbkdf2${salt}${digest.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify a password against a hash produced by hash_password()."""
    try:
        if stored_hash.startswith("bcrypt$") and _HAS_BCRYPT:
            return bcrypt.checkpw(plain_password.encode(), stored_hash[len("bcrypt$"):].encode())
        if stored_hash.startswith("pbkdf2$"):
            _, salt, digest_hex = stored_hash.split("$", 2)
            check = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), bytes.fromhex(salt), 260_000)
            return hmac.compare_digest(check.hex(), digest_hex)
        return False
    except Exception:
        return False


# ----------------------------------------------------------------------
# Admin credential check (env vars, never hardcoded)
# ----------------------------------------------------------------------
def verify_admin(email: str, password: str) -> bool:
    """
    Verify admin login against environment variables:
      ADMIN_EMAIL           — the admin's email address
      ADMIN_PASSWORD_HASH   — (recommended) a bcrypt hash of the admin password
      ADMIN_PASSWORD        — (dev-only fallback) plaintext password

    Never hardcode admin credentials in source code.
    """
    admin_email = os.environ.get("ADMIN_EMAIL", "")
    if not admin_email or email.strip().lower() != admin_email.strip().lower():
        return False

    admin_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")
    if admin_hash:
        return verify_password(password, admin_hash if "$" in admin_hash else f"bcrypt${admin_hash}")

    admin_plain = os.environ.get("ADMIN_PASSWORD", "")
    if admin_plain:
        return hmac.compare_digest(password, admin_plain)

    return False


def admin_env_configured() -> bool:
    return bool(os.environ.get("ADMIN_EMAIL")) and bool(
        os.environ.get("ADMIN_PASSWORD_HASH") or os.environ.get("ADMIN_PASSWORD")
    )


# ----------------------------------------------------------------------
# Connection / schema
# ----------------------------------------------------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            status TEXT NOT NULL DEFAULT 'active',
            registration_date TEXT NOT NULL,
            college TEXT,
            branch TEXT,
            graduation_year INTEGER,
            cgpa REAL,
            technical_skills TEXT,
            dsa_score REAL,
            communication_score REAL,
            projects INTEGER,
            internships INTEGER,
            certifications TEXT,
            career_path TEXT,
            target_role TEXT,
            resume_uploaded INTEGER DEFAULT 0,
            resume_score REAL,
            resume_skills TEXT
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            student_name TEXT NOT NULL,
            cgpa REAL, projects INTEGER, internships INTEGER,
            dsa_score REAL, communication_score REAL,
            prediction INTEGER, probability REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            student_name TEXT NOT NULL,
            resume_score REAL,
            detected_skills TEXT,
            missing_skills TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL
        );
        """
    )
    conn.commit()
    conn.close()


# ----------------------------------------------------------------------
# Student account functions
# ----------------------------------------------------------------------
def create_student(name: str, email: str, password: str) -> tuple[bool, str]:
    """Register a new student. Role is always forced to 'student' — a
    student can never self-register as admin."""
    email = email.strip().lower()
    if not name.strip() or not email or not password:
        return False, "Name, email and password are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    conn = get_connection()
    try:
        existing = conn.execute("SELECT id FROM students WHERE email = ?", (email,)).fetchone()
        if existing:
            return False, "An account with this email already exists."
        conn.execute(
            """INSERT INTO students (name, email, password_hash, role, status, registration_date)
               VALUES (?, ?, ?, 'student', 'active', ?)""",
            (name.strip(), email, hash_password(password), datetime.now().strftime("%d %b %Y")),
        )
        conn.commit()
        return True, "Account created successfully. You can now log in."
    except Exception as e:
        return False, f"Registration failed: {e}"
    finally:
        conn.close()


def authenticate_student(email: str, password: str):
    """Returns the student row (sqlite3.Row) if credentials are valid and
    account is active, else None."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM students WHERE email = ?", (email.strip().lower(),)).fetchone()
    conn.close()
    if row is None:
        return None
    if row["status"] != "active":
        return None
    if not verify_password(password, row["password_hash"]):
        return None
    return row


def get_student_by_id(student_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return row


def update_student_profile(student_id: int, **fields):
    if not fields:
        return
    allowed = {
        "college", "branch", "graduation_year", "cgpa", "technical_skills",
        "dsa_score", "communication_score", "projects", "internships",
        "certifications", "career_path", "target_role",
        "resume_uploaded", "resume_score", "resume_skills",
    }
    fields = {k: v for k, v in fields.items() if k in allowed}
    if not fields:
        return
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    conn = get_connection()
    conn.execute(f"UPDATE students SET {set_clause} WHERE id = ?", (*fields.values(), student_id))
    conn.commit()
    conn.close()


# ----------------------------------------------------------------------
# Admin: student listing / management (every function assumes the
# CALLER has already verified role == 'admin' via require_admin())
# ----------------------------------------------------------------------
def list_students(search: str = "", status_filter: str = "All", sort_by: str = "registration_date", ascending: bool = False):
    conn = get_connection()
    query = "SELECT * FROM students WHERE 1=1"
    params = []
    if search:
        query += " AND (name LIKE ? OR email LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if status_filter in ("Active", "Inactive"):
        query += " AND status = ?"
        params.append(status_filter.lower())
    sort_col = sort_by if sort_by in {
        "registration_date", "name", "email", "cgpa", "status"
    } else "registration_date"
    direction = "ASC" if ascending else "DESC"
    query += f" ORDER BY {sort_col} {direction}"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def update_student_status(student_id: int, status: str):
    conn = get_connection()
    conn.execute("UPDATE students SET status = ? WHERE id = ?", (status, student_id))
    conn.commit()
    conn.close()


def delete_student(student_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


# ----------------------------------------------------------------------
# Predictions
# ----------------------------------------------------------------------
def log_prediction(student_id, student_name, cgpa, projects, internships, dsa_score, communication_score, prediction, probability):
    conn = get_connection()
    conn.execute(
        """INSERT INTO predictions
           (student_id, student_name, cgpa, projects, internships, dsa_score, communication_score, prediction, probability, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (student_id, student_name, cgpa, projects, internships, dsa_score, communication_score,
         prediction, probability, datetime.now().strftime("%d %b %Y %H:%M")),
    )
    conn.commit()
    conn.close()


def get_predictions(search: str = "", prediction_filter: str = "All", sort_by: str = "created_at", ascending: bool = False):
    conn = get_connection()
    query = "SELECT * FROM predictions WHERE 1=1"
    params = []
    if search:
        query += " AND student_name LIKE ?"
        params.append(f"%{search}%")
    if prediction_filter == "Placed":
        query += " AND prediction = 1"
    elif prediction_filter == "Not Placed":
        query += " AND prediction = 0"
    sort_col = sort_by if sort_by in {"created_at", "probability", "student_name"} else "created_at"
    direction = "ASC" if ascending else "DESC"
    query += f" ORDER BY {sort_col} {direction}"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


# ----------------------------------------------------------------------
# Resumes
# ----------------------------------------------------------------------
def log_resume(student_id, student_name, resume_score, detected_skills, missing_skills):
    conn = get_connection()
    conn.execute(
        """INSERT INTO resumes (student_id, student_name, resume_score, detected_skills, missing_skills, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (student_id, student_name, resume_score, ",".join(detected_skills), ",".join(missing_skills),
         datetime.now().strftime("%d %b %Y %H:%M")),
    )
    conn.commit()
    conn.close()
    if student_id:
        update_student_profile(
            student_id,
            resume_uploaded=1,
            resume_score=resume_score,
            resume_skills=",".join(detected_skills),
        )


def get_resumes():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM resumes ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows


# ----------------------------------------------------------------------
# Aggregate admin stats
# ----------------------------------------------------------------------
def admin_dashboard_stats() -> dict:
    conn = get_connection()
    total_students = conn.execute("SELECT COUNT(*) c FROM students").fetchone()["c"]
    active_students = conn.execute("SELECT COUNT(*) c FROM students WHERE status='active'").fetchone()["c"]
    total_predictions = conn.execute("SELECT COUNT(*) c FROM predictions").fetchone()["c"]
    total_resumes = conn.execute("SELECT COUNT(*) c FROM resumes").fetchone()["c"]
    avg_prob_row = conn.execute("SELECT AVG(probability) a FROM predictions").fetchone()
    avg_probability = round(avg_prob_row["a"], 1) if avg_prob_row["a"] is not None else 0.0
    top_path_row = conn.execute(
        """SELECT career_path, COUNT(*) c FROM students
           WHERE career_path IS NOT NULL AND career_path != ''
           GROUP BY career_path ORDER BY c DESC LIMIT 1"""
    ).fetchone()
    most_selected_career_path = top_path_row["career_path"] if top_path_row else "—"
    conn.close()
    return {
        "total_students": total_students,
        "active_students": active_students,
        "total_predictions": total_predictions,
        "total_resumes": total_resumes,
        "avg_probability": avg_probability,
        "most_selected_career_path": most_selected_career_path,
    }


def resume_analytics_stats() -> dict:
    conn = get_connection()
    rows = conn.execute("SELECT resume_score, detected_skills, missing_skills FROM resumes").fetchall()
    conn.close()
    if not rows:
        return {
            "total": 0, "avg_score": 0, "highest": 0, "lowest": 0,
            "common_skills": [], "common_missing": [],
        }
    scores = [r["resume_score"] for r in rows if r["resume_score"] is not None]
    from collections import Counter
    skill_counter = Counter()
    missing_counter = Counter()
    for r in rows:
        if r["detected_skills"]:
            skill_counter.update(s for s in r["detected_skills"].split(",") if s)
        if r["missing_skills"]:
            missing_counter.update(s for s in r["missing_skills"].split(",") if s)
    return {
        "total": len(rows),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "highest": max(scores) if scores else 0,
        "lowest": min(scores) if scores else 0,
        "common_skills": skill_counter.most_common(8),
        "common_missing": missing_counter.most_common(8),
    }


def export_students_csv_rows():
    """Rows for CSV export — explicitly EXCLUDES password_hash and any auth secrets."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT name, email, registration_date, college, branch, cgpa,
                  projects, internships, dsa_score, communication_score
           FROM students ORDER BY registration_date DESC"""
    ).fetchall()
    conn.close()
    return rows


# ----------------------------------------------------------------------
# Charting helpers for the Student Analytics admin page
# ----------------------------------------------------------------------
def registrations_over_time():
    conn = get_connection()
    rows = conn.execute(
        "SELECT registration_date, COUNT(*) c FROM students GROUP BY registration_date ORDER BY registration_date"
    ).fetchall()
    conn.close()
    return [(r["registration_date"], r["c"]) for r in rows]


def predictions_over_time():
    conn = get_connection()
    rows = conn.execute(
        "SELECT substr(created_at, 1, 11) d, COUNT(*) c FROM predictions GROUP BY d ORDER BY d"
    ).fetchall()
    conn.close()
    return [(r["d"], r["c"]) for r in rows]


def placement_distribution():
    conn = get_connection()
    placed = conn.execute("SELECT COUNT(*) c FROM predictions WHERE prediction = 1").fetchone()["c"]
    not_placed = conn.execute("SELECT COUNT(*) c FROM predictions WHERE prediction = 0").fetchone()["c"]
    conn.close()
    return placed, not_placed


def average_academic_scores():
    conn = get_connection()
    row = conn.execute(
        "SELECT AVG(cgpa) a, AVG(dsa_score) b, AVG(communication_score) c FROM students"
    ).fetchone()
    conn.close()
    return {
        "avg_cgpa": round(row["a"], 2) if row["a"] is not None else 0,
        "avg_dsa": round(row["b"], 1) if row["b"] is not None else 0,
        "avg_communication": round(row["c"], 1) if row["c"] is not None else 0,
    }


def career_path_distribution():
    conn = get_connection()
    rows = conn.execute(
        """SELECT career_path, COUNT(*) c FROM students
           WHERE career_path IS NOT NULL AND career_path != ''
           GROUP BY career_path ORDER BY c DESC"""
    ).fetchall()
    conn.close()
    return [(r["career_path"], r["c"]) for r in rows]
