import contextlib
import contextvars
from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

_inner_session = contextvars.ContextVar("_inner_session", default=None)


class Database:
    """Database session provider helper class. All it does is check whether or not a session is set, and if not
    raise an exception."""

    @classmethod
    def set_session(cls, session):
        _inner_session.set(session)

    @property
    def session(cls) -> Session:
        try:
            current_session = _inner_session.get()
            if current_session is None:
                raise AttributeError
            return current_session
        except (AttributeError, LookupError):
            raise Exception("Can't get session. Please call Database.set_session()")


@contextlib.contextmanager
def get_session(session_maker: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Database session context manager. Can be used with `Database` and context vars, which is the default
    implementation, but works well on its own as a context manager or dependency.

    :params sessionmaker[:class:`Session`] session_maker: Session maker, returned by SQLAlchemy ORM's `sessionmaker`
    builder."""
    inner_db_session = session_maker()
    try:
        Database.set_session(inner_db_session)
        yield inner_db_session
    except Exception:
        inner_db_session.rollback()
        raise
    finally:
        Database.set_session(None)
        inner_db_session.close()
