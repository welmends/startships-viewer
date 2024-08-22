import pytest
from fastapi import status
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_get_starships_authorization_fails():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/starships")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Missing token"}


@pytest.mark.asyncio
async def test_get_starships_with_invalid_pagination(mock_auth_jwt):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        params = {"page": -1, "page_size": 10}
        headers = {"Authorization": "Bearer your_valid_token"}
        response = await ac.get("/api/starships", params=params, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "page and page_size must be positive integers greater than zero"
    }


@pytest.mark.asyncio
async def test_get_starships_success(mock_auth_jwt):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        params = {"page": 1, "page_size": 10}
        headers = {"Authorization": "Bearer your_valid_token"}
        response = await ac.get("/api/starships", params=params, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.json()
    assert isinstance(response.json()["results"], list)
