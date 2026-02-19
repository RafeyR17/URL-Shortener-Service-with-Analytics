import pytest
from httpx import AsyncClient
from app.main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_shorten_url():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            f"{settings.API_V1_STR}/shorten",
            json={"original_url": "https://google.com", "expire_days": 1}
        )
        assert response.status_code == 200
        data = response.json()
        assert "short_code" in data
        assert data["original_url"] == "https://google.com/"

@pytest.mark.asyncio
async def test_stats_not_found():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"{settings.API_V1_STR}/stats/nonexistent")
        assert response.status_code == 404
