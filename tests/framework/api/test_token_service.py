import pytest
import time
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from datetime import timedelta
from jose import jwt
from api.auth.token_service import create_tokens, refresh_access_token, revoke_tokens, verify_token
from api.auth.auth_service import SECRET_KEY, ALGORITHM, get_password_hash
from api.api_router import api_router,API_PREFIX
from db.mysql.mysql import MySQL_Database
from api.models.auth_models import User, ThirdPartyToken

app = FastAPI()
app.include_router(api_router)

client = TestClient(app)

expected_prefix = API_PREFIX

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

@pytest.fixture(autouse=True)
def clean_test_data(session):
    session.query(User).filter_by(username="testuser").delete()
    session.commit()

@pytest.fixture(autouse=True)
def clean_test_user(session):
    session.query(User).filter_by(username="testuser").delete()
    session.query(ThirdPartyToken).delete()
    session.commit()

def setup_test_user(session):
    existing_user = session.query(User).filter_by(username="testuser").first()
    if existing_user:
        return existing_user
    hashed_password = get_password_hash("testpassword")
    user = User(username="testuser", password_hash=hashed_password, email="test@example.com")
    session.add(user)
    session.commit()
    return user

def test_create_tokens(session):
    user = setup_test_user(session)
    access_token, refresh_token = create_tokens(user.username)
    
    # 验证访问令牌
    payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == user.username
    assert "exp" in payload
    
    # 验证刷新令牌
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == user.username
    assert payload["type"] == "refresh"
    assert "exp" in payload

def test_refresh_access_token(session):
    user = setup_test_user(session)
    access_token, refresh_token = create_tokens(user.username)
    
    new_access_token, new_refresh_token = refresh_access_token(refresh_token)
    
    # 验证新的访问令牌
    payload = jwt.decode(new_access_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == user.username
    assert "exp" in payload
    
    # 验证新的刷新令牌
    payload = jwt.decode(new_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == user.username
    assert payload["type"] == "refresh"
    assert "exp" in payload

def test_revoke_tokens(session):
    user = setup_test_user(session)
    access_token, _ = create_tokens(user.username)
    
    revoke_tokens(user.username)
    
    # 尝试使用已撤销的令牌
    response = client.get(f"{expected_prefix}/test", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 401, f"Expected 401, got {response.status_code}. Response: {response.json()}"

def test_verify_token(session):
    user = setup_test_user(session)
    access_token, _ = create_tokens(user.username)
    
    try:
        payload = verify_token(access_token)
        assert payload["sub"] == user.username
    except HTTPException:
        pytest.fail("Valid token should not raise HTTPException")

def test_verify_expired_token():
    payload = {"sub": "testuser", "exp": int(time.time()) - 300}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    with pytest.raises(HTTPException) as excinfo:
        verify_token(token)
    assert excinfo.value.status_code == 401

def test_login_and_refresh_flow(session):
    user = setup_test_user(session)
    access_token, refresh_token = create_tokens(user.username)
    
    # 使用访问令牌
    response = client.get(f"{expected_prefix}/test", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
    
    # 刷新令牌
    new_access_token, new_refresh_token = refresh_access_token(refresh_token)
    
    # 使用新的访问令牌
    response = client.get(f"{expected_prefix}/test", headers={"Authorization": f"Bearer {new_access_token}"})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"

def test_logout():
    db = MySQL_Database()
    session = db.get_session()
    try:
        setup_test_user(session)
        response = client.post(f"{expected_prefix}/token", data={"username": "testuser", "password": "testpassword"})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.json()}"
        tokens = response.json()

        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = client.post(f"{expected_prefix}/logout", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"
    finally:
        session.close()
