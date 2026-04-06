# AI Resume & Cover Letter Creator

## Overview
A Flask-based web application that helps users build resumes, track job applications, practice interviews, chat with an AI career assistant, and optimize their LinkedIn profiles.

## Architecture
- **Framework**: Flask (Python 3.11)
- **Server**: Gunicorn (`python3 -m gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app`)
- **Database**: Google Cloud Firestore (via `firebase-admin`)
- **AI**: Groq API (via `groq` package)
- **Entry point**: `main.py` → `app.py` (`create_app()`)

## Key Files
- `main.py` — App entry point
- `app.py` — Flask factory, routes, context processor
- `utils/firestore_manager.py` — Firestore connection management
- `utils/credentials_store.py` — Firebase credential storage (env var or SQLite fallback)
- `utils/data_layer.py` — CRUD abstraction layer over Firestore
- `utils/ai_engine.py` — AI/Groq integration
- `routes/` — Flask blueprints (resume, jobs, interview, chat, linkedin, admin, job_board, setup)
- `models/settings.py` — Settings backed by Firestore
- `templates/` — Jinja2 HTML templates
- `static/` — CSS, JS, images

## Environment Variables / Secrets
- `FIREBASE_CREDENTIALS` — Firebase service account JSON (stringified). If not set, the app falls back to SQLite credentials store at `instance/credentials.db`. Configure via `/setup` page.
- `GROQ_API_KEY` — Groq API key for AI features.
- `SECRET_KEY` or `SESSION_SECRET` — Flask session secret.

## Setup Notes
- Firebase credentials must be configured before database features work. Visit `/setup` in the running app.
- The app gracefully degrades if Firebase is unavailable.
- Admin panel is at `/julisunkan`.
- Uploads are stored in the `uploads/` directory (max 10MB per file).

## Workflow
- **Start application**: `python3 -m gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app` (port 5000, webview)
