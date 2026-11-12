<div align="center">

# DeskIn Sync

**Book desks and rooms for any time window.**
A full-stack booking app for students, teachers and admins — live availability, overlap-free bookings and role-based rules.

![FastAPI](https://img.shields.io/badge/FastAPI-0.141-1D4ED8?style=for-the-badge&logo=fastapi&logoColor=DBEAFE&labelColor=172554)
![Python](https://img.shields.io/badge/Python-3.14-1D4ED8?style=for-the-badge&logo=python&logoColor=DBEAFE&labelColor=172554)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-psycopg%203-1D4ED8?style=for-the-badge&logo=postgresql&logoColor=DBEAFE&labelColor=172554)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-1D4ED8?style=for-the-badge&logo=sqlalchemy&logoColor=DBEAFE&labelColor=172554)
![Alembic](https://img.shields.io/badge/Alembic-migrations-1D4ED8?style=for-the-badge&logo=alembic&logoColor=DBEAFE&labelColor=172554)
![Pydantic](https://img.shields.io/badge/Pydantic-2-1D4ED8?style=for-the-badge&logo=pydantic&logoColor=DBEAFE&labelColor=172554)
![JWT](https://img.shields.io/badge/Auth-JWT%20%28HS256%29-1D4ED8?style=for-the-badge&logo=jsonwebtokens&logoColor=DBEAFE&labelColor=172554)
![bcrypt](https://img.shields.io/badge/Passwords-bcrypt-1D4ED8?style=for-the-badge&logo=letsencrypt&logoColor=DBEAFE&labelColor=172554)

![React](https://img.shields.io/badge/React-19-0E7490?style=for-the-badge&logo=react&logoColor=CFFAFE&labelColor=164E63)
![Vite](https://img.shields.io/badge/Vite-8-0E7490?style=for-the-badge&logo=vite&logoColor=CFFAFE&labelColor=164E63)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-4-0E7490?style=for-the-badge&logo=tailwindcss&logoColor=CFFAFE&labelColor=164E63)
![React Router](https://img.shields.io/badge/React%20Router-7-0E7490?style=for-the-badge&logo=reactrouter&logoColor=CFFAFE&labelColor=164E63)
![Prettier](https://img.shields.io/badge/Prettier-3-0E7490?style=for-the-badge&logo=prettier&logoColor=CFFAFE&labelColor=164E63)

[![CI](https://img.shields.io/github/actions/workflow/status/purpledocx/deskin-sync/ci.yml?style=for-the-badge&logo=githubactions&logoColor=EDE9FE&label=CI&labelColor=2E1065)](https://github.com/purpledocx/deskin-sync/actions/workflows/ci.yml)
![Tests](https://img.shields.io/badge/tests-69%20passed-5B21B6?style=for-the-badge&logo=pytest&logoColor=EDE9FE&labelColor=2E1065)
![ESLint](https://img.shields.io/badge/ESLint-0%20errors-5B21B6?style=for-the-badge&logo=eslint&logoColor=EDE9FE&labelColor=2E1065)
![Code style](https://img.shields.io/badge/code%20style-PEP%208-5B21B6?style=for-the-badge&logo=python&logoColor=EDE9FE&labelColor=2E1065)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI-5B21B6?style=for-the-badge&logo=githubactions&logoColor=EDE9FE&labelColor=2E1065)
![GitLab CI](https://img.shields.io/badge/GitLab%20CI-pipeline-5B21B6?style=for-the-badge&logo=gitlab&logoColor=EDE9FE&labelColor=2E1065)

![Design pattern](https://img.shields.io/badge/pattern-Strategy-3730A3?style=for-the-badge&logo=diagramsdotnet&logoColor=E0E7FF&labelColor=1E1B4B)
![Planning](https://img.shields.io/badge/planning-Scrum%20%2B%20MoSCoW-3730A3?style=for-the-badge&logo=jira&logoColor=E0E7FF&labelColor=1E1B4B)

[Features](#key-features) · [Quick start](#quick-start) · [Architecture](#architecture) · [Testing & CI](#testing--ci) · [Design docs](#design-docs)

[Backend README](backend/README.md) · [Frontend README](frontend/README.md) · [Definition of Done](DoD.md)

<img src="docs/showcase.gif" alt="DeskIn Sync showcase: landing page, sign in, availability dashboard, booking and cancelling" width="860">

</div>

---

## Overview

DeskIn Sync lets users find a free desk, focus booth, meeting room or training room for a chosen time window and book it in a few clicks. The repository contains two parts:

| Component | Stack | Description |
| --- | --- | --- |
| [`backend/`](backend/README.md) | FastAPI · Pydantic 2 · SQLAlchemy 2 · Alembic · PostgreSQL · JWT + bcrypt | REST API with authentication, availability search and booking rules |
| [`frontend/`](frontend/README.md) | React 19 · Vite 8 · React Router 7 · Tailwind CSS 4 · ESLint | Single-page app with landing page, sign in / sign up, dashboard and bookings overview |

## Key features

- **Live availability** — see which spaces are available or booked for any time range, and when a booked space becomes free.
- **Overlap-free bookings** — the API never allows two active bookings for the same space at the same time.
- **Edit and cancel** — reschedule or cancel bookings; cancelled bookings stay in the history.
- **Roles** — *Student*, *Teacher* and *Admin* with different viewing and editing rights; see [Booking rules](#booking-rules).
- **JWT authentication** — OAuth2 password flow with bcrypt-hashed passwords.
- **Service layer** — all booking rules live in one place and are testable without HTTP.
- **Tested** — 69 pytest tests for authentication, bookings, availability and role rules.
- **CI** — every push runs pytest against a real PostgreSQL and ESLint on the frontend.

## Booking rules

A booking runs from a chosen start time to a chosen end time, picked in steps of 30 minutes. There
is no separate "whole day" mode — a full day is simply a booking that spans it.

| Role | Sees | May change or cancel | Change window |
| --- | --- | --- | --- |
| Student | own bookings | own bookings | until 30 minutes before the start |
| Teacher | all bookings | own bookings | until 30 minutes before the start |
| Admin | all bookings | all bookings | until the booking starts |

These rules are evaluated by the API only. The frontend never re-implements them: every booking it
receives carries `can_modify` and, when a change is blocked, a `lock_hint` explaining why — that is
what the interface renders. Role permissions live in
[`backend/app/strategies/role_strategy.py`](backend/app/strategies/role_strategy.py) (Strategy
pattern), the change window in
[`backend/app/services/booking_service.py`](backend/app/services/booking_service.py).

### Known limitations

- **Overlap is enforced in the service layer, not by a database constraint.** Every create and
  update checks for conflicts (`existing.start_at < new.end_at AND existing.end_at > new.start_at`,
  over `active` bookings only) and rejects them with HTTP 409. The `bookings` table itself has no
  `EXCLUDE` constraint, so two requests arriving at the very same moment could in theory both pass
  the check. For the scope of this project that is an accepted trade-off; a PostgreSQL
  `EXCLUDE USING gist` constraint over `(space_id, tstzrange(start_at, end_at))` would be the fix
  if real concurrency mattered.
- There are no configurable opening hours and no maximum booking length: any time window in the
  future is accepted.

## Architecture

```mermaid
flowchart LR
    U([User]) --> FE[React frontend<br/>Vite · port 5173]
    FE -- "fetch · JSON<br/>Authorization: Bearer token" --> BE[FastAPI backend<br/>port 8000]
    BE -- "SQLAlchemy · psycopg" --> DB[(PostgreSQL)]
```

Inside the backend a request passes through these layers:

```mermaid
flowchart LR
    P[Pydantic schemas<br/>validation] --> R[Router<br/>HTTP in, status code out]
    R --> S[Service layer<br/>booking rules · overlap check]
    S --> M[SQLAlchemy models]
    S -. "may this role do it?" .-> ST[Role strategies<br/>Student · Teacher · Admin]
```

| Layer | Where | Responsibility |
| --- | --- | --- |
| Schemas | [`backend/app/schemas/`](backend/app/schemas) | Validate input and shape responses (Pydantic) |
| Routers | [`backend/app/routers/`](backend/app/routers) | HTTP only: call the service, map errors to status codes |
| Services | [`backend/app/services/`](backend/app/services) | Business rules: overlap check, create, update, cancel |
| Strategies | [`backend/app/strategies/`](backend/app/strategies) | Per-role permissions (Strategy pattern) |
| Models | [`backend/app/models/`](backend/app/models) | SQLAlchemy tables, migrated with Alembic |

## Repository structure

```text
deskin-sync/
├── backend/        # FastAPI app, Alembic migrations, seeder, pytest suite
├── frontend/       # React + Vite single-page app
├── docs/           # ERD, diagrams, wireframes, screenshots and showcase
├── .github/        # GitHub Actions workflow (pytest + ESLint)
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

## Testing & CI

| Check | Command | What it covers |
| --- | --- | --- |
| Backend tests | `cd backend && python -m pytest -q` | 69 tests: auth, booking API, booking service, role strategies, availability |
| Frontend lint | `cd frontend && npm run lint` | ESLint on all React code |
| Frontend build | `cd frontend && npm run build` | Production build with Vite |

The tests run against a separate database (`deskin_sync_test`) and refuse to start on any other one. The same checks run automatically on every push and pull request in [GitHub Actions](.github/workflows/ci.yml) and [GitLab CI](.gitlab-ci.yml), with a throwaway PostgreSQL service container.

## Design docs

| Document | File |
| --- | --- |
| Entity relationship diagram | [`docs/ERD.png`](docs/ERD.png) |
| Class diagram (schemas + role strategies) | [`docs/Klassendiagram.png`](docs/Klassendiagram.png) · [source](docs/Klassendiagram.puml) |
| Sequence diagram (overlap prevention) | [`docs/Sequence_diagram.png`](docs/Sequence_diagram.png) |
| Flowchart / sitemap | [`docs/Flowchart.png`](docs/Flowchart.png) |
| Wireframes | [`docs/wireframes/`](docs/wireframes) |

<details>
<summary>Show the ERD and the sequence diagram</summary>

<img src="docs/ERD.png" alt="Entity relationship diagram" width="860">

<img src="docs/Sequence_diagram.png" alt="Sequence diagram of creating a booking with overlap prevention" width="860">

</details>

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
