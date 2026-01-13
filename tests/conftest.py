import pytest
import httpx

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the running application"""
    return "http://localhost:8000/api/v1"

@pytest.fixture(scope="function")
def client(base_url):
    """Synchronous client for E2E tests"""
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        yield client
