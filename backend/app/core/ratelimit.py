"""Lightweight in-memory rate limiter (per client IP, sliding window).

Kept dependency-free and simple; suitable for single-process dev/small deploys.
For multi-worker production, prefer a shared store (e.g. Redis) — see TODO.
"""
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

# ip -> (deque of recent request timestamps)
_requests: dict[str, deque] = defaultdict(deque)


def rate_limit(max_requests: int = 30, window_seconds: int = 60):
    """Return an async FastAPI dependency that limits requests per client IP."""

    async def limiter(request: Request):
        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()

        window = _requests[ip]
        while window and now - window[0] > window_seconds:
            window.popleft()

        if len(window) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests, please slow down.",
            )
        window.append(now)

    return limiter
