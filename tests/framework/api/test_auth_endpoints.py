import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import pythonprojecttemplate.api.api_router as api_module
from pythonprojecttemplate.api.auth.auth_service import get_db


@pytest.fixture()
def client(monkeypatch):
    app = FastAPI()
    app.include_router(api_module.api_router)

    async def override_get_db():
        yield None

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)

    yield test_client
    app.dependency_overrides.clear()


def test_token_endpoint_returns_tokens(client, monkeypatch):
    async def fake_auth(session, username, password):
        assert username == "alice"
        assert password == "secret"
        return {"access_token": "access-token", "refresh_token": "refresh-token", "token_type": "bearer"}

    monkeypatch.setattr(api_module, "authenticate_user", fake_auth)

    response = client.post(f"{api_module.API_PREFIX}/token", data={"username": "alice", "password": "secret"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["code"] == 200
    assert payload["data"]["access_token"] == "access-token"
    assert payload["data"]["refresh_token"] == "refresh-token"
    assert payload["data"]["token_type"] == "bearer"


def test_login_endpoint_uses_authenticate_user_tokens(client, monkeypatch):
    async def fake_auth(session, username, password):
        return {"access_token": "login-access", "refresh_token": "login-refresh", "token_type": "bearer"}

    monkeypatch.setattr(api_module, "authenticate_user", fake_auth)

    response = client.post(f"{api_module.API_PREFIX}/login", data={"username": "bob", "password": "pwd"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert payload["data"] == {
        "access_token": "login-access",
        "refresh_token": "login-refresh",
        "token_type": "bearer",
    }
