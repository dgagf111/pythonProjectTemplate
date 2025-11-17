import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete, select, text
from sqlalchemy.exc import OperationalError
from zoneinfo import ZoneInfo

from pythonprojecttemplate.api.api_router import API_PREFIX, api_router
from pythonprojecttemplate.api.auth.token_service import generate_permanent_token
from pythonprojecttemplate.api.main import app
from pythonprojecttemplate.api.models.auth_models import ThirdPartyToken, Token, User
from pythonprojecttemplate.config.config import config
from pythonprojecttemplate.db.mysql.mysql import MySQL_Database

TIME_ZONE = ZoneInfo(config.get_time_zone())

app.include_router(api_router)
client = TestClient(app)


@asynccontextmanager
async def mysql_session():
    db = MySQL_Database()
    session_gen = db.get_session()
    session = await session_gen.__anext__()
    try:
        yield session
    finally:
        try:
            await session.rollback()
        finally:
            await session_gen.aclose()


async def _ping_database() -> None:
    async with mysql_session() as session:
        await session.execute(text("SELECT 1"))


def check_database_connection() -> bool:
    try:
        asyncio.run(_ping_database())
        return True
    except OperationalError:
        return False
    except Exception:
        return False


pytestmark = [
    pytest.mark.skipif(
        not check_database_connection(),
        reason="数据库连接不可用，跳过第三方令牌测试",
    ),
    pytest.mark.asyncio,
]


async def _clear_test_records() -> None:
    async with mysql_session() as session:
        user_ids = select(User.user_id).where(User.username == "testuser")
        await session.execute(delete(ThirdPartyToken).where(ThirdPartyToken.user_id.in_(user_ids)))
        await session.execute(delete(Token).where(Token.user_id.in_(user_ids)))
        await session.execute(delete(User).where(User.username == "testuser"))
        await session.commit()


@pytest_asyncio.fixture(autouse=True)
async def clean_test_records():
    await _clear_test_records()
    yield
    await _clear_test_records()


@pytest_asyncio.fixture
async def session():
    async with mysql_session() as session:
        yield session


async def setup_test_user(session) -> User:
    result = await session.execute(select(User).where(User.username == "testuser"))
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(username="testuser", password_hash="hashed_password", email="test@example.com")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def test_generate_permanent_token(session):
    user = await setup_test_user(session)
    token = await generate_permanent_token(session, user.user_id, "test_provider")

    result = await session.execute(
        select(Token).where(Token.user_id == user.user_id, Token.token_type == 1)
    )
    stored_token = result.scalar_one()
    assert stored_token.token == token


async def test_third_party_access_with_valid_token(session):
    user = await setup_test_user(session)
    token = await generate_permanent_token(session, user.user_id, "test_provider")

    response = client.get(f"{API_PREFIX}/third_party_test", headers={"X-API-Key": token})
    assert response.status_code == 200
    assert response.json()["message"] == "Third party access successful"


async def test_third_party_access_with_invalid_token():
    response = client.get(f"{API_PREFIX}/third_party_test", headers={"X-API-Key": "invalid_token"})
    assert response.status_code == 401


async def test_third_party_access_without_token():
    response = client.get(f"{API_PREFIX}/third_party_test")
    assert response.status_code == 401


async def test_revoke_permanent_token(session):
    user = await setup_test_user(session)
    token = await generate_permanent_token(session, user.user_id, "test_provider")

    response = client.get(f"{API_PREFIX}/third_party_test", headers={"X-API-Key": token})
    assert response.status_code == 200

    result = await session.execute(
        select(Token).where(Token.token == token, Token.token_type == 1)
    )
    stored_token = result.scalar_one()
    stored_token.state = -1
    await session.commit()

    response = client.get(f"{API_PREFIX}/third_party_test", headers={"X-API-Key": token})
    assert response.status_code == 401


async def test_permanent_token_expiration(session):
    user = await setup_test_user(session)
    token = await generate_permanent_token(session, user.user_id, "test_provider")

    response = client.get(f"{API_PREFIX}/third_party_test", headers={"X-API-Key": token})
    assert response.status_code == 200

    result = await session.execute(
        select(Token).where(Token.token == token, Token.token_type == 1)
    )
    stored_token = result.scalar_one()
    assert stored_token.expires_at.replace(tzinfo=TIME_ZONE) > (
        datetime.now(TIME_ZONE) + timedelta(days=365 * 999)
    )

    stored_token.expires_at = datetime.now(TIME_ZONE) - timedelta(days=1)
    await session.commit()

    response = client.get(f"{API_PREFIX}/third_party_test", headers={"X-API-Key": token})
    assert response.status_code == 401

