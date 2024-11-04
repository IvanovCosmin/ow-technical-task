import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """
        Redefining event loop because the interaction
        between fastapi and pytest asyncio does not work nicely
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()

    try:
        yield loop
    finally:
        loop.close()

# @pytest.fixture(scope="session")
# def anyio_backend():
#     return "asyncio"
