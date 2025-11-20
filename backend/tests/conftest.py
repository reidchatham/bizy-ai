"""
Pytest configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from api.dependencies import get_db
from models.base import Base
from models.user import User
from models.task import Task
from models.goal import Goal


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password_here",
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user2(db):
    """Create a second test user"""
    user = User(
        id=2,
        username="testuser2",
        email="test2@example.com",
        hashed_password="hashed_password_here2",
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user, monkeypatch):
    """Mock JWT authentication headers"""
    from api.auth import TokenData
    from api.routes import goals, tasks

    async def mock_get_current_user():
        return TokenData(
            user_id=test_user.id,
            username=test_user.username,
            email=test_user.email,
            is_admin=False
        )

    # Patch in all route modules
    monkeypatch.setattr("api.auth.get_current_user", mock_get_current_user)
    monkeypatch.setattr("api.routes.goals.get_current_user", mock_get_current_user)
    monkeypatch.setattr("api.routes.tasks.get_current_user", mock_get_current_user)

    return {"Authorization": "Bearer fake-jwt-token"}


@pytest.fixture
def auth_headers_user2(test_user2, monkeypatch):
    """Mock JWT authentication headers for second user"""
    from api.auth import TokenData
    from api.routes import goals, tasks

    async def mock_get_current_user():
        return TokenData(
            user_id=test_user2.id,
            username=test_user2.username,
            email=test_user2.email,
            is_admin=False
        )

    # Patch in all route modules
    monkeypatch.setattr("api.auth.get_current_user", mock_get_current_user)
    monkeypatch.setattr("api.routes.goals.get_current_user", mock_get_current_user)
    monkeypatch.setattr("api.routes.tasks.get_current_user", mock_get_current_user)

    return {"Authorization": "Bearer fake-jwt-token-user2"}
