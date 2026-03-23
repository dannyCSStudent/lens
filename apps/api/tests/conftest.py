import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.models.base import Base


@pytest.fixture()
def session():
    """Provide an in-memory SQLite session for model tests."""
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session
        session.rollback()
