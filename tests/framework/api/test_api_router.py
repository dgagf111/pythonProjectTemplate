from fastapi.testclient import TestClient
from fastapi import FastAPI
from pythonprojecttemplate.api.api_router import api_router, API_PREFIX
from pythonprojecttemplate.api.auth.token_service import create_tokens, revoke_tokens
from pythonprojecttemplate.config.config import config
from pythonprojecttemplate.api.auth.auth_service import create_access_token, create_user, ALGORITHM, SECRET_KEY, get_current_user, get_password_hash
from datetime import timedelta
from pythonprojecttemplate.db.mysql.mysql import MySQL_Database
from pythonprojecttemplate.api.models.auth_models import User
from jose import jwt
from pythonprojecttemplate.api.exception.custom_exceptions import InvalidCredentialsException, InvalidTokenException, TokenRevokedException, UserNotFoundException
from pythonprojecttemplate.api.models.result_vo import ResultVO
from main import app
from sqlalchemy.exc import OperationalError

app.include_router(api_router)

client = TestClient(app)

import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from pythonprojecttemplate.config.config import config

# 检查数据库连接是否可用
def check_database_connection():
    try:
        db = MySQL_Database()
        session = db.get_session()
        session.execute("SELECT 1")
        session.close()
        return True
    except OperationalError:
        return False

# 如果数据库不可用，跳过所有测试
pytestmark = pytest.mark.skipif(
    not check_database_connection(),
    reason="数据库连接不可用，跳过API测试"
)

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

def setup_test_user(session):
    existing_user = session.query(User).filter_by(username="testuser").first()
    if existing_user:
        return existing_user
    hashed_password = get_password_hash("testpassword")
    test_user = User(username="testuser", password_hash=hashed_password, email="test@example.com")
    session.add(test_user)
    session.commit()
    return test_user

def get_test_token():
    db = MySQL_Database()
    session = db.get_session()
    try:
        test_user = setup_test_user(session)
        access_token, _ = create_tokens(test_user.username)
        return access_token
    finally:
        session.close()

# 设置预期的 API 前缀
expected_prefix = API_PREFIX

def test_api_version_and_prefix():
    api_config = config.get_api_config()
    expected_version = api_config.get('api_version', 'v1')
    expected_prefix = f"/api/{expected_version}"

    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"{expected_prefix}/test", headers=headers)
    result = ResultVO(**response.json())
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    assert result.code == 200
    assert result.message == "success"
    assert result.data["message"] == "Test route"
    assert result.data["version"] == expected_version
    assert result.data["user"] == "testuser"

def test_authentication():
    api_config = config.get_api_config()
    expected_version = api_config.get('api_version', 'v1')  # 使用默认值 'v1'
    expected_prefix = f"/api/{expected_version}"

    token = get_test_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"{expected_prefix}/test", headers=headers)
    data = response.json()["data"]
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    assert data["user"] == "testuser"

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
    db = MySQL_Database()
    session = db.get_session()
    try:
        setup_test_user(session)  # 确保测试用户存在
        response = client.post(f"{expected_prefix}/token", data={"username": "testuser", "password": "testpassword"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
        
        result = response.json()
        assert result["code"] == 200
        assert result["message"] == "success"
        
        data = result["data"]
        assert "access_token" in data
        assert "token_type" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    finally:
        session.close()

# 这个测试可能需要模拟数据库会话
def test_get_current_user(session):
    user = setup_test_user(session)
    access_token, _ = create_tokens(user.username)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"{expected_prefix}/test", headers=headers)
    data = response.json()['data']
    assert response.status_code == 200
    assert data["user"] == "testuser"

# 添加以下测试函数

def test_invalid_credentials():
    response = client.post(f"{expected_prefix}/token", data={"username": "wronguser", "password": "wrongpassword"})
    print("response11", response)
    print("response11.json()", response.json())
    assert response.json()["code"] == 401
    assert response.json()['message'] == "Incorrect username or password"

def test_invalid_token_exception():
    invalid_token = "invalid_token"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = client.get(f"{expected_prefix}/test", headers=headers)
    assert response.status_code == 401
    print(response.json())
    assert response.json() == {"detail": "Invalid token"}

def test_token_revoked_exception(session):
    user = setup_test_user(session)
    access_token, _ = create_tokens(user.username)
    revoke_tokens(user.username)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"{expected_prefix}/test", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Token has been revoked"}

def test_user_not_found_exception(session):
    # 首先创建一个用户并获取token
    user = setup_test_user(session)
    access_token, _ = create_tokens(user.username)
    
    # 然后删除这个用户
    session.delete(user)
    session.commit()
    
    # 尝试使用token访问
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"{expected_prefix}/test", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_exception_handling():
    api_config = config.get_api_config()
    expected_version = api_config.get('api_version', 'v1')
    expected_prefix = f"/api/{expected_version}"

    response = client.get(f"{expected_prefix}/test_exception")
    print("Response status code:", response.status_code)
    print("Response content:", response.content)
    
    assert response.status_code == 500
    
    try:
        result = response.json()
        print("Response JSON:", result)
    except Exception as e:
        print("Failed to parse response as JSON:", str(e))
        raise
    
    assert "detail" in result, "Response should contain 'detail' key"
    assert result["detail"] == "测试异常", f"Expected message '测试异常', got {result.get('detail')}"