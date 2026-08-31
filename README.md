# Academy Operations API

REST API (FastAPI) that exposes the operations of the Escuela Hopi
`academy-operations` portal so it can be consumed by the mobile app. It connects
to the **same MySQL** used by the PHP portal and reuses the `cleanup_events`
table.

## Requirements

- Python 3.9+
- A reachable MySQL with the `academy-operations` schema
  (`escuelahopi/academy-operations/sql/init_cleanup_events.sql`). The
  `cleanup_events` table is created automatically on first access if it does not
  exist.

## Configuration

```bash
cp .env.example .env
# fill in ACADEMY_DB_*, ACADEMY_STAFF_*, ACADEMY_ADMIN_*, OPENAI_*, HOPI_JWT_SECRET
```

The variables use the **same names** as `escuelahopi/env.php`, so you can share
the same configuration as the PHP portal.

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs: `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/auth/login` | Staff login, returns a session token. |
| GET | `/api/v1/profiles/{id}` | Staff member profile. |
| GET | `/api/v1/events?q=` | Cleanup event search. |
| GET | `/api/v1/cleanup/events?page=&per_page=` | Paginated event log. |
| DELETE | `/api/v1/cleanup/orphans` | Runs the orphan-users cleanup. |
| DELETE | `/api/v1/cleanup/logs` | Runs the legacy-logs cleanup. |
| DELETE | `/api/v1/cleanup/cache` | Runs the cache cleanup. |
| DELETE | `/api/v1/cleanup/reset` | Resets the event log (admin basic auth). |
| GET | `/api/v1/admin/overview` | Operations overview (requires admin session). |
| POST | `/api/v1/chat` | Statements assistant (OpenAI). |
| GET | `/api/v1/status` | System status. |

## Quick MySQL for development

```bash
docker run -d --name hopi-mysql -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=academy -p 3306:3306 mysql:8
# .env -> ACADEMY_DB_HOST=127.0.0.1 DB_NAME=academy DB_USER=root DB_PASS=root
```

## Deploy (Render)

This repo includes a `render.yaml` blueprint. On Render: **New -> Blueprint**,
pick the repo, and fill in the `sync:false` environment variables. The service
starts even without a database (the `/` health check returns 200); only the
event/cleanup/reset endpoints need MySQL.
