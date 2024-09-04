from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
UTC = ZoneInfo("UTC")
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.orm import Session
from api.api_router import api_router, API_PREFIX
from api.auth.token_service import generate_permanent_token
from api.auth.auth_models import User, ThirdPartyToken
from db.mysql.mysql import MySQL_Database

app = FastAPI()
app.include_router(api_router)

client = TestClient(app)

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
def clean_test_user(session):
    session.rollback()
    session.query(User).filter_by(username="testuser").delete()
    session.query(ThirdPartyToken).delete()
    session.commit()
    yield
    session.rollback()
    session.query(User).filter_by(username="testuser").delete()
    session.query(ThirdPartyToken).delete()
    session.commit()

def setup_test_user(session):
    user = User(username="testuser", password_hash="hashed_password", email="test@example.com")
    session.add(user)
    session.commit()
    return user

def test_generate_permanent_token(session):
    user = setup_test_user(session)
    token = generate_permanent_token(session, user.user_id, "test_provider")
    assert token is not None
    stored_token = session.query(ThirdPartyToken).filter_by(user_id=user.user_id).first()
    assert stored_token is not None
    assert stored_token.third_party_token == token  # 使用 third_party_token

def test_third_party_access_with_valid_token(session):
    user = setup_test_user(session)
    token = generate_permanent_token(session, user.user_id, "test_provider")
    response = client.get(f"{API_PREFIX}/third_party_test", headers={"X-API-Key": token})
    assert response.status_code == 200
    assert response.json()["message"] == "Third party access successful"

def test_third_party_access_with_invalid_token():
    response = client.get(f"{API_PREFIX}/third_party_test", headers={"X-API-Key": "invalid_token"})
    assert response.status_code == 401

def test_third_party_access_without_token():
    response = client.get(f"{API_PREFIX}/third_party_test")
    assert response.status_code == 401

def test_revoke_permanent_token(session):
    user = setup_test_user(session)
    token = generate_permanent_token(session, user.user_id, "test_provider")
    
    # 使用token访问
    response = client.get(f"{API_PREFIX}/third_party_test", headers={"X-API-Key": token})
    assert response.status_code == 200
    
    # 撤销token
    third_party_token = session.query(ThirdPartyToken).filter_by(third_party_token=token).first()
    third_party_token.state = -1  # 假设-1表示已撤销
    session.commit()
    
    # 再次尝试使用已撤销的token
    response = client.get(f"{API_PREFIX}/third_party_test", headers={"X-API-Key": token})
    assert response.status_code == 401

def test_permanent_token_expiration(session):
    user = setup_test_user(session)
    token = generate_permanent_token(session, user.user_id, "test_provider")
    
    # 使用token访问
    response = client.get(f"{API_PREFIX}/third_party_test", headers={"X-API-Key": token})
    assert response.status_code == 200
    
    # 模拟token过期
    third_party_token = session.query(ThirdPartyToken).filter_by(third_party_token=token).first()
    third_party_token.expires_at = datetime.now(UTC) - timedelta(days=1)
    session.commit()
    
    # 尝试使用过期的token
    response = client.get(f"{API_PREFIX}/third_party_test", headers={"X-API-Key": token})
    assert response.status_code == 401
