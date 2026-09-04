# tests/conftest.py
import os
from datetime import datetime, timedelta, UTC

import jwt
import pytest
import pytest_asyncio
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_session
from app.models.document import Document
from app.models.user import User

# Separate database on the same podman-compose Postgres instance (see db/init/02-test-db.sql)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://paper_trail:paper_trail@localhost:5443/paper_trail_test",
)


@pytest_asyncio.fixture(name="async_session")
async def async_session_fixture():
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


# Override get_session dependency. asyncpg connections are bound to the event
# loop that opened them, so the client must share the fixture's loop -- an
# httpx.AsyncClient over ASGITransport does that; the sync TestClient runs
# requests in a separate thread/loop and breaks against real Postgres.
@pytest_asyncio.fixture(name="client")
async def client_fixture(async_session: AsyncSession):
    async def get_session_override():
        yield async_session

    app.dependency_overrides[get_session] = get_session_override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()


# Authentication fixtures
@pytest.fixture
def auth_headers():
    private_key = os.getenv("JWT_PRIVATE_KEY").replace("\\n", "\n")
    payload = {
        "sub": "test_user",
        "role": "user",
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    token = jwt.encode(payload, private_key, algorithm="RS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers():
    private_key = os.getenv("JWT_PRIVATE_KEY").replace("\\n", "\n")
    payload = {
        "sub": "test_admin",
        "role": "admin",
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    token = jwt.encode(payload, private_key, algorithm="RS256")
    return {"Authorization": f"Bearer {token}"}


# Pre-populated test data
@pytest_asyncio.fixture
async def sample_documents(async_session: AsyncSession):
    documents = [
        Document(
            name="Invoice #1024",
            description="Q3 invoice for office supplies",
            status="approved",
        ),
        Document(
            name="Contract - Acme Co",
            description="Vendor services contract with Acme Co",
            status="pending",
        ),
        Document(
            name="Receipt #552",
            description="Receipt for team lunch",
            status="draft",
        ),
    ]
    for document in documents:
        async_session.add(document)
    await async_session.commit()
    return documents


@pytest_asyncio.fixture
async def sample_users(async_session: AsyncSession):
    users = [
        User(email="alice@example.com", name="Alice", role="admin"),
        User(email="bob@example.com", name="Bob", role="user"),
    ]
    for user in users:
        async_session.add(user)
    await async_session.commit()
    return users
