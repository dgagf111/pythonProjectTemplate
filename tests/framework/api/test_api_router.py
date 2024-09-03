from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.api_router import api_router
from config.config import config
from api.auth import create_access_token, create_user
from datetime import timedelta
from db.mysql.mysql import MySQL_Database
from api.auth_models import User

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
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return access_token
    finally:
        session.close()

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