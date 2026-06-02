import asyncio
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.database.session import get_session
from app.main import app


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("data") / "test_support_tickets.db"
    return path


@pytest.fixture(scope="session")
async def test_engine(test_db_path):
    database_url = f"sqlite+aiosqlite:///{test_db_path}"
    engine = create_async_engine(database_url, echo=False, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    async_session = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
def client(test_engine, db_session):
    async_sessionmaker = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_session():
        async with async_sessionmaker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()