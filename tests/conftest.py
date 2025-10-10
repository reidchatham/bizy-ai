"""
Pytest Configuration and Fixtures
Provides test database, sessions, and sample data for testing
"""

import pytest
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from agent.models import Base, Task, Goal, BusinessPlan

# Set test environment
os.environ['BIZY_ENV'] = 'test'


@pytest.fixture(scope='function')
def test_engine():
    """Create in-memory test database for each test"""
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def test_session(test_engine):
    """Create isolated test session for each test"""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_goal(test_session):
    """Create a sample goal for testing"""
    goal = Goal(
        title="Launch MVP Product",
        description="Build and launch minimum viable product",
        horizon="yearly",
        target_date=datetime(2026, 10, 1),
        progress_percentage=0,
        status="active"
    )
    test_session.add(goal)
    test_session.commit()
    test_session.refresh(goal)
    return goal


@pytest.fixture
def sample_task(test_session):
    """Create a sample task for testing"""
    task = Task(
        title="Test Task",
        description="Sample task for testing",
        priority=2,
        status="pending",
        category="development"
    )
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    return task


@pytest.fixture
def sample_task_with_goal(test_session, sample_goal):
    """Create a task associated with a goal"""
    task = Task(
        title="Goal-linked Task",
        description="Task linked to a goal",
        priority=1,
        status="pending",
        parent_goal_id=sample_goal.id
    )
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    return task


@pytest.fixture
def sample_business_plan(test_session):
    """Create a sample business plan for testing"""
    plan = BusinessPlan(
        name="Test Business Plan",
        version="1.0",
        vision="Test vision statement",
        mission="Test mission statement",
        value_proposition="Test value proposition",
        target_market="Test target market",
        revenue_model="Test revenue model",
        is_active=True
    )
    test_session.add(plan)
    test_session.commit()
    test_session.refresh(plan)
    return plan


@pytest.fixture
def multiple_tasks(test_session, sample_goal):
    """Create multiple tasks with different statuses"""
    tasks = [
        Task(title="Completed Task", status="completed", parent_goal_id=sample_goal.id, completed_at=datetime.now()),
        Task(title="Pending Task 1", status="pending", parent_goal_id=sample_goal.id, priority=1),
        Task(title="Pending Task 2", status="pending", parent_goal_id=sample_goal.id, priority=2),
        Task(title="In Progress Task", status="in_progress", parent_goal_id=sample_goal.id),
    ]
    for task in tasks:
        test_session.add(task)
    test_session.commit()
    return tasks
