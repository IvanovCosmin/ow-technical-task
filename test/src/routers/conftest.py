import pytest
from src.app import app

@pytest.fixture()
async def api_client():
    from httpx import ASGITransport, AsyncClient
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        yield client