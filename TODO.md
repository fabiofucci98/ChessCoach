# ChessCoach - Development TODO

## Phase 1: Authentication & User Management
- [x] Create backend auth endpoints (register, login, me)
- [x] Add password hashing (bcrypt)
- [x] Add JWT token authentication
- [x] Create frontend login/register page
- [x] Add auth state management (context/hook)
- [x] Protect routes with auth middleware

## Phase 2: Frontend Style & Layout Review
- [x] Create a proper app shell with header/navigation
- [x] Improve overall visual design (dark theme, consistent styling)
- [x] Create dashboard layout with sections
- [x] Add responsive design improvements

## Phase 3: Chess.com Integration
- [x] Backend: Add chess.com API client to fetch user games
- [x] Backend: Add endpoint to sync games from chess.com
- [x] Backend: Add endpoint to list user's games
- [x] Backend: Add endpoint to get a specific game
- [x] Frontend: Add chess.com username input in settings
- [x] Frontend: Add game list/selector component
- [x] Frontend: Add "sync games" button with polling
- [x] Frontend: Display last 10 games + new games

## Phase 4: Game Analysis & Bad Move Tracking
- [x] Backend: Add BadMove model (position, chosen move, best move, counter)
- [x] Backend: Analyze all moves in a game, identify bad moves
- [x] Backend: Increment counter when same bad move is repeated
- [x] Backend: Add endpoint to get user's bad moves
- [x] Frontend: Add bad moves panel/dashboard
- [x] Frontend: Show bad moves with position, chosen move, best move
- [x] Frontend: Show repeat counter for each bad move

## Phase 5: Additional Features (Ideas)
- [ ] Opening repertoire tracking
- [ ] Time management analysis (move times)
- [ ] Blunder/accuracy score per game
- [ ] Progress tracking over time
- [ ] Weekly/monthly reports
- [ ] Practice mode for bad moves
- [ ] Tactics trainer based on missed tactics

---

## Phase 6: Git & Project Foundation
- [x] Initialize git repo + baseline commit (currently NO git repo!)
- [x] Review root .gitignore (add .next, *.pyc, .venv, coverage)
- [x] Add committed .env.example files (root + backend) documenting required vars

## Phase 7: Fix Play-vs-Stockfish (BUG)
- [x] Backend play.py: Stockfish reply uses best move from `board_before` instead of `board_after` -> use `result_after["pv"][0]` (root cause)
- [x] Frontend PlayVsStockfish: stale closure on color toggle -> switching to Black never triggers stockfishFirstMove()
- [x] Frontend PlayVsStockfish: enforce turns + player color in onDrop (currently can move both sides)
- [ ] (Design) Server-side game/session state instead of 100% client-side
- [x] Play-vs-Stockfish: WRONG checkmate message — after Stockfish's reply, isCheckmate() means the player LOST (currently says "🏆 you win"); also detect the player's own checkmate after their move and show the correct win/lose/draw message
- [x] Play-vs-Stockfish: when a move is flagged as a mistake, the game keeps playing ("let's review it") — pause the game and offer to review the mistake (show the best move / position) instead of silently continuing

## Phase 8: Docker Fixes
- [ ] Add backend/.dockerignore (exclude ~99MB .venv from build context - biggest build win)
- [ ] Entrypoint script: run `alembic upgrade head` before uvicorn (README claims auto-migrate but nothing does it)
- [ ] Add healthchecks for db/redis + `depends_on: condition: service_healthy`
- [ ] Split dev/prod compose (remove --reload from prod, don't publish db/redis ports in prod)
- [ ] Frontend: multi-stage Dockerfile with `next build && next start` for prod (drop `npm ci || npm install` hack)
- [ ] Redis auth + resource limits (prod)
- [ ] Consider newer Stockfish build (apt version is old)

## Phase 9: Backend Tests (pytest)
- [ ] Add pytest + async test setup (httpx ASGITransport)
- [ ] Unit: sm2_update (puzzles.py)
- [ ] Unit: parse_chess_com_game (games.py)
- [ ] Unit: eval_diff -> mistake_level classification (play.py)
- [ ] Unit: security.py (hash/verify/JWT)
- [ ] Integration w/ Stockfish: analyze_position, play_move, analyze_game_moves
- [ ] API tests against test Postgres

## Phase 10: Architecture / Performance
- [ ] Move blocking SimpleEngine.analyse off the event loop (Celery worker exists but is a stub: tasks/engine.py ping_worker) or anyio.to_thread
- [ ] Centralize STOCKFISH_PATH in config.py (currently hardcoded in stockfish.py, play.py, analysis.py + find_stockfish in main.py)
- [ ] Factor duplicated bad-move dedupe/increment logic (games.py + analysis.py)
- [ ] Replace deprecated datetime.utcnow() with timezone-aware datetime.now(UTC)
- [ ] Pin requirements.txt (currently unpinned)
- [ ] Bump BadMove.move_played/best_move to String(50) (SAN can exceed 20)

## Phase 11: Frontend Tests
- [ ] Add Vitest + React Testing Library
- [ ] useChessGame.ts unit tests
- [ ] PlayVsStockfish + PuzzleTrainer component tests
- [ ] Playwright E2E smoke (login -> sync -> puzzle)

## Phase 12: Security & Hardening
- [ ] SECRET_KEY: no hardcoded dev default (from env, fail fast in prod)
- [ ] Make CORS origins configurable (hardcoded localhost:3000)
- [ ] Rate limiting on /analyze, /play/move, /games/sync
- [ ] Make SQLAlchemy echo configurable (hardcoded True)

## Phase 13: Feature Ideas
- [ ] Play-vs-Stockfish: real game mode, difficulty levels (UCI skill), Hint button, persist played games
- [ ] Eval curve / centipawn chart per game + click-to-jump
- [ ] Opening explorer / opening-name detection from PGN
- [ ] Rating & progress tracking (ELO over time, mistake-rate trends)
- [ ] Lichess support alongside chess.com
- [ ] Puzzle UX: tap-to-move, multi-move puzzles
- [ ] Sync-complete notifications

---

## Phase 14: Improvements to Existing Features

### Auth
- [ ] Fix OAuth2 mismatch: `tokenUrl="/auth/login"` expects JSON, but Swagger's Authorize uses OAuth2 form -> the Authorize button in /docs doesn't work
- [ ] Move tokens from localStorage to httpOnly cookies (localStorage is XSS-exposed)
- [ ] Add refresh-token flow + shorter access-token lifetime (currently 7 days, no refresh)
- [ ] Add password change / reset endpoints
- [ ] Rate-limit login/register + account lockout after repeated failures (brute-force protection)
- [ ] Make username lookup case-insensitive (currently exact match -> "Bob" and "bob" can both register)
- [ ] Add email verification flow
- [ ] Consistent error response format across all endpoints
- [ ] Validate `sync_limit` and `chess_com_username` with Pydantic models instead of raw `dict` bodies

### Chess.com integration
- [ ] Move the background sync from `asyncio.create_task` + shared in-memory state to Celery (worker exists but is a stub); in-memory `_sync_progress`/`_sync_tasks` is lost on restart and fragile
- [ ] Persist sync progress/status in DB instead of in-memory dicts
- [ ] Fix month-fetch loop: `now - 30*i` days can miss/duplicate calendar months; iterate actual year/month pairs
- [ ] Add rate-limit / backoff / retry handling for the chess.com API (429s)
- [ ] Surface per-game sync failures instead of failing the whole sync on one bad game
- [ ] Make `months_back` and per-month limits configurable (hardcoded 6 in the sync call)
- [ ] Handle the edge case where the logged-in user is neither white nor black (currently defaults to black)
- [ ] Avoid re-fetching months already synced (cache/incremental sync)
- [ ] Add a way to cancel or re-trigger a running sync

### Game analysis & bad moves
- [ ] Stop spawning a new Stockfish engine per game/request (reuse a pool); analysis currently blocks the event loop during sync
- [ ] Persist analysis state so re-analyzing the same game doesn't inflate `BadMove.counter` (dedupe per game, not just per position)
- [ ] Add a unique constraint on `(user_id, fen, move_played)` to prevent duplicate rows from races
- [ ] Make eval threshold (-0.3), depth (12), and mate_score configurable
- [ ] Add pagination to `/analysis/bad-moves` (currently only `limit`)
- [ ] Surface invalid-PGN games to the user instead of silently returning `[]`
- [ ] Add indexes on hot columns: `bad_moves(user_id, next_review_at)`, `games(user_id, played_at)`
- [ ] Store a "reviewed/fixed" flag on BadMove and avoid re-flagging already-fixed mistakes
- [ ] Factor the duplicated dedupe-and-increment logic out of `games.py` and `analysis.py`

### Play vs Stockfish
- [ ] Reuse a shared engine instead of `SimpleEngine.popen_uci` on every `/play/move` call
- [ ] Add a difficulty/skill setting (UCI `Skill Level` / depth) instead of a fixed depth-12
- [ ] Return evaluation relative to the player's color (currently always white POV)
- [ ] Add turn/color + game-state enforcement server-side (currently fully client-side, easy to cheat/desync)
- [ ] Add a "Hint" action and an undo button
- [ ] Detect and surface win/draw/checkmate states in the UI
- [ ] Show a move history panel for the current game
- [ ] Handle the `fen == fen_before` (first move) case explicitly

### Puzzle trainer
- [ ] Replace deprecated `datetime.utcnow()` with timezone-aware `datetime.now(UTC)` (puzzles.py)
- [ ] Compare answers by UCI move instead of case-insensitive SAN string (fragile)
- [ ] Validate the submitted move is legal on the puzzle board before grading
- [ ] Persist puzzle stats (solved/attempted are component state, lost on refresh)
- [ ] Add skip/reveal/retry actions and re-queue a failed puzzle soon
- [ ] Support partial credit in `sm2_update` (currently only quality 1 or 5)
- [ ] Fix `fen_before or fen` fallback: when `fen_before` is None the puzzle starts from the wrong side-to-move
- [ ] Add difficulty/type filtering for review sessions

### General backend / frontend polish (existing code)
- [ ] Add a global exception handler for a consistent error shape
- [ ] Add structured logging + request IDs (main.py currently uses `print()`)
- [ ] Move `STOCKFISH_PATH` (and `find_stockfish`) into `config.py`; remove the 3 hardcoded copies
- [ ] Make SQLAlchemy `echo` and CORS origins configurable (both hardcoded today)
- [ ] Replace deprecated `datetime.utcnow()` everywhere (models, routers)
- [ ] Add loading skeletons + error boundaries on the dashboard instead of raw error text
- [ ] Replace 3s/5-min polling with SSE or WebSocket for sync status
- [ ] Add a toast/notification component (currently only inline messages)
- [ ] Add accessibility pass (ARIA labels, keyboard navigation) on the chessboard and buttons
- [ ] Pin backend dependency versions in requirements.txt (currently unpinned)