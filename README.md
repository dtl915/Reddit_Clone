# Reddit Clone

[![CI](https://github.com/dtl915/Reddit_Clone/actions/workflows/ci.yaml/badge.svg)](https://github.com/dtl915/Reddit_Clone/actions/workflows/ci.yaml)

A Reddit-style forum: accounts, communities, posts, nested comments and voting.
The backend is a Flask REST API with PostgreSQL, tested with pytest and deployed automatically
through GitHub Actions to Render (API) and Neon (database). The React + TypeScript frontend is in progress.

**Live API:** https://reddit-clone-u5cd.onrender.com — try [`/health`](https://reddit-clone-u5cd.onrender.com/health) or [`/posts/`](https://reddit-clone-u5cd.onrender.com/posts/)

> The API runs on Render's free tier: after 15 minutes without traffic it goes to sleep,
> and the next request takes about a minute while it wakes up. Requests after that are fast.

---

## Contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Architecture](#architecture)
- [API overview](#api-overview)
- [Design decisions](#design-decisions)
- [Running locally](#running-locally)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project structure](#project-structure)
- [Roadmap](#roadmap)

---

## Features

- **Accounts:** registration and login with bcrypt-hashed passwords and JWT access tokens
- **Communities:** create, list, view and delete (by the creator); names are unique
- **Posts:** create, view and delete posts in a community; a feed of recent posts
- **Nested comments:** replies to replies; deleting a comment keeps the thread intact (soft delete)
- **Voting:** up/down votes on posts and comments, with scores kept consistent with the vote records
- **Consistent errors:** every error, including unexpected server errors, is returned as JSON without internal details

## Tech stack

| Layer | Technology |
|---|---|
| API | Python 3.12, Flask 3, Flask-SQLAlchemy, Flask-Migrate (Alembic), Flask-JWT-Extended, bcrypt, flask-cors |
| Database | PostgreSQL (Neon in production) |
| Server | gunicorn in a Docker container (`python:3.12-slim`, non-root user) |
| Tests | pytest, run against a real PostgreSQL database |
| CI/CD | GitHub Actions → migrations on Neon → deploy hook on Render |
| Frontend (in progress) | React 19, TypeScript, Vite, React Router, Tailwind CSS |

## Architecture

```
                    ┌─────────────────────────── GitHub Actions ───────────────────────────┐
 pull request ────▶ │ test (pytest + PostgreSQL service)                                   │
                    │                                                                      │
 merge to main ───▶ │ test ──▶ migrate (flask db upgrade, owner role) ──▶ deploy (hook) ───┼──┐
                    └──────────────────────────────────────────────────────────────────────┘  │
                                                                                              ▼
 client ──HTTPS──▶  Render: Docker image ─ gunicorn ─ Flask API ──SSL──▶ Neon: PostgreSQL
                    (health check /health)            (app role: read/write data only)
```

- **Two database roles:** the API connects as a role that can only read and write rows; migrations run as the
  owner role, from CI only. The running service never holds credentials that can change the schema.
- **Schema first, then code:** CI migrates the database before triggering the deploy, and any failing step
  stops the pipeline. Migrations are written to be backward-compatible, so the previous version keeps working
  during a deploy.
- **Fail fast on configuration:** each environment has its own config class that refuses to start when a
  required setting is missing or unsafe (e.g. a short JWT key or a non-HTTPS CORS origin in production).

## API overview

All request and response bodies are JSON. Protected endpoints require `Authorization: Bearer <token>`
from `/auth/login`.

<!-- Keep in sync with: flask --app app routes -->

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | | Liveness check |
| `POST` | `/auth/register` | | Create an account |
| `POST` | `/auth/login` | | Get an access token |
| `GET` | `/auth/me` | ✓ | The current user |
| `GET` | `/communities/` | | List communities |
| `POST` | `/communities/` | ✓ | Create a community |
| `GET` | `/communities/<id>` | | One community |
| `DELETE` | `/communities/<id>` | ✓ | Delete (creator only); removes its posts and comments |
| `GET` | `/communities/<id>/posts` | | Posts in a community |
| `GET` | `/posts/` | | Recent posts feed |
| `POST` | `/posts/` | ✓ | Create a post |
| `GET` | `/posts/<id>` | | One post |
| `DELETE` | `/posts/<id>` | ✓ | Delete (author only) |
| `GET` | `/posts/<id>/comments` | | Comments on a post |
| `POST` | `/posts/<id>/vote` | ✓ | Vote `1`, `-1`, or `0` to remove the vote |
| `POST` | `/comments/` | ✓ | Create a comment or a reply (`parent_id`) |
| `GET` | `/comments/<id>` | | One comment |
| `DELETE` | `/comments/<id>` | ✓ | Soft delete (author only): content replaced, replies kept |
| `POST` | `/comments/<id>/vote` | ✓ | Vote `1`, `-1`, or `0` |

Example:

```bash
API=https://reddit-clone-u5cd.onrender.com

curl -X POST $API/auth/register -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"a-long-test-password"}'

TOKEN=$(curl -s -X POST $API/auth/login -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"a-long-test-password"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

curl $API/auth/me -H "Authorization: Bearer $TOKEN"
```

Errors use one shape, `{"error": "<message>"}`, with the matching status code
(400 invalid input, 401 missing/invalid token, 403 not allowed, 404 not found, 405 wrong method,
409 conflict such as a taken name, 500 unexpected error).

## Design decisions

- **Nested comments as an adjacency list:** each comment stores its `parent_id`; a comment and its reply must
  belong to the same post.
- **Denormalized vote scores:** each post and comment stores its score for fast reads, while the vote tables
  remain the source of truth (one row per user and item, enforced by a composite primary key). A vote of `0`
  removes the user's vote instead of storing a zero.
- **Soft delete for comments:** deleting a comment replaces its content but keeps the row, so replies survive.
- **Uniqueness enforced by the database:** community names have a unique constraint; the API turns a
  violation into `409` rather than relying on a check-then-insert in Python.
- **Strict input validation:** wrong types (e.g. a string id, a boolean vote) are rejected with `400` before
  any database access.

More detail: [`docs/schema.md`](docs/schema.md) (schema and diagram) and [`docs/bugs.md`](docs/bugs.md)
(bugs found and fixed, mostly test-first).

## Running locally

### Prerequisites

- Python 3.12
- PostgreSQL (16 or newer; production runs 18)
- Node.js, for the frontend
- Docker, optional, to run the production image

### 1. Database

As the Postgres superuser (`sudo -u postgres psql`), create an owner role (migrations and tests)
and an app role (the running API):

```sql
CREATE ROLE reddit_clone LOGIN;
\password reddit_clone
CREATE ROLE reddit_clone_app LOGIN;
\password reddit_clone_app
CREATE DATABASE reddit_clone OWNER reddit_clone;
CREATE DATABASE reddit_clone_test OWNER reddit_clone;
```

Then connect to `reddit_clone` **as `reddit_clone`** and grant the app role data access, including tables
created by future migrations:

```sql
GRANT CONNECT ON DATABASE reddit_clone TO reddit_clone_app;
GRANT USAGE ON SCHEMA public TO reddit_clone_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO reddit_clone_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO reddit_clone_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO reddit_clone_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO reddit_clone_app;
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env        # then fill in the values (see below)
flask db upgrade            # builds the schema, as the owner role
flask run                   # http://localhost:5000
```

`.env` keys:

| Key | Value |
|---|---|
| `APP_ENV` | `development` |
| `DATABASE_URL` | `postgresql://reddit_clone_app:<password>@localhost:5432/reddit_clone` |
| `MIGRATION_DATABASE_URL` | `postgresql://reddit_clone:<password>@localhost:5432/reddit_clone` (used only by `flask db` commands) |
| `TEST_DATABASE_URL` | `postgresql://reddit_clone:<password>@localhost:5432/reddit_clone_test` (name must end in `_test`) |
| `JWT_SECRET_KEY` | at least 64 characters: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `CORS_ORIGINS` | optional in development (defaults to the Vite dev server); comma-separated `https://` origins in production |

### 3. Frontend

```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173
```

<!-- TODO: confirm the API base URL variable name used in frontend/src (e.g. VITE_API_URL) -->
The API base URL is read from a `VITE_` environment variable in `frontend/.env`.

### 4. Production image (optional)

```bash
cd backend
docker build -t reddit-clone-api .
docker run --rm -p 8001:8000 --env-file .env.docker reddit-clone-api
```

`.env.docker` holds the same keys as `.env`, but the database host must be reachable from inside the
container (e.g. `host.docker.internal` with Docker Desktop), `CORS_ORIGINS` must be an `https://` origin,
and values must not be quoted. The image runs as a non-root user and contains no secrets; all
configuration comes from the environment.

## Testing

```bash
cd backend
pytest              # or: pytest -W error  (fail on any warning)
```

- 150+ tests against a real PostgreSQL database (`TEST_DATABASE_URL`); tables are created once per run
  and emptied after every test, so tests are independent of each other.
- Tests check outcomes, not just status codes: a rejected request (401/403/400) must leave the database
  unchanged, including denormalized vote scores.
- Many bugs were found test-first: the failing test is committed before the fix, so the history shows each
  bug and its fix.
- CI runs the suite on every pull request against PostgreSQL 18 (the production version); merging requires
  a green run.

## Deployment

Merging to `main` runs `.github/workflows/ci.yml`:

1. **test:** the full test suite.
2. **migrate:** `flask db upgrade` against Neon, as the owner role. Credentials come from the `production`
   GitHub environment, available only to this job and the next one.
3. **deploy:** calls Render's deploy hook. Render builds the Docker image from `backend/`, starts it, and
   switches traffic only after `/health` responds.

Any failing step stops the pipeline, and the previous version keeps running. Render's auto-deploy is off,
so code never goes live before its migrations have run.

## Project structure

```
backend/
  app/                 Flask application package (app factory, models, routes)
  migrations/          Alembic migrations
  tests/               pytest suite
  config.py            per-environment configuration with startup checks
  gunicorn.conf.py     server settings (port and workers from the environment)
  Dockerfile           production image
docs/                  schema and bug notes
frontend/              React + TypeScript client (in progress)
.github/workflows/     CI/CD
```

## Roadmap

- [x] REST API with authentication, communities, posts, nested comments and voting
- [x] Test suite, CI, and test-first bug fixing
- [x] Docker image, least-privilege database roles, CI/CD to Render and Neon
- [ ] Frontend: authentication, forms, voting, community pages
- [ ] Ranked feed ("hot" and "best") with cursor pagination
- [ ] Load testing with seeded data, query optimization
- [ ] Rate limiting and structured logging; deploy the frontend
