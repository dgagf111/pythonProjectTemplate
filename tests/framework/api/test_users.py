from fastapi.testclient import TestClient
from api.fastapi_center import fastapi_center

client = TestClient(fastapi_center.app)

def test_get_user():
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "John Doe", "email": "john@example.com"}

    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_create_user():
    user_data = {"id": 2, "name": "Jane Doe", "email": "jane@example.com"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully", "user_id": 2}
