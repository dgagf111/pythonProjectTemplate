from sqlalchemy import Column, BigInteger, String, DateTime, Integer
from sqlalchemy.sql import func
from db.mysql.mysql import MySQL_Base

class User(MySQL_Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True)
    id_card_number = Column(String(50), unique=True)
    last_login_at = Column(DateTime)
    state = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Token(MySQL_Base):
    __tablename__ = 'tokens'

    token_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    token_type = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    state = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ThirdPartyToken(MySQL_Base):
    __tablename__ = 'third_party_tokens'

    token_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    provider = Column(String(50), nullable=False)
    third_party_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    state = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())