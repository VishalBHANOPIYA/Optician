# Ayan-Optics

Optician e-commerce site for Ayan-Optics, Indore.
Stack: Flask + PostgreSQL + SQLAlchemy.

## Setup

1. python -m venv venv
2. Activate venv:
   - Windows: venv\Scripts\activate
   - Mac/Linux: source venv/bin/activate
3. pip install -r requirements.txt
4. Create PostgreSQL database:
   psql -U postgres
   CREATE DATABASE ayan_optics;
   \q
5. Edit .env and set DATABASE_URL and SECRET_KEY
6. flask db init
7. flask db migrate -m "initial"
8. flask db upgrade
9. flask run

Open http://127.0.0.1:5000 — you should see "Welcome to Ayan-Optics".
Open http://127.0.0.1:5000/health — should return JSON with status ok.

## Deployment (Production)

1. Set environment variables (see .env.example): FLASK_ENV=production, a strong SECRET_KEY,
   the production DATABASE_URL, and a NEW secret ADMIN_SECRET_PATH.
2. Install deps: pip install -r requirements.txt
3. Apply migrations: flask db upgrade
4. Seed once (first deploy only): python seed.py
5. Run with gunicorn: gunicorn wsgi:app --workers 3 --bind 0.0.0.0:8000
   (or use the Procfile on platforms like Render/Railway/Heroku-style hosts)
6. Put behind HTTPS (the app sets secure cookies in production).
7. After first login, change the admin password from the admin panel and pick a strong ADMIN_SECRET_PATH.
8. Ensure the upload folder (app/static/uploads) is writable / persisted on your host.
