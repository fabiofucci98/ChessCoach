# ChessCoach - Project Summary

## 📋 Overview

ChessCoach is a web-based chess analysis application that combines a modern frontend with a powerful backend for processing chess games and positions. It leverages Next.js for the user interface, FastAPI for the API layer, and integrates with the Stockfish chess engine for analysis tasks.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Frontend      │  │   Backend API   │  │  Database   │ │
│  │   Next.js       │  │   FastAPI       │  │ PostgreSQL  │ │
│  │   (Port 3000)   │◄─┤   (Port 8000)  │◄─┤  & Redis    │ │
│  │                 │  │   ┌───────────┐ │  │             │ │
│  └────────┬────────┘  └────────┼───────┘  └─────────────┘ │
│          │                    │                           │
│          │ Celery Worker      │                            │
│          └────────────────────┼───────────────────────────┘
│                               │
│                   Stockfish    │
│                   (Async Tasks)                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Tech Stack

### Frontend
- **Framework:** Next.js 14+ with TypeScript
- **Styling:** Tailwind CSS
- **State Management:** React Hooks (useChessGame)

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **ORM:** SQLAlchemy 2.0 (Async)
- **Database:** PostgreSQL 16
- **Cache/Queue:** Redis
- **Task Queue:** Celery (for Stockfish analysis)

### Infrastructure
- **Containerization:** Docker & Docker Compose
- **Migrations:** Alembic

## 🚀 Key Features

- Interactive chess board visualization
- Game analysis with Stockfish engine
- PGN file loading and game history
- Captured pieces tracking
- Move history panel
- Position evaluation

## 📦 Project Structure

```
chesscoach/
├── docker-compose.yml      # Multi-container orchestration
├── README.md              # Detailed documentation
├── PROJECT_SUMMARY.md     # This file
│
├── backend/               # Python API & Worker
│   ├── app/
│   │   ├── core/         # Config, DB, Celery setup
│   │   ├── migrations/   # Alembic migrations
│   │   ├── models/       # SQLAlchemy models
│   │   ├── tasks/        # Stockfish worker tasks
│   │   └── main.py       # API entry point
│   ├── Dockerfile
│   ├── alembic.ini
│   └── requirements.txt
│
└── frontend/              # Next.js application
    ├── app/              # Next.js App Router pages
    ├── components/       # React components
    │   └── chess/       # Chess-specific UI components
    ├── hooks/            # Custom React hooks
    ├── lib/              # Utility functions
    ├── Dockerfile
    └── package.json
```

## 🐳 Quick Start with Docker

```bash
# Build and start all services
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down
```

## 🌐 Service Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main application UI |
| API Docs | http://localhost:8000/docs | Swagger API documentation |
| PostgreSQL | localhost:5432 | Primary database |
| Redis | localhost:6379 | Cache & message broker |

## 📝 Notes

- Backend handles asynchronous Stockfish analysis via Celery workers
- Frontend provides real-time chess board interactions
- Database stores game history, positions, and user data
- All services are containerized for easy deployment
