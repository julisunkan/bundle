# AI Resume & Cover Letter Creator

## Overview
A full-stack Progressive Web App (PWA) that uses Groq's AI (Llama 3) to help users with resume optimization, cover letter generation, job tracking, interview preparation, LinkedIn profile optimization, and career chat.

## Running the App
The app runs via gunicorn on port 5000:
```
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload --workers 4 --timeout 30 main:app
```

## Architecture
- **Framework**: Flask (Python)
- **Database**: Firebase Firestore (sole database)
- **AI**: Groq API (Llama 3.3-70b) — configured via the Admin Panel at `/julisunkan`
- **File parsing**: pdfplumber (PDF), python-docx (DOCX)
- **PDF generation**: reportlab
- **Frontend**: Jinja2 templates + vanilla JS + CSS (PWA-enabled)

## Key Files
- `main.py` — App entry point
- `app.py` — Flask application factory, blueprint registration, startup Firebase check
- `routes/` — Blueprint route handlers (resume, jobs, interview, chat, linkedin, admin, job_board)
- `models/settings.py` — Firestore-backed Settings class
- `utils/firestore_manager.py` — Firebase Admin SDK init with startup_check() for non-blocking initialization
- `utils/credentials_store.py` — Firebase credentials lookup (supports FIREBASE_CREDENTIALS env var)
- `utils/data_layer.py` — All CRUD operations for resumes, jobs, messages, job posts → Firestore only
- `utils/ai_engine.py` — Groq AI integration
- `utils/parser.py` — PDF/DOCX text extraction
- `utils/job_aggregator.py` — External job board API fetching
- `templates/` — Jinja2 HTML templates
- `static/` — CSS, images, PWA manifest, service worker

## Configuration
- **Firebase Credentials**: Visit `/setup` (hidden admin-only page) to paste your service account JSON, OR set the `FIREBASE_CREDENTIALS` env var with the full JSON string. Credentials are stored in `instance/credentials.db` — never hardcoded in source code.
- **Groq API Key**: Set via Admin Panel at `/julisunkan` (stored in Firestore Settings collection)
- **Secret Key**: `SECRET_KEY` env var (or `SESSION_SECRET`)
- **Admin Panel**: Protected at `/julisunkan`
- **Setup Page**: `/setup` — hidden page to paste Firebase service account JSON before the app loads

## Security
- No credentials are hardcoded in source code
- Firebase credentials stored in SQLite at `instance/credentials.db` (gitignored)
- Credential priority: `FIREBASE_CREDENTIALS` env var → `instance/credentials.db`
- Admin password stored in Firestore Settings (default: `admin123` — change after first login)
- Sensitive keys (`groq_api_key`, `admin_password`) are masked in the admin settings UI

## Database
- **Firebase Firestore is the only database.** SQLite (credentials.db) stores only Firebase credentials.
- Firebase credentials are provided via `/setup` page or `FIREBASE_CREDENTIALS` env var.
- At app startup, `startup_check()` in `firestore_manager.py` verifies connectivity within 15 seconds. If unavailable, all Firestore calls fail fast with an exception (caught by try/except blocks returning empty defaults).
- Credentials can be updated without a restart via `/setup` or the admin Firebase panel.
- Collections: `resumes`, `jobs`, `contact_messages`, `job_posts`, `settings`, `_counters`
- `utils/data_layer.py` is the sole data access layer for all collections.

## Dependencies
All dependencies listed in `requirements.txt`. Key packages:
- flask, flask-sqlalchemy, flask-cors
- groq
- pdfplumber, python-docx, reportlab
- gunicorn, psycopg2-binary, email_validator
- firebase-admin (primary database driver)
- gevent (installed for async worker support)

## Replit-Specific Notes
- Workflow: "Start application" runs gunicorn with 4 workers and 30s timeout on port 5000
- The app gracefully handles Firebase being unavailable — pages load with empty/default data
- To restore full functionality, provide valid Firebase credentials via the FIREBASE_CREDENTIALS secret
