from __future__ import annotations

from sqlalchemy.orm import scoped_session

from pythonprojecttemplate.db.session import Base, SessionLocal, engine


MySQL_Base = Base


class MySQL_Database:
    """
    Backwards compatible database helper that reuses the shared engine/session factory.
    """

    def __init__(self):
        self.engine = engine
        self.Session = scoped_session(SessionLocal)

    def get_session(self):
        return self.Session()

    def close_session(self):
        self.Session.remove()
