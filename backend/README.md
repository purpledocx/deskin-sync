<div align="center">

# DeskIn Sync — Backend API

**REST API for booking desks and rooms by the hour or by the day.**
Built with FastAPI, PostgreSQL and JWT authentication.

![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-psycopg%203-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-1.20-6BA539?style=flat-square)
![Pydantic](https://img.shields.io/badge/Pydantic-2.13-E92063?style=flat-square&logo=pydantic&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT%20%28HS256%29-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)
![pytest](https://img.shields.io/badge/Tests-pytest%209-0A9EDC?style=flat-square&logo=pytest&logoColor=white)

[Frontend README](../frontend/README.md) · [Project root](../README.md) · [Definition of Done](../DoD.md)

</div>

---

## Contents

- [Overview](#overview)
- [Key features](#key-features)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting started](#getting-started)
- [Environment variables](#environment-variables)
- [Database, data model and migrations](#database-data-model-and-migrations)
- [Authentication (JWT)](#authentication-jwt)
- [Roles and permissions](#roles-and-permissions)
- [API reference](#api-reference)
- [Request and response examples](#request-and-response-examples)
- [Booking rules](#booking-rules)
- [Interactive API docs](#interactive-api-docs)
- [Testing](#testing)
- [How the frontend talks to this API](#how-the-frontend-talks-to-this-api)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The backend is a FastAPI application (`app/main.py`, title **DeskIn SmartDesk API**, version `0.1.0`) that powers the DeskIn Sync booking app. It lets users:

- register and sign in with email and password,
- check which desks, focus booths, meeting rooms and training rooms are free for a chosen time window,
- create, reschedule and cancel bookings,
- see their own bookings — or, for teachers and admins, everyone's bookings.

The booking rules depend on the caller's role, and the API reports its verdict per booking, so clients never have to re-implement them — see [Roles and permissions](#roles-and-permissions).

Business rules (overlap prevention, past-time checks, the 30-minute change window and role permissions) are enforced on the server, so the API stays consistent no matter which client calls it.

## Key features

- **JWT authentication** using the OAuth2 password flow (`/auth/login`), with bcrypt password hashing via passlib.
- **Role-based rules** for `Student`, `Teacher` and `Admin`, implemented with a Strategy pattern (`app/strategies/role_strategy.py`).
- **Overlap prevention**: a space can never have two active bookings in the same time range.
- **Availability search** that returns every active space with its category, capacity, facilities and — when booked — the time it becomes free.
- **Soft cancellation**: cancelled bookings keep their history (`status = "cancelled"`).
- **Timezone-safe input**: datetimes sent without an offset are treated as UTC.
- **Alembic migrations** plus an idempotent **demo data seeder** (`seeder.py`).
- **58 pytest tests** covering auth, booking API, availability, overlap logic and role strategies.

## Tech stack

| Layer | Technology (version pinned in `requirements.txt`) |
| --- | --- |
| Web framework | FastAPI 0.141.1, Starlette 1.6.0, Uvicorn 0.52.4 |
| Validation | Pydantic 2.13.5, email-validator 2.3.0 |
| Database | PostgreSQL, driver psycopg 3.3.5 (`postgresql+psycopg://`) |
| ORM | SQLAlchemy 2.0.52 (typed `Mapped[...]` declarative models) |
| Migrations | Alembic 1.20.0 |
| Auth | python-jose 3.5.0 (JWT), passlib 1.7.4 + bcrypt 4.0.1, python-multipart (form login) |
| Config | python-dotenv (`.env`) |
| Tests | pytest 9.1.1, httpx (FastAPI `TestClient`), pytest-dotenv |

## Project structure

```text
backend/
├── alembic/
│   ├── env.py                 # reads DATABASE_URL from app.database
│   └── versions/              # 4 migrations (schema + seed data)
├── alembic.ini
├── app/
│   ├── main.py                # FastAPI app, CORS, health checks, router registration
│   ├── database.py            # engine, SessionLocal, Base, get_db()
│   ├── security.py            # bcrypt hashing + JWT creation
│   ├── dependencies.py        # OAuth2 bearer scheme + get_current_user()
│   ├── models/                # SQLAlchemy models (User, Role, Space, Booking, ...)
│   ├── schemas/               # Pydantic request/response schemas
│   ├── routers/               # auth.py, bookings.py, spaces.py
│   ├── services/              # booking_service.py (overlap), space_service.py (availability)
│   └── strategies/            # role_strategy.py (Student / Teacher / Admin rules)
├── tests/                     # pytest suite (uses a separate test database)
├── seeder.py                  # optional demo data
├── requirements.txt
└── .env.example
```

## Prerequisites

- **Python 3.14** (the version the project's virtual environment was created with) — `X | None` type hints require at least Python 3.10.
- **PostgreSQL** server you can create databases on (the project does not pin a server version).
- `pip` and `venv` (bundled with Python).

## Getting started

All commands below are run from the `backend/` directory.

**1. Create a virtual environment and install dependencies**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Create the databases**

The app uses one database for development and a separate one for tests (the test suite refuses to run unless the test URL contains `deskin_sync_test`).

```bash
psql -U postgres -c "CREATE USER deskin WITH PASSWORD 'change-me';"
psql -U postgres -c "CREATE DATABASE deskin_sync OWNER deskin;"
psql -U postgres -c "CREATE DATABASE deskin_sync_test OWNER deskin;"
```

**3. Configure the environment**

```bash
cp .env.example .env
```

Then edit `.env` — at minimum set the database credentials and a long random `JWT_SECRET_KEY` (see [Environment variables](#environment-variables)).

**4. Apply the migrations**

```bash
alembic upgrade head
```

This creates all tables and seeds the three roles plus a minimal set of spaces and facilities.

**5. (Optional) Load demo data**

```bash
python seeder.py
```

**6. Start the API**

```bash
uvicorn app.main:app --reload
```

The API is now available at <http://127.0.0.1:8000>. Verify it with:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok","project":"DeskIn SmartDesk"}

curl http://127.0.0.1:8000/health/database
# {"status":"ok","database":"connected"}   (503 "Database connection failed" if PostgreSQL is unreachable)
```

## Environment variables

`app/database.py`, `app/security.py`, `seeder.py` and the tests read these values from `backend/.env` via python-dotenv. The `.env` file is git-ignored.

| Variable | Required | Default | Used by | Description |
| --- | --- | --- | --- | --- |
| `DATABASE_URL` | Yes | — | app, Alembic, seeder | SQLAlchemy URL of the main database. The app stops at startup if it is missing. |
| `TEST_DATABASE_URL` | For tests | — | `tests/conftest.py` | URL of the test database. Must contain `deskin_sync_test`. |
| `JWT_SECRET_KEY` | Yes | — | `app/security.py` | Secret used to sign JWTs. The app stops at startup if it is missing. |
| `JWT_ALGORITHM` | No | `HS256` | `app/security.py` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRES_MINUTES` | No | `60` | `app/security.py` | Access token lifetime in minutes. |
| `DEMO_PASSWORD` | For `seeder.py` | — | `seeder.py` | Password given to every seeded demo account. |

### `.env.example`

```dotenv
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/deskin_sync
TEST_DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@localhost:5432/deskin_sync_test
JWT_SECRET_KEY=change-me-long-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MINUTES=60
DEMO_PASSWORD=123123123
```

> [!IMPORTANT]
> Replace `JWT_SECRET_KEY` with a long random value, e.g. `python -c "import secrets; print(secrets.token_hex(32))"`. Never commit a real `.env`.

## Database, data model and migrations

### Data model

All tables are defined as SQLAlchemy 2.0 typed models in `app/models/`. Every `datetime` column is stored as `TIMESTAMP WITH TIME ZONE`.

```mermaid
erDiagram
    roles ||--o{ users : "has"
    users ||--o{ bookings : "makes"
    space_categories ||--o{ spaces : "groups"
    spaces ||--o{ bookings : "is booked in"
    spaces ||--o{ space_facilities : "has"
    facilities ||--o{ space_facilities : "is linked to"

    roles {
        int id PK
        string name UK "Student | Teacher | Admin"
    }
    users {
        int id PK
        string name
        string email UK
        string password_hash "bcrypt"
        int role_id FK
    }
    space_categories {
        int id PK
        string name UK
    }
    spaces {
        int id PK
        string name UK
        int category_id FK
        bool is_active
        int capacity
    }
    facilities {
        int id PK
        string name UK
    }
    space_facilities {
        int space_id PK, FK
        int facility_id PK, FK
    }
    bookings {
        int id PK
        int user_id FK
        int space_id FK
        timestamptz start_at
        timestamptz end_at
        string status "active | cancelled"
        timestamptz created_at "server default NOW()"
    }
```

### Migrations

Alembic reads the database URL from `DATABASE_URL` (see `alembic/env.py`), so `alembic.ini` needs no credentials.

| Revision | Description |
| --- | --- |
| `a92d80019b9a` | Create the initial schema (all tables above, without `capacity`) |
| `289295f4e7e6` | Add `spaces.capacity` |
| `f8e876d50280` | Seed the roles `Student`, `Teacher`, `Admin` |
| `fee1e5971e47` | Seed categories `Desk` and `Meeting room`, spaces `Desk A1` and `Meeting Room B1`, facilities `Screen` and `Whiteboard` |

Useful commands:

```bash
alembic upgrade head      # apply all migrations
alembic current           # show the current revision (fee1e5971e47 (head) after a full upgrade)
```

`alembic/env.py` sets `target_metadata = Base.metadata`, so new migrations can be generated from model changes with Alembic's autogenerate feature.

### Demo data (`seeder.py`)

`python seeder.py` fills the database with reproducible demo data (`random.seed(42)`):

- **Accounts** — three demo accounts plus generated users (25 students, 5 teachers, 1 admin). Every seeded account uses the password from `DEMO_PASSWORD`.

  | Email | Role |
  | --- | --- |
  | `student@deskin.test` | Student |
  | `teacher@deskin.test` | Teacher |
  | `admin@deskin.test` | Admin |

- **Spaces** — 20 desks, 8 meeting rooms, 4 focus booths and 3 training rooms with random facilities; roughly 8% are created inactive.
- **Bookings** — weekday bookings from 10 days ago to 14 days ahead, between 08:00 and 18:00 UTC, about 10% of them cancelled.

The seeder is safe to re-run: existing users, roles, categories, facilities and spaces are reused, and bookings are only generated when the `bookings` table is empty.

## Authentication (JWT)

### Flow

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant A as FastAPI
    participant DB as PostgreSQL
    C->>A: POST /auth/register (JSON: name, email, password)
    A->>DB: insert user with role "Student"
    A-->>C: 201 {id, name, email, role}
    C->>A: POST /auth/login (form: username=email, password)
    A->>DB: find user by email, verify bcrypt hash
    A-->>C: 200 {access_token, token_type: "bearer"}
    C->>A: GET /bookings/ (Authorization: Bearer <token>)
    A->>A: decode + verify signature and exp
    A->>DB: load user by "sub" (email)
    A-->>C: 200 [bookings]
```

### Details (from the code)

| Topic | Behaviour |
| --- | --- |
| Registration | `POST /auth/register` with JSON. `name` 2–100 chars, valid `email`, `password` 8–72 chars. New users always get the `Student` role. A duplicate email returns `409`. |
| Login | `POST /auth/login` uses `OAuth2PasswordRequestForm`, so the body is **form-encoded** (`application/x-www-form-urlencoded`) and the **email goes in the `username` field**. Wrong credentials return `401 Invalid email or password`. |
| Token delivery | The token is returned in the JSON response body: `{"access_token": "<jwt>", "token_type": "bearer"}`. No cookies are set. |
| Token usage | Send it in the header `Authorization: Bearer <jwt>` (`OAuth2PasswordBearer`). |
| Claims | `sub` (user email), `user_id`, `role`, `exp`. Signed with `JWT_SECRET_KEY` using `JWT_ALGORITHM` (default `HS256`). |
| Expiration | `exp` = issue time + `ACCESS_TOKEN_EXPIRES_MINUTES` (default 60). An expired or invalid token returns `401 Could not validate credentials`; a missing header returns `401 Not authenticated`. |
| Refresh / logout | Not implemented. There is no refresh token, logout endpoint or token revocation — clients sign in again when the token expires. |
| Authorization source | On every request the user is loaded from the database by the `sub` email, and permissions are based on that user's current role in the database. |

**Protected endpoints:** every `/bookings` and `/spaces` endpoint requires a valid token. Only `/auth/*` and `/health*` are public.

## Roles and permissions

Rules live in `app/strategies/role_strategy.py`. An unknown role falls back to the least-privileged `Student` rules.

| Capability | Student | Teacher | Admin |
| --- | :---: | :---: | :---: |
| Create bookings | ✅ | ✅ | ✅ |
| See bookings of all users (`GET /bookings/`) | Own only | ✅ | ✅ |
| Edit / cancel other users' bookings | — | — | ✅ |
| Minimum time before start to edit or cancel | 30 min | 30 min | Until the start |

New accounts created through `/auth/register` are always Students. Teacher and Admin accounts come from the seeder (or a direct database change); there is no API endpoint for changing roles.

A Teacher therefore has a read-only overview of everyone's bookings, while changing and cancelling stays with the owner and the Admin.

Because these rules belong to the API, `BookingRead` carries the outcome for the requesting user:

| Field | Meaning |
| --- | --- |
| `can_modify` | `true` when this user may edit or cancel this booking right now |
| `lock_hint` | `null` when `can_modify` is `true`, otherwise the reason a change is refused |

A client only has to render those two fields; `PUT` and `DELETE` apply the same check again and answer `403` or `409` if it no longer holds.

## API reference

Base URL for local development: `http://127.0.0.1:8000`

### Health

| Method | Path | Auth | Description |
| --- | --- | :---: | --- |
| `GET` | `/health` | — | Liveness check. |
| `GET` | `/health/database` | — | Runs `SELECT 1`; returns `503` if the database is unreachable. |

### Authentication — `/auth`

| Method | Path | Auth | Body | Success | Errors |
| --- | --- | :---: | --- | --- | --- |
| `POST` | `/auth/register` | — | JSON `UserRegister` | `201` `RegisteredUser` | `409` email exists, `422` validation |
| `POST` | `/auth/login` | — | Form `username`, `password` | `200` `Token` | `401` invalid credentials |

### Spaces — `/spaces`

| Method | Path | Auth | Query | Success | Errors |
| --- | --- | :---: | --- | --- | --- |
| `GET` | `/spaces/availability` | JWT | `start_at`, `end_at` (ISO 8601) | `200` list of `SpaceAvailabilityRead` | `400` start ≥ end, `401` no / invalid token, `422` missing params |
| `GET` | `/spaces/{space_id}/bookings` | JWT | `start_at`, `end_at` | `200` list of `{start_at, end_at}` | `400` start ≥ end, `401` no / invalid token, `404` unknown space |

`/spaces/availability` lists only **active** spaces. `is_available` is `false` when an active booking overlaps the window, and `available_from` is then the latest end time among those overlapping bookings. `/spaces/{id}/bookings` returns only the time slots of active bookings — no user data.

### Bookings — `/bookings` (JWT required)

| Method | Path | Body | Success | Errors |
| --- | --- | --- | --- | --- |
| `GET` | `/bookings/` | — | `200` list of `BookingRead`, sorted by `start_at` | `401` |
| `POST` | `/bookings/` | `BookingCreate` | `201` `BookingRead` | `400` start in the past, `404` unknown space, `409` space inactive or overlap, `422` validation |
| `PUT` | `/bookings/{booking_id}` | `BookingUpdate` | `200` `BookingRead` | `400`, `403` not allowed, `404`, `409` not active / too close to start / overlap / space inactive, `422` |
| `DELETE` | `/bookings/{booking_id}` | — | `200` `BookingRead` with `status: "cancelled"` | `403`, `404`, `409` already cancelled / too close to start |

> [!NOTE]
> The list and create routes are registered with a trailing slash. `GET /bookings` (without `/`) answers with a `307` redirect to `/bookings/`.

### Schemas

| Schema | Fields |
| --- | --- |
| `UserRegister` | `name`, `email`, `password` |
| `RegisteredUser` | `id`, `name`, `email`, `role` |
| `Token` | `access_token`, `token_type` |
| `BookingCreate` / `BookingUpdate` | `space_id` (> 0), `start_at`, `end_at` |
| `BookingRead` | `id`, `user_id`, `space_id`, `space_name`, `user_name`, `start_at`, `end_at`, `status`, `created_at`, `can_modify`, `lock_hint` |
| `SpaceAvailabilityRead` | `id`, `name`, `capacity`, `category`, `facilities[]`, `is_available`, `available_from` |
| `SpaceBookingSlot` | `start_at`, `end_at` |

## Request and response examples

The examples below were recorded against a local instance loaded with the seeder data. Emails and passwords are placeholders, and the token is shortened.

<details open>
<summary><b>Register</b></summary>

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Doe", "email": "jane.doe@example.com", "password": "change-me-123"}'
```

```json
{ "id": 35, "name": "Jane Doe", "email": "jane.doe@example.com", "role": "Student" }
```
</details>

<details open>
<summary><b>Log in and store the token</b></summary>

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=jane.doe@example.com" \
  -d "password=change-me-123"
```

```json
{ "access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer" }
```

Decoded token payload:

```json
{ "sub": "jane.doe@example.com", "user_id": 35, "role": "Student", "exp": 1792935777.49 }
```

```bash
TOKEN="<paste access_token here>"
```
</details>

<details>
<summary><b>Check availability</b></summary>

```bash
curl "http://127.0.0.1:8000/spaces/availability?start_at=2026-10-26T09:00:00Z&end_at=2026-10-26T10:00:00Z"
```

```json
[
  {
    "id": 1,
    "name": "Desk A1",
    "capacity": 1,
    "category": "Desk",
    "facilities": [],
    "is_available": false,
    "available_from": "2026-10-26T11:00:00+01:00"
  },
  {
    "id": 11,
    "name": "Desk A10",
    "capacity": 1,
    "category": "Desk",
    "facilities": ["Docking station"],
    "is_available": true,
    "available_from": null
  }
]
```
</details>

<details>
<summary><b>Create, reschedule and cancel a booking</b></summary>

```bash
# Create
curl -X POST http://127.0.0.1:8000/bookings/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"space_id": 2, "start_at": "2026-11-02T06:00:00Z", "end_at": "2026-11-02T07:00:00Z"}'
```

```json
{
  "space_id": 2,
  "start_at": "2026-11-02T07:00:00+01:00",
  "end_at": "2026-11-02T08:00:00+01:00",
  "id": 814,
  "user_id": 35,
  "status": "active",
  "created_at": "2026-10-25T13:43:08.135101+01:00",
  "space_name": "Meeting Room B1",
  "user_name": "Jane Doe",
  "can_modify": true,
  "lock_hint": null
}
```

```bash
# Reschedule (all three fields are required)
curl -X PUT http://127.0.0.1:8000/bookings/814 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"space_id": 2, "start_at": "2026-11-02T06:00:00Z", "end_at": "2026-11-02T06:30:00Z"}'

# Cancel (soft delete: the booking is returned with "status": "cancelled")
curl -X DELETE http://127.0.0.1:8000/bookings/814 \
  -H "Authorization: Bearer $TOKEN"
```
</details>

<details>
<summary><b>Typical error responses</b></summary>

| Situation | Status | Body |
| --- | :---: | --- |
| No `Authorization` header | `401` | `{"detail": "Not authenticated"}` |
| Invalid or expired token | `401` | `{"detail": "Could not validate credentials"}` |
| Wrong email or password | `401` | `{"detail": "Invalid email or password"}` |
| Email already registered | `409` | `{"detail": "User with this email already exists"}` |
| Overlapping booking | `409` | `{"detail": "This space is already booked for the selected time"}` |
| Start time in the past | `400` | `{"detail": "Start time can not be earlier than <current UTC time>"}` |
| Booking of another student | `403` | `{"detail": "You have no access to following booking"}` |
| Cancelling twice | `409` | `{"detail": "Current booking is already cancelled"}` |
| Unknown booking | `404` | `{"detail": "Booking not found"}` |
| Invalid body | `422` | FastAPI validation error list (`detail[]` with `loc`, `msg`, `type`) |

</details>

> [!TIP]
> Returned timestamps are timezone-aware ISO 8601 strings. The offset (for example `+01:00`) follows the PostgreSQL session time zone; the instant is the same as the UTC value that was sent.

## Booking rules

These rules are enforced by the schemas (`app/schemas/booking.py`), the router (`app/routers/bookings.py`) and the service (`app/services/booking_service.py`):

1. `start_at` must be earlier than `end_at` (`422`).
2. Datetimes without an offset are interpreted as **UTC**.
3. A booking cannot start in the past (`400`).
4. The space must exist (`404`) and be active (`409`).
5. Two **active** bookings for the same space may not overlap (`409`). Cancelled bookings are ignored, and back-to-back bookings (one ends exactly when the next starts) are allowed.
6. When rescheduling, the booking itself is excluded from the overlap check.
7. Only active bookings can be edited or cancelled, and Students and Teachers must do so at least 30 minutes before the start (Admins have no limit).

The overlap check flow is also documented in [`docs/Sequence-diagram(overlap_prevention).png`](../docs/Sequence-diagram%28overlap_prevention%29.png) (labels in Dutch):

<p align="center">
  <img src="../docs/Sequence-diagram%28overlap_prevention%29.png" alt="Sequence diagram of the booking overlap check" width="820">
</p>

## Interactive API docs

FastAPI generates OpenAPI documentation automatically once the server is running:

| Tool | URL |
| --- | --- |
| Swagger UI | <http://127.0.0.1:8000/docs> |
| ReDoc | <http://127.0.0.1:8000/redoc> |
| OpenAPI schema (JSON) | <http://127.0.0.1:8000/openapi.json> |

To try protected endpoints in Swagger UI, click **Authorize** and enter your **email in the `username` field** together with your password — the button uses the same OAuth2 password flow as `/auth/login`.

For screenshots of the API in use through the web app (availability search, booking, rescheduling and cancelling), see the [frontend README](../frontend/README.md#screenshots).

## Testing

The test suite uses the database from `TEST_DATABASE_URL`. It creates all tables from the SQLAlchemy models at the start of the session, runs each test inside a transaction that is rolled back, and drops the tables at the end — migrations are not needed for tests.

```bash
cd backend
pytest
```

| File | Covers |
| --- | --- |
| `tests/test_auth.py` | Registration, duplicate email, login, wrong credentials, protected route token check |
| `tests/test_booking_api.py` | Create / list / update / cancel bookings, permissions, 30-minute window, naive datetimes |
| `tests/test_booking_service.py` | Overlap detection edge cases |
| `tests/test_spaces_api.py` | Availability and space slot endpoints |
| `tests/test_role_strategies.py` | Student / Teacher / Admin strategies |

There is no linter or formatter configured for the backend.

## How the frontend talks to this API

- The React app calls this API with `fetch`, using the base URL from its `VITE_API_URL` variable (default `http://localhost:8000`).
- CORS in `app/main.py` allows the origins `http://localhost:5173` and `http://127.0.0.1:5173` (the Vite dev server), with credentials, all methods and all headers. If the frontend runs on another origin, add it to `allow_origins`.
- The frontend logs in through `/auth/login` with form data, stores the returned token and sends it as `Authorization: Bearer <token>` on every request.

See the [frontend README](../frontend/README.md) for details.

## Contributing

The repository includes a [Definition of Done](../DoD.md) (in Dutch). In short, a change is done when:

- it has clear acceptance criteria and is linked to a GitLab issue,
- input is validated on the backend and errors are shown clearly to the user,
- pytest tests are added or updated and **all tests pass**,
- `npm run lint` passes for frontend changes,
- it is committed with a clear message and merged through a merge request, with evidence (screenshot, test log or MR link) saved.

---

<div align="center">

[Frontend README](../frontend/README.md) · [Project root](../README.md)

</div>
