# 🔧 ChessCoach – Debugging & Useful Commands

Quick reference for running, inspecting, and debugging the ChessCoach stack.

> **Paths:** `cd C:\Users\fabio\Desktop\chesscoach` (root). Local dev is Windows/PowerShell; the
> Docker commands work anywhere. `api`/`worker`/`web`/`db`/`redis` are the docker-compose service names.

---

## 0. Environment & quick sanity checks

### Endpoints
| What | URL |
| :--- | :--- |
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| **API docs (Swagger)** | http://localhost:8000/docs |
| **Health check** | http://localhost:8000/health |

```powershell
# Health check — reports DB/Stockfish detection status
curl.exe http://localhost:8000/health

# Same via the dockerized API
docker compose exec api python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read())"
```

The `/health` response tells you whether Stockfish was found and its detected path:
- `"stockfish": { "installed": true, "path": "..." }` → good.
- `installed: false` → set `STOCKFISH_PATH` (see §5).

---

## 1. Backend (FastAPI / Python)

```powershell
# Activate the virtualenv (one-time per shell)
.\backend\.venv\Scripts\Activate.ps1

# Run with auto-reload (local dev)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*Required first:* Postgres + Redis must be reachable — either run `docker compose up -d db redis` or have local instances. See §4.

### Alembic (database migrations)
```powershell
# Show current DB revision vs. latest in code
alembic current
alembic heads

# Apply all pending migrations
alembic upgrade head

# Roll back one step / to a specific revision
alembic downgrade -1
alembic downgrade <revision_id>

# Autogenerate a new migration after editing models
alembic revision --autogenerate -m "describe change"
```
> The compose `api` service runs `alembic upgrade head` automatically before uvicorn starts,
> so migrations are applied on startup. Manual commands remain available (see below).

### Celery worker
```powershell
# Run the worker (local)
celery -A app.core.celery_app worker --loglevel=info

# Inspect registered tasks / worker health (local)
celery -A app.core.celery_app inspect registered
celery -A app.core.celery_app inspect ping
```

### Test Stockfish directly
```powershell
# Sanity check: does the configured engine actually run? (uses .env STOCKFISH_PATH)
.\backend\.venv\Scripts\python.exe -c "import os; os.environ.setdefault('STOCKFISH_PATH', r'C:/stockfish/stockfish-windows-x86-64-avx2.exe'); import chess.engine; e=chess.engine.SimpleEngine.popen_uci(os.environ['STOCKFISH_PATH']); print('uci ok'); e.quit()"
```

---

## 2. Frontend (Next.js)

```powershell
Set-Location frontend

npm run dev        # dev server (localhost:3000)
npm run build      # production build (also runs type-check / lint via next)
npm run lint       # eslint
npm run start      # serve production build
```
Useful build/debug views:
```powershell
# Confirm the API base URL the frontend will use
Get-ChildItem Env:NEXT_PUBLIC_API_URL
# Default is http://localhost:8000 (see frontend/src/lib/api.ts)
```

---

## 3. Docker (docker compose)

```powershell
# Service status
docker compose ps

# Live logs (one service or all)
docker compose logs -f            # all
docker compose logs -f api        # just backend
docker compose logs -f web        # just frontend
docker compose logs -f worker     # just celery

# Rebuild after dependency/code changes
docker compose up -d --build

# Restart a single service
docker compose restart api

# Enter a running container
docker compose exec api  /bin/sh
docker compose exec web  /bin/sh

# Run a shell inside the DB / Redis containers
docker compose exec db    psql -U $env:POSTGRES_USER -d $env:POSTGRES_DB
docker compose exec redis redis-cli

# Full teardown (keeps DB volume)
docker compose down
# Teardown + delete the postgres volume (fresh DB)
docker compose down -v

# Inspect health / exit status
docker inspect --format '{{.State.Health.Status}}' chesscoach_api

---

## 4. Database (PostgreSQL) & Redis

### psql
```powershell
# Connect (local dev — matches backend\.env; use the compose values in Docker)
psql "postgresql://chesscoach:chesscoach_secret@localhost:5432/chesscoach_db"

# Via compose (avoids exposing the port):
docker compose exec db psql -U chesscoach -d chesscoach_db
```

Useful queries:
```sql
\dt                                  -- list tables
SELECT count(*) FROM users;
SELECT id, username, chess_com_username, sync_limit FROM users;
SELECT count(*) FROM games;
SELECT count(*) FROM bad_moves;
SELECT move_played, best_move, counter, next_review_at
  FROM bad_moves ORDER BY counter DESC LIMIT 20;
SELECT id, external_game_id, is_analyzed, played_at FROM games ORDER BY played_at DESC LIMIT 10;
```

### Redis
```powershell
redis-cli ping          # -> PONG = broker reachable
redis-cli dbsize        # how many keys
redis-cli keys '*'      # list keys (Celery uses celery-task-meta-*, etc.)
```

---

## 5. Common problems → fixes

| Symptom | Cause / check | Fix |
| :--- | :--- | :--- |
| `/health` shows `stockfish.installed: false` | `STOCKFISH_PATH` wrong/missing | Set it in `backend\.env` (Windows) or compose env (Linux: `/usr/games/stockfish`); restart the service |
| Analysis/play returns 500 "engine not found" | Same as above | See `/health`, set path correctly |
| Tables missing on a fresh DB | Migration step failed / wrong DB target | Check `api` logs; rerun `docker compose exec api alembic upgrade head` manually |
| Frontend can't reach API / CORS error | `NEXT_PUBLIC_API_URL` mismatch or CORS origins | Check API is up (`/health`); CORS allow list is in `backend/app/main.py` |
| `docker compose up` fails waiting for DB | No healthcheck + `depends_on` only (see TODO Phase 8) | `docker compose restart api` once db/redis are up, or fix compose |
| Celery task stuck | Redis unreachable | `redis-cli ping` from host/`docker compose exec redis redis-cli ping` |
| Port already in use (3000/8000/5432/6379) | Another process | `docker compose down` or change the left-hand port in `docker-compose.yml` |

---

## 6. Git

```powershell
git status                     # what changed
git --no-pager log --oneline -10
git --no-pager diff            # unstaged changes
git --no-pager diff --cached   # staged changes
git show <commit> --stat
git restore <file>             # discard working-tree changes (careful)
git checkout -- <file>         # older alias for the above
git branch -a
git remote -v
```
> Push model: commit on `main`, then `git push origin main`.

---

## 7. Fast "everything is broken" checklist (in order)

1. `docker compose ps` — are all 5 services up and healthy?
2. `curl.exe http://localhost:8000/health` — DB & Stockfish detection.
3. `docker compose logs -f api` — backend errors/stack traces.
4. `docker compose exec api alembic current` — DB migrated?
5. `docker compose logs -f web worker` — frontend/celery errors.
6. Frontend → check `NEXT_PUBLIC_API_URL` and browser DevTools → Network for the failing request.

```
