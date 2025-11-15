from datetime import datetime, timedelta, UTC
from typing import Optional

from jose import jwt

from pythonprojecttemplate.config.settings import settings

SECRET_KEY = settings.api.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.api.access_token_expire_minutes

def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_access_token(data: dict, username: str, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "sub": username})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, username: str, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire_delta = expires_delta or timedelta(days=settings.api.refresh_token_expire_days)
    expire = datetime.now(UTC) + expire_delta
    to_encode.update({"exp": expire, "sub": username, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
