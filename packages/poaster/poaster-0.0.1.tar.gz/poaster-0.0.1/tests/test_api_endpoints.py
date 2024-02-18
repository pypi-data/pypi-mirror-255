from fastapi.testclient import TestClient


def test_api_help_docs_status_code(client: TestClient):
    response = client.get("/api/v1/docs")
    assert response.status_code == 200
