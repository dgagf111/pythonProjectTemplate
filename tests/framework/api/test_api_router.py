from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.api_router import api_router
from config.config import config
from api.auth.auth_service import create_access_token, create_user, ALGORITHM, SECRET_KEY, get_current_user
from datetime import timedelta
from db.mysql.mysql import MySQL_Database
from api.auth.auth_models import User
from jose import jwt

# 创建一个测试用的 FastAPI 应用
app = FastAPI()
app.include_router(api_router)

client = TestClient(app)

import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config.config import config

@pytest.fixture(autouse=True)
def clean_test_user():
    db = MySQL_Database()
    session = db.get_session()
    try:
        session.query(User).filter_by(username="testuser").delete()
        session.commit()
    finally:
        session.close()

@pytest.fixture(scope="module")
def db():
    db = MySQL_Database()
    yield db
    db.close_session()

@pytest.fixture(scope="function")
def session(db):
    session = db.get_session()
    yield session
    session.close()

def setup_test_user():
    db = MySQL_Database()
    session = db.get_session()
    try:
        existing_user = session.query(User).filter_by(username="testuser").first()
        if existing_user:
            return existing_user
        test_user = create_user(session, "testuser", "testpassword", "test@example.com")
        session.refresh(test_user)
        return test_user
    finally:
        session.close()

def get_test_token():
    test_user = setup_test_user()
    db = MySQL_Database()
    session = db.get_session()
    try:
        user = session.query(User).filter_by(username=test_user.username).first()
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username}, username=user.username, expires_delta=access_token_expires
        )
        return access_token
    finally:
        session.close()

# 设置预期的 API 前缀
api_config = config.get_api_config()
expected_version = api_config.get('api_version', 'v1')
expected_prefix = f"/api/{expected_version}"

def test_api_version_and_prefix():
    api_config = config.get_api_config()
    expected_version = api_config.get('api_version', 'v1')  # 使用默认值 'v1'
    expected_prefix = f"/api/{expected_version}"

    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"{expected_prefix}/test", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    assert response.json()["message"] == "Test route"
    assert response.json()["version"] == expected_version
    assert response.json()["user"] == "testuser"

def test_authentication():
    api_config = config.get_api_config()
    expected_version = api_config.get('api_version', 'v1')  # 使用默认值 'v1'
    expected_prefix = f"/api/{expected_version}"

    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"{expected_prefix}/test", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    assert response.json()["user"] == "testuser"

def test_create_access_token():
    username = "testuser"
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data={"sub": username}, username=username, expires_delta=expires_delta)
    
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == username
    assert "exp" in decoded

def test_invalid_token():
    invalid_token = "invalid_token"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = client.get(f"{expected_prefix}/test", headers=headers)
    assert response.status_code == 401

def test_expired_token():
    expired_token = create_access_token(data={"sub": "testuser"}, username="testuser", expires_delta=timedelta(minutes=-1))
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get(f"{expected_prefix}/test", headers=headers)
    assert response.status_code == 401

def test_unauthenticated_access():
    response = client.get(f"{expected_prefix}/test")
    assert response.status_code == 401

def test_login_process():
    setup_test_user()  # 确保测试用户存在
    response = client.post(f"{expected_prefix}/token", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# 这个测试可能需要模拟数据库会话
def test_get_current_user(mocker):
    mock_get_user = mocker.patch('api.auth.auth_service.get_user')
    mock_get_user.return_value = User(username="testuser")  # 假设User是你的用户模型
    
    token = create_access_token(data={"sub": "testuser"}, username="testuser")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"{expected_prefix}/test", headers=headers)
    assert response.status_code == 200
    assert response.json()["user"] == "testuser"