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
