# ChessCoach - Development Roadmap

> End goal: fully containerize the app and publish it to a Docker registry (Docker Hub / GHCR) so
> anyone can run ChessCoach for themselves with a single command, without cloning/building the source.

## Done (current state)
- Core app works end to end: auth, chess.com sync, engine analysis, bad-move SRS puzzles, play-vs-Stockfish.
- Git repo + baseline commit, .gitignore, .env.example files.
- Play-vs-Stockfish bugs fixed (reply move, color toggle, turn/color enforcement, checkmate/draw messages, mistake pause).
- Docker dev/prod split, healthchecks, auto-migrations, backend .dockerignore, multi-stage frontend build, resource limits.
- Backend: engine moved off the event loop, centralized config/Stockfish, shared upsert_bad_moves, utcnow, pinned deps, String(50)+migration.
- Security: SECRET_KEY fail-fast in prod, configurable CORS/DB echo, per-IP rate limiting.
- Tests: backend pytest suite (18 passing) + frontend Vitest suite (8 passing) + Playwright render smoke.

## Priority Phase: Publish to a Docker Registry (self-hosting)
- [ ] Pick a registry: GitHub Container Registry (GHCR - recommended, repo is on GitHub) vs Docker Hub
- [ ] Choose image strategy: 3 images (api, worker, web), versioned tags (semver) + `latest`
- [ ] Add an open-source LICENSE (e.g. MIT) so others are free to use it
- [ ] GitHub Actions workflow: build multi-arch (linux/amd64 + linux/arm64) and push on tag/release and main
- [ ] Publish prebuilt images and update `docker-compose.yml` to reference `image:` tags (no source build needed for end users)
- [ ] Add a setup script / one-liner that generates a secure `.env` (random SECRET_KEY, postgres/redis passwords) from .env.example
- [ ] Keep published images self-contained: Stockfish bundled in the backend image; no dev bind-mounts / `--reload`
- [ ] Document minimal host requirements + ports, and a reverse-proxy note (expose only web on 443)
- [ ] Secure defaults in published config: strong SECRET_KEY required, CORS easy to configure, rate limits enabled
- [ ] README end-user quick-start: `docker compose up -d` with prebuilt images, visit localhost:3000

## Backend hardening
### Reliability / architecture
- [ ] Move game sync to Celery (worker is a stub); persist sync progress in DB, not in-memory
- [ ] Reuse a single Stockfish engine (pool) instead of spawning one per request
- [ ] Server-side game/session state for play-vs-Stockfish (currently fully client-side)
- [ ] Global exception handler + structured logging with request IDs

### Chess.com sync
- [ ] Fix month-fetch loop (iterate real year/month pairs instead of now-30*i)
- [ ] Add 429 / backoff / retry handling; isolate per-game failures
- [ ] Incremental sync (avoid re-fetching already-synced months); make months_back configurable
- [ ] Handle the user-is-neither-white-nor-black edge case; allow cancel / re-trigger

### Game analysis & bad moves
- [ ] Persist analysis state so re-analyzing a game does not inflate `BadMove.counter` (dedupe per game)
- [ ] Unique constraint on `(user_id, fen, move_played)`; indexes on hot columns
- [ ] Make eval threshold / depth / mate_score configurable
- [ ] Pagination on /analysis/bad-moves; surface invalid-PGN errors to the user
- [ ] Add a reviewed/fixed flag on BadMove

### Play vs Stockfish
- [ ] Difficulty / skill setting (UCI Skill Level / depth), Hint + undo buttons, move-history panel
- [ ] Return evaluation relative to the player color; handle first-move (fen == fen_before) explicitly

### Puzzle trainer
- [ ] Compare answers by UCI (not SAN string); validate move legality
- [ ] Partial credit in SM-2; persist puzzle stats; skip/reveal/retry + requeue failed
- [ ] Fix `fen_before or fen` fallback; add difficulty/type filtering

### Auth & security
- [ ] Fix Swagger /docs Authorize button (OAuth2 form vs JSON login)
- [ ] httpOnly cookies or a refresh-token flow; password change/reset; email verification
- [ ] Rate-limit login + account lockout; case-insensitive usernames; consistent error shape; Pydantic bodies for sync_limit / chess_com_username
- [ ] Redis auth (deferred: needs celery password support + REDIS_PASSWORD env)

### UX polish
- [ ] Loading skeletons + error boundaries; toast/notification component; accessibility pass
- [ ] Replace 3s/5-min polling with SSE or WebSocket for sync status

## Features (ideas)
- [ ] Play-vs-Stockfish: real game mode (turn clock), difficulty levels, persisted games
- [ ] Eval curve / centipawn chart per game with click-to-jump
- [ ] Opening repertoire / explorer + opening-name detection from PGN
- [ ] Blunder/accuracy score per game; ELO & progress tracking; weekly/monthly reports
- [ ] Time-management analysis (move times)
- [ ] Practice mode for bad moves; tactics trainer from missed tactics
- [ ] Lichess support alongside chess.com
- [ ] Puzzle UX: tap-to-move, multi-move puzzles
- [ ] Sync-complete notifications

## Testing (extend)
- [ ] Full Playwright login -> sync -> puzzle flow (currently a render smoke only)
- [ ] Wire the DB-backed API tests into CI (provide a TEST_DATABASE_URL)
- [ ] CI pipeline: run backend pytest + frontend vitest on every PR/push
