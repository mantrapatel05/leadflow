import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.database.base import Base
from app.database.session import get_db
import app.models


@pytest.fixture
def client(tmp_path):
    from app.main import app

    database_path = tmp_path / "test_leadflow.db"
    database_url = f"sqlite+aiosqlite:///{database_path.as_posix()}"

    async def override_get_db():
        test_engine = create_async_engine(database_url)
        async with test_engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        test_session_factory = async_sessionmaker(
            bind=test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
