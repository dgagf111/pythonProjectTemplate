from fastapi.testclient import TestClient
from api.fastapi_center import fastapi_center

client = TestClient(fastapi_center.app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
