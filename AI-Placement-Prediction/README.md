# AI Student Placement Prediction System

A professional, AI-powered Streamlit dashboard that predicts a student's placement
chances using a trained machine learning model, with a real student login/register
system and a fully separate, role-gated Admin Panel backed by SQLite.

## ✨ Features

**Student experience**
- **Register / Login** — real accounts, bcrypt-hashed passwords, stored in SQLite
- **Placement Prediction** — RandomForestClassifier-based prediction with probability score, logged to your account
- **Skill Score & Breakdown**, **AI Recommendation & Improvement Plan**
- **Resume Analyzer** — PDF upload, skill detection, ATS-style scoring (logged to your account)
- **Job Matcher**, **Interview Preparation**, **Career Roadmap**, **AI Chatbot**, **Analytics**

**Owner / Admin experience** (completely separate from the student app)
- **Admin Login** — checked against environment variables only, never hardcoded
- **Admin Dashboard** — live counts (students, predictions, resumes, avg. probability, top career path)
- **Registered Students** — search, sort, filter, view full profile, deactivate/reactivate/delete (with confirmation), CSV export
- **Prediction History** — every prediction ever run, searchable/sortable
- **Resume Analytics** — aggregate resume stats + most common skill gaps
- **Student Analytics** — registrations/predictions over time, placement distribution, popular career paths
- **Settings** — read-only system/config status

## 📁 Project Structure

```
AI-Placement-Prediction/
│
├── app.py                          # Main dashboard (Home) — student-only, login required
├── db.py                           # SQLite data layer + bcrypt password hashing
├── auth.py                         # Session-based role guards (require_student / require_admin)
├── style.css                       # Global stylesheet
├── placement_model.pkl             # Trained RandomForestClassifier
├── placement.db                    # SQLite database (created automatically on first run)
│
├── assets/
│   ├── logo.png
│   ├── banner.jpg
│   └── sidebar-bottom.png
│
├── pages/
│   ├── 1_Resume_Analyzer.py
│   ├── 2_Job_Matcher.py
│   ├── 3_Interview_Preparation.py
│   ├── 4_Career_Roadmap.py
│   ├── 5_AI_Chatbot.py
│   ├── 6_Analytics.py
│   ├── 7_Login.py                  # Student login / register
│   ├── 8_Admin_Login.py            # Admin login (env-var credentials only)
│   ├── 9_Admin_Dashboard.py
│   ├── 10_Registered_Students.py   # Also serves as "User Management"
│   ├── 11_Prediction_History.py
│   ├── 12_Resume_Analytics.py
│   ├── 13_Admin_Analytics.py
│   └── 14_Admin_Settings.py
│
└── README.md
```

## 🔁 Architecture note: what changed from the original spec

The original spec described a MongoDB + Express API + React + JWT (MERN) stack.
This build is **Streamlit-native** instead, since that's what the rest of the app
is built in — the two aren't compatible in the same codebase. The substitutions,
mapped 1:1:

| Original spec           | This build                                                |
|--------------------------|------------------------------------------------------------|
| MongoDB                  | SQLite (`placement.db`, via `db.py`)                        |
| Express `/api/admin/*`   | Plain Python functions in `db.py`, called directly          |
| JWT auth                 | Streamlit `st.session_state` (server-side, per-session)      |
| React + Recharts         | Streamlit + Plotly                                          |
| bcrypt password hashing  | Same — real `bcrypt` if installed, safe PBKDF2 fallback otherwise |
| Auth middleware           | `auth.require_student()` / `auth.require_admin()`, called at the top of every gated page — re-checked on every page load, so visiting an admin URL directly without the right session role is refused |

All data (students, predictions, resumes) is real and persisted in SQLite — nothing
on the Admin pages is hardcoded.

## 🔐 Admin credentials (required before first use)

Admin credentials are **never hardcoded**. Set them as environment variables before
starting the app:

```bash
export ADMIN_EMAIL="admin@yourcompany.com"
export ADMIN_PASSWORD="choose-a-strong-password"     # dev-only, plaintext
streamlit run app.py
```

For production, hash the password yourself and use `ADMIN_PASSWORD_HASH` instead:

```bash
python3 -c "import bcrypt; print(bcrypt.hashpw(b'your-password', bcrypt.gensalt()).decode())"
export ADMIN_EMAIL="admin@yourcompany.com"
export ADMIN_PASSWORD_HASH="<paste the bcrypt hash here>"
```

On Windows PowerShell, use `$env:ADMIN_EMAIL = "..."` instead of `export`.

Without these variables set, the Admin Login page will show a warning and refuse
all logins — there is no default/backdoor admin account.

## 🧠 The ML Model

`placement_model.pkl` is a `RandomForestClassifier` trained on a synthetic but
realistic dataset of student profiles. It takes exactly 5 features, in this order:

```
CGPA, Projects, Internships, DSA, Communication
```

Prediction flow:

```
Student Input → Pandas DataFrame → RandomForestClassifier
    → model.predict() → model.predict_proba() → Placement Probability & Result
    → logged to SQLite via db.log_prediction()
```

> ⚠️ This model is trained on synthetic data for demonstration purposes. Retrain it
> on real historical placement data before using it for actual decisions.

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install streamlit pandas numpy scikit-learn plotly pypdf pillow bcrypt
```

`bcrypt` is strongly recommended for real password security. If it isn't
installed, the app still works — it falls back to a salted PBKDF2 hash — but
you'll see a note about it on the Admin Settings page.

### 2. Set admin credentials (see above), then run the app

```bash
export ADMIN_EMAIL="admin@yourcompany.com"
export ADMIN_PASSWORD="choose-a-strong-password"
streamlit run app.py
```

### 3. Use the app

- New students: go to **Login / Register** in the sidebar → Register tab → create an account → Login.
- The Home dashboard, Resume Analyzer, and every other student page require login.
- Admins: go to `pages/8_Admin_Login.py` (linked from the bottom of the student Login page) and sign in with the env-var credentials.
- The student sidebar **never** shows any admin links, and every admin page independently refuses to render for non-admin sessions — even if a student guesses the URL.

### 4. (Optional) Retrain the ML model

Regenerate `placement_model.pkl` using `scikit-learn`'s `RandomForestClassifier` on
your own historical student/placement data, keeping the same 5 feature columns
(`CGPA`, `Projects`, `Internships`, `DSA`, `Communication`) and a binary `Placed` target.

## 🖼️ Assets

Place `logo.png`, `banner.jpg` and `sidebar-bottom.png` in `assets/`. The app
degrades gracefully with a fallback UI (icons/gradients) if any image is missing
or fails to load — it will never crash because of an optional image.

## ⬆️ Pushing this to GitHub

`.gitignore` is already set up to exclude `placement.db` (your local database —
never commit real student data) and `.streamlit/secrets.toml` (never commit
real admin credentials). To push:

```bash
cd AI-Placement-Prediction
git init
git add .
git commit -m "Initial commit: AI Student Placement Prediction System"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

If you plan to deploy on Streamlit Community Cloud, set `ADMIN_EMAIL` and
`ADMIN_PASSWORD` (or `ADMIN_PASSWORD_HASH`) as **Secrets** in the app's settings
there instead of committing them anywhere — never put real credentials in
`.streamlit/config.toml` or in code.

## 📝 Disclaimer

Placement probabilities and expected package estimates shown in this dashboard
are model-generated, illustrative metrics — not guarantees of employment or salary.
Passwords are hashed and never displayed anywhere in the UI, including the Admin Panel.
