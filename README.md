# Rate-Limited Task Queue Service

A production-ready **FastAPI** REST API backed by **Redis** and **Celery** for background job processing, with **JWT authentication**, **role-based access control (RBAC)**, **per-user sliding-window rate limiting**, **structured logging**, and a **GitHub Actions CI/CD pipeline**.

---

## Features

- **JWT authentication** — register/login, Bearer tokens, configurable expiry
- **Role-based access control** — three roles: `user`, `premium`, `admin`, enforced per endpoint
- **Per-user rate limiting** — sliding-window counter backed by Redis (memory fallback); different limits per role (user: 30/min, premium: 100/min, admin: 500/min)
- **Celery task queue** — three task types across two named queues: `default` and `analysis`
- **Task routing** — `process_data` → default queue, `run_analysis` → analysis queue
- **Retry logic** — tasks retry up to 3× with configurable backoff on failure
- **Job tracking** — in-memory job store with user-scoped visibility (users see only their own jobs)
- **Admin endpoints** — `/admin/jobs` and `/admin/stats` restricted to `admin` role
- **Rate limit headers** — `Retry-After` header on 429 responses
- **GitHub Actions CI** — spins up Redis service container, runs all pytest tests on push
- **19 unit tests** — auth, task submission, RBAC, rate limiter logic

---

## Tech Stack

| Component | Technology |
|---|---|
| Framework | FastAPI 0.110+ |
| Task Queue | Celery 5.3+ |
| Message Broker | Redis 7 |
| Auth | JWT (PyJWT) |
| Validation | Pydantic v2 |
| Rate Limiting | Sliding-window counter (Redis + memory fallback) |
| CI/CD | GitHub Actions |
| Testing | pytest + FastAPI TestClient |

---

## Project Structure

```
rate-limited-task-queue/
├── app/
│   ├── __init__.py          # FastAPI app factory
│   ├── auth.py              # JWT creation, validation, role checker
│   ├── config.py            # Pydantic settings (env-based)
│   ├── rate_limiter.py      # Sliding-window rate limiter (Redis + memory fallback)
│   ├── workers/
│   │   ├── celery_app.py    # Celery configuration and task routing
│   │   └── tasks.py         # process_data, send_report, run_analysis tasks
│   └── routes/
│       ├── auth.py          # POST /auth/register, /auth/login
│       ├── tasks.py         # POST /tasks/submit, GET /tasks/{id}, GET /tasks
│       └── admin.py         # GET /admin/jobs, /admin/stats (admin only)
├── tests/
│   ├── conftest.py          # Fixtures with state reset between tests
│   ├── test_auth.py         # 5 auth tests
│   ├── test_tasks.py        # 7 task and rate-limit tests
│   ├── test_rbac.py         # 3 RBAC tests
│   └── test_rate_limiter.py # 4 rate limiter unit tests
├── .github/workflows/ci.yml # GitHub Actions with Redis service container
└── requirements.txt
```

---

## Setup

```bash
git clone https://github.com/rajasuleman7/rate-limited-task-queue.git
cd rate-limited-task-queue
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Start Redis: `docker run -d -p 6379:6379 redis:7-alpine`

---

## Running

```bash
# API server
python run.py

# Celery worker (separate terminal)
celery -A app.workers.celery_app worker --loglevel=info -Q default,analysis
```

API at **http://localhost:8000** — interactive docs at **http://localhost:8000/docs**

---

## API Endpoints

| Method | Endpoint | Role | Description |
|---|---|---|---|
| `POST` | `/auth/register` | — | Register with role |
| `POST` | `/auth/login` | — | Login, receive JWT |
| `POST` | `/tasks/submit` | any 🔒 | Submit background job |
| `GET` | `/tasks/{id}` | owner/admin 🔒 | Get job status |
| `GET` | `/tasks` | any 🔒 | List own jobs |
| `GET` | `/tasks/rate-limit/status` | any 🔒 | View rate limit remaining |
| `GET` | `/admin/jobs` | admin 🔒 | All jobs across all users |
| `GET` | `/admin/stats` | admin 🔒 | System-wide stats |

---

## Rate Limits by Role

| Role | Requests/minute |
|---|---|
| `user` | 30 |
| `premium` | 100 |
| `admin` | 500 |

429 response includes `Retry-After` header and remaining time.

---

## Tests

```bash
pytest tests/ -v
# 19 tests: auth, RBAC, job isolation, rate limiter
```
