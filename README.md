# GreenLife Wellness Center — Minimal Web App
A simple Flask web application implementing core features:
- User registration & login (clients, therapists, admins)
- Appointment booking (basic)
- Client profile and therapist dashboard
- Admin management page
- SQLite database

## Run locally (Linux / WSL / macOS)
1. Create virtual env: `python -m venv venv && source venv/bin/activate`
2. Install: `pip install -r requirements.txt`
3. Run: `export FLASK_APP=app.py; flask run --host=0.0.0.0 --port=5000`
4. Open http://127.0.0.1:5000

## Notes
This is a minimal educational demo. For production use, add strong password hashing, input validation, CSRF protection, sessions hardening, and deploy behind HTTPS.
