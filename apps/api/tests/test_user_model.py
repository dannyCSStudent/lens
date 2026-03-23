import pytest
from sqlalchemy.exc import IntegrityError

from app.core.models.user import User


def make_user(email: str = "user@example.com", username: str = "user") -> User:
    return User(email=email, username=username, password_hash="hashed")


def test_user_defaults(session):
    user = make_user()
    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.is_verified is False
    assert user.failed_login_attempts == 0
    assert user.locked_until is None
    assert user.created_at is not None
    assert user.updated_at is not None


def test_user_email_unique_constraint(session):
    session.add(make_user(email="dupe@example.com", username="dupe1"))
    session.commit()

    session.add(make_user(email="dupe@example.com", username="dupe2"))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_user_username_unique_constraint(session):
    session.add(make_user(email="unique1@example.com", username="same"))
    session.commit()

    session.add(make_user(email="unique2@example.com", username="same"))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
