from fastapi.testclient import TestClient
from api.fastapi_center import fastapi_center

client = TestClient(fastapi_center.app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_read_hello():
    response = client.get("/hello/FastAPI")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello FastAPI"}

def test_get_cache():
    response = client.get("/cache/test_key")
    assert response.status_code == 200
    assert "key" in response.json()
    assert "value" in response.json()

def test_set_cache():
    response = client.post("/cache/test_key?value=test_value")
    assert response.status_code == 200
    assert response.json() == {"message": "Cache set successfully"}
