from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.api_router import api_router
from config.config import config
from api.auth import create_access_token
from datetime import timedelta

# 创建一个测试用的 FastAPI 应用
app = FastAPI()
app.include_router(api_router)

client = TestClient(app)

def get_test_token():
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": "johndoe"}, expires_delta=access_token_expires
    )
    return access_token

def test_api_version_and_prefix():
    api_config = config.get_api_config()
    expected_version = api_config['version']
    expected_prefix = f"/api/{expected_version}"

    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"{expected_prefix}/test", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Test route"
    assert response.json()["version"] == expected_version
    assert response.json()["user"] == "johndoe"

def test_authentication():
    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/test", headers=headers)
    assert response.status_code == 200
    assert response.json()["user"] == "johndoe"