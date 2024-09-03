from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.api_router import api_router
from config.config import config

# 创建一个测试用的 FastAPI 应用
app = FastAPI()
app.include_router(api_router)

client = TestClient(app)

def test_api_version_and_prefix():
    api_config = config.get_api_config()
    expected_version = api_config['version']
    expected_prefix = f"/api/{expected_version}"

    response = client.get(f"{expected_prefix}/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Test route", "version": expected_version}

    # 测试错误的前缀
    response = client.get("/api/wrong_version/test")
    assert response.status_code == 404

    # 测试没有前缀
    response = client.get("/test")
    assert response.status_code == 404