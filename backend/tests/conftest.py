"""
Pytest configuration and fixtures
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from api.dependencies import get_db
from api.auth import get_current_user, TokenData
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


# Global variable to store current test user for dependency override
_current_test_user = None


def get_mock_current_user():
    """Override for get_current_user dependency"""
    global _current_test_user
    if _current_test_user is None:
        raise ValueError("Test user not set")
    return _current_test_user


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
def auth_headers(test_user):
    """Mock JWT authentication headers using dependency override"""
    global _current_test_user

    # Create token data for test user
    token_data = TokenData(
        user_id=test_user.id,
        username=test_user.username,
        email=test_user.email,
        is_admin=False,
        exp=9999999999  # Far future expiration
    )

    # Set global test user and override dependency
    _current_test_user = token_data
    app.dependency_overrides[get_current_user] = lambda: token_data

    yield {"Authorization": "Bearer fake-jwt-token"}

    # Cleanup
    _current_test_user = None
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]


@pytest.fixture
def auth_headers_user2(test_user2):
    """Mock JWT authentication headers for second user"""
    global _current_test_user

    # Create token data for test user 2
    token_data = TokenData(
        user_id=test_user2.id,
        username=test_user2.username,
        email=test_user2.email,
        is_admin=False,
        exp=9999999999
    )

    # Set global test user and override dependency
    _current_test_user = token_data
    app.dependency_overrides[get_current_user] = lambda: token_data

    yield {"Authorization": "Bearer fake-jwt-token-user2"}

    # Cleanup
    _current_test_user = None
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]


@pytest.fixture
def sample_task(db, test_user):
    """Create a sample task for testing"""
    task = Task(
        user_id=test_user.id,
        title="Sample Task",
        description="A sample task for testing",
        priority=2,
        status="pending",
        category="testing"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@pytest.fixture
def sample_goal(db, test_user):
    """Create a sample goal for testing"""
    goal = Goal(
        user_id=test_user.id,
        title="Sample Goal",
        description="A sample goal for testing",
        horizon="monthly",
        status="active",
        progress_percentage=0.0
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@pytest.fixture
def mock_anthropic_client(monkeypatch):
    """Mock Anthropic API client for AI endpoint tests"""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-api-key")

    with patch('anthropic.Anthropic') as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        yield mock_client
