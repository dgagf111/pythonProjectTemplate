from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
from typing import Optional
from config.config import config
from db.mysql.mysql import MySQL_Database
from .auth_models import User, Token
from sqlalchemy.orm import Session

# 获取API配置
api_config = config.get_api_config()

# 设置关键常量
SECRET_KEY = api_config.get("secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 创建数据库连接
db = MySQL_Database()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(session: Session, username: str):
    return session.query(User).filter(User.username == username, User.state >= 0).first()

def authenticate_user(session: Session, username: str, password: str):
    user = get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    session = db.get_session()
    user = get_user(session, username)
    session.close()
    if user is None:
        raise credentials_exception
    return user

# 新增函数：创建新用户
def create_user(session: Session, username: str, password: str, email: str):
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, password_hash=hashed_password, email=email)
    session.add(new_user)
    session.commit()
    return new_user

# 新增函数：保存token
def save_token(session: Session, user_id: int, token: str, token_type: int, expires_at: datetime):
    new_token = Token(user_id=user_id, token=token, token_type=token_type, expires_at=expires_at)
    session.add(new_token)
    session.commit()
    return new_token
