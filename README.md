<div align="center">

# DeskIn Sync

**Book desks and rooms by the hour or by the day.**
A full-stack booking app for students, teachers and admins — live availability, overlap-free bookings and role-based rules.

![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=flat-square&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat-square&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-psycopg%203-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT%20%28HS256%29-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)
![pytest](https://img.shields.io/badge/Tests-pytest%209-0A9EDC?style=flat-square&logo=pytest&logoColor=white)

[Backend README](backend/README.md) · [Frontend README](frontend/README.md) · [Definition of Done](DoD.md)

<img src="docs/screenshots/frontend/dashboard-availability.png" alt="DeskIn Sync space availability dashboard" width="860">

</div>

---

## Overview

DeskIn Sync lets users find a free desk, focus booth, meeting room or training room for a chosen time window and book it in a few clicks. The repository contains two parts:

| Component | Stack | Description |
| --- | --- | --- |
| [`backend/`](backend/README.md) | FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL · JWT | REST API with authentication, availability search and booking rules |
| [`frontend/`](frontend/README.md) | React 19 · Vite 8 · React Router 7 · Tailwind CSS 4 | Single-page app with landing page, sign in / sign up, dashboard and bookings overview |

## Key features

- **Live availability** — see which spaces are available or booked for any time range, and when a booked space becomes free.
- **Overlap-free bookings** — the API never allows two active bookings for the same space at the same time.
- **Edit and cancel** — reschedule or cancel bookings; cancelled bookings stay in the history.
- **Roles** — *Student*, *Teacher* and *Admin* with different viewing and editing rights, plus a 30-minute change window for students and teachers.
- **JWT authentication** — OAuth2 password flow with bcrypt-hashed passwords.
- **Tested** — 49 pytest tests for authentication, bookings, availability and role rules.

## Architecture

```mermaid
flowchart LR
    U([User]) --> FE[React frontend<br/>Vite · port 5173]
    FE -- "fetch · JSON<br/>Authorization: Bearer token" --> BE[FastAPI backend<br/>port 8000]
    BE -- "SQLAlchemy · psycopg" --> DB[(PostgreSQL)]
```

## Repository structure

```text
deskin-sync/
├── backend/        # FastAPI app, Alembic migrations, seeder, pytest suite
├── frontend/       # React + Vite single-page app
├── docs/           # ERD, diagrams and screenshots
├── DoD.md          # Definition of Done (Dutch)
└── README.md
```

## Quick start

**Prerequisites:** Python 3.14, PostgreSQL, Node.js 20.19+ / 22.13+ / 24+ and npm.

**1. Backend** — API on <http://127.0.0.1:8000>

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # set database URLs and a long random JWT_SECRET_KEY
alembic upgrade head
python seeder.py                   # optional demo data
uvicorn app.main:app --reload
```

**2. Frontend** — app on <http://localhost:5173>

```bash
cd frontend
npm ci
echo "VITE_API_URL=http://127.0.0.1:8000" > .env
npm run dev
```

With the seeder data you can log in as `student@deskin.test`, `teacher@deskin.test` or `admin@deskin.test` using the `DEMO_PASSWORD` from `backend/.env`.

Full setup, environment variables, API reference and scripts are in the [backend](backend/README.md) and [frontend](frontend/README.md) READMEs.

## API documentation

While the backend is running, FastAPI serves interactive docs at [`/docs`](http://127.0.0.1:8000/docs) (Swagger UI) and [`/redoc`](http://127.0.0.1:8000/redoc) (ReDoc).

## Screenshots

<table>
  <tr>
    <td width="50%" valign="top">
      <img src="docs/screenshots/frontend/landing.png" alt="Landing page"><br>
      <sub><b>Landing page</b></sub>
    </td>
    <td width="50%" valign="top">
      <img src="docs/screenshots/frontend/booking-modal.png" alt="Booking modal"><br>
      <sub><b>Booking a space</b></sub>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <img src="docs/screenshots/frontend/my-bookings-student.png" alt="My bookings"><br>
      <sub><b>My bookings</b></sub>
    </td>
    <td valign="top">
      <img src="docs/screenshots/frontend/all-bookings-admin.png" alt="All bookings (admin)"><br>
      <sub><b>All bookings (admin view)</b></sub>
    </td>
  </tr>
</table>

More screenshots: [frontend README](frontend/README.md#screenshots).

## Contributing

Work follows the [Definition of Done](DoD.md): clear acceptance criteria, backend validation, updated pytest tests that all pass, `npm run lint` without errors, a linked GitLab issue and a merge request.
