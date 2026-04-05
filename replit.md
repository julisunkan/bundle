# AI Resume & Cover Letter Creator

## Overview
A full-stack Progressive Web App (PWA) that uses Groq's AI (Llama 3) to help users with resume optimization, cover letter generation, job tracking, interview preparation, LinkedIn profile optimization, and career chat.

## Running the App
The app runs via gunicorn on port 5000:
```
python3 -m gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

## Architecture
- **Framework**: Flask (Python)
- **Database**: Firebase Firestore (sole database — hardcoded credentials, no SQLite/MySQL)
- **AI**: Groq API (Llama 3.3-70b) — configured via the Admin Panel at `/julisunkan`
- **File parsing**: pdfplumber (PDF), python-docx (DOCX)
- **PDF generation**: reportlab
- **Frontend**: Jinja2 templates + vanilla JS + CSS (PWA-enabled)

## Key Files
- `main.py` — App entry point
- `app.py` — Flask application factory, blueprint registration
- `routes/` — Blueprint route handlers (resume, jobs, interview, chat, linkedin, admin, job_board)
- `models/settings.py` — Firestore-backed Settings class (same API as old SQLAlchemy model)
- `utils/firestore_manager.py` — Firebase Admin SDK init with hardcoded service account credentials
- `utils/data_layer.py` — All CRUD operations for resumes, jobs, messages, job posts → Firestore only
- `utils/ai_engine.py` — Groq AI integration
- `utils/parser.py` — PDF/DOCX text extraction
- `utils/job_aggregator.py` — External job board API fetching
- `templates/` — Jinja2 HTML templates
- `static/` — CSS, images, PWA manifest, service worker

## Configuration
- **Groq API Key**: Set via Admin Panel at `/julisunkan` (stored in Firestore Settings collection)
- **Secret Key**: `SECRET_KEY` env var (or `SESSION_SECRET`)
- **Admin Panel**: Protected at `/julisunkan`

## Database
- **Firebase Firestore is the only database.** SQLite and MySQL have been removed.
- Firebase credentials are hardcoded in `utils/firestore_manager.py` (`_HARDCODED_CREDENTIALS`).
- Project: `resume-app-db` on Firebase
- Collections: `resumes`, `jobs`, `contact_messages`, `job_posts`, `settings`, `_counters`
- `utils/data_layer.py` is the sole data access layer for all collections.
- `utils/db_manager.py` and `utils/sync_manager.py` are stubs kept for import compatibility.

## Dependencies
All dependencies listed in `requirements.txt`. Key packages:
- flask, flask-sqlalchemy, flask-cors
- groq
- pdfplumber, python-docx, reportlab
- gunicorn, psycopg2-binary, email_validator
- firebase-admin (primary database driver)
