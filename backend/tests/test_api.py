"""API smoke tests against a dedicated Postgres test database.

These are skipped unless TEST_DATABASE_URL is set, e.g.:
    TEST_DATABASE_URL=postgresql+asyncpg://chesscoach:chesscoach_secret@localhost:5432/chesscoach_test_db
"""
import os
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.main import app
from app.core.database import Base, get_db

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

pytestmark = pytest.mark.skipif(not TEST_DATABASE_URL, reason="TEST_DATABASE_URL not set")


@pytest.fixture(scope="session")
async def app_client():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    TestSession = async_sessionmaker(engine, expire_on_commit=False)

    # Create a clean schema for the test database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def _override_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = _override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.pop(get_db, None)
    await engine.dispose()


async def test_health(app_client):
    resp = await app_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


async def test_register_then_me(app_client):
    uname = f"user_{uuid.uuid4().hex[:8]}"
    reg = await app_client.post(
        "/auth/register",
        json={"username": uname, "email": f"{uname}@example.com", "password": "secret123"},
    )
    assert reg.status_code == 201
    token = reg.json()["access_token"]

    me = await app_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == uname
