import pytest
from fastapi_jwt_auth import AuthJWT

from app.db import async_db, seed_database

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_auth_jwt(monkeypatch):
    def mock_jwt_required(*args, **kwargs):
        pass

    monkeypatch.setattr(AuthJWT, "jwt_required", mock_jwt_required)


@pytest.fixture(scope="session", autouse=True)
async def seed_test_db():
    await seed_database()


@pytest.fixture(autouse=True)
async def clear_test_db():
    yield
    # Limpa o banco de dados após cada teste
    await async_db.starships.delete_many({})
    await async_db.manufacturers.delete_many({})
    await async_db.users.delete_many({})
    await async_db.search.delete_many({})
