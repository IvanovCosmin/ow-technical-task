from httpx import AsyncClient
import pytest
from starlette.datastructures import URLPath


from src.routers.usage import router as usage_router, usage

@pytest.mark.anyio()
async def test_usage_endpoint_returns_correct_structure(api_client: AsyncClient):
    # this is not an amazing test as the route handler rather simple
    # I am doing this to illustrate what I would do in more complex scenarios
    PATH_GET_USAGE: URLPath = usage_router.url_path_for(usage.__name__)    
    response =  await api_client.get(PATH_GET_USAGE)

    assert response.status_code == 200

    response_data = response.json()
    assert "usage" in response_data.keys() 
