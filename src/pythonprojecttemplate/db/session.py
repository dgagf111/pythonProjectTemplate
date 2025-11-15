from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, scoped_session, sessionmaker

from pythonprojecttemplate.config.settings import settings

engine = create_engine(
    settings.database.url,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_recycle=settings.database.pool_recycle,
    pool_pre_ping=True,
    echo=settings.database.echo,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
ScopedSession = scoped_session(SessionLocal)
Base = declarative_base()


def get_session() -> Generator[Session, None, None]:
    session = ScopedSession()
    try:
        yield session
    finally:
        ScopedSession.remove()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

