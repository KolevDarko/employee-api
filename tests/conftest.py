import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from tests.data.seed_employees import seed_employees_data

from app.db.base import Base
from app.db.session import get_session
from app.main import app


@pytest.fixture(scope="module")
async def engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="module")
async def seeded_engine(engine):
    async with AsyncSession(engine) as session:
        session.add_all(seed_employees_data())
        await session.commit()
    return engine


@pytest.fixture(scope="module")
async def session(seeded_engine):
    async with AsyncSession(seeded_engine) as session:
        yield session


@pytest.fixture
def client(session):
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()
