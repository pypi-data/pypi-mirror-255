import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """Test client (httpx) fixture for making requests to the app."""
    from poaster.app import app

    return TestClient(app)
