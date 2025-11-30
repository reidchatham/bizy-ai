"""
Test suite for Analytics API endpoints
"""

import pytest
from datetime import datetime, timedelta


class TestTaskAnalytics:
    """Test task analytics endpoint"""

    def test_get_task_analytics_empty(self, client, auth_headers):
        """Test analytics with no tasks"""
        response = client.get("/api/analytics/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 7
        assert data["tasks_completed"] == 0
        assert data["tasks_created"] == 0
        assert data["completion_rate"] == 0
        assert data["overdue_count"] == 0

    def test_get_task_analytics_with_data(self, client, auth_headers, test_user, db):
        """Test analytics with task data"""
        from models import Task

        now = datetime.utcnow()

        # Create completed tasks
        tasks = [
            Task(
                user_id=test_user.id,
                title="Completed Task 1",
                priority=1,
                status="completed",
                category="development",
                estimated_hours=5.0,
                actual_hours=4.0,
                completed_at=now - timedelta(days=1),
                created_at=now - timedelta(days=3)
            ),
            Task(
                user_id=test_user.id,
                title="Completed Task 2",
                priority=2,
                status="completed",
                category="testing",
                estimated_hours=3.0,
                actual_hours=3.5,
                completed_at=now - timedelta(days=2),
                created_at=now - timedelta(days=4)
            ),
            Task(
                user_id=test_user.id,
                title="Pending Task",
                priority=3,
                status="pending",
                created_at=now - timedelta(days=1)
            ),
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/analytics/tasks?days=7", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["tasks_completed"] == 2
        assert data["tasks_created"] == 3
        assert data["total_estimated_hours"] == 8.0
        assert data["total_actual_hours"] == 7.5
        assert data["by_category"]["development"] == 1
        assert data["by_category"]["testing"] == 1
        assert data["by_priority"]["1"] == 1
        assert data["by_priority"]["2"] == 1

    def test_get_task_analytics_custom_period(self, client, auth_headers, test_user, db):
        """Test analytics with custom period"""
        from models import Task

        now = datetime.utcnow()

        # Task completed within 30 days
        task = Task(
            user_id=test_user.id,
            title="Recent Task",
            priority=1,
            status="completed",
            completed_at=now - timedelta(days=15),
            created_at=now - timedelta(days=20)
        )
        db.add(task)
        db.commit()

        # 7 days - should not include the task
        response = client.get("/api/analytics/tasks?days=7", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["tasks_completed"] == 0

        # 30 days - should include the task
        response = client.get("/api/analytics/tasks?days=30", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["tasks_completed"] == 1

    def test_get_task_analytics_overdue(self, client, auth_headers, test_user, db):
        """Test overdue task count in analytics"""
        from models import Task

        now = datetime.utcnow()

        tasks = [
            Task(
                user_id=test_user.id,
                title="Overdue Task",
                priority=1,
                status="pending",
                due_date=now - timedelta(days=2),
                created_at=now - timedelta(days=5)
            ),
            Task(
                user_id=test_user.id,
                title="Not Overdue",
                priority=1,
                status="pending",
                due_date=now + timedelta(days=5),
                created_at=now - timedelta(days=1)
            ),
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/analytics/tasks", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["overdue_count"] == 1

    def test_get_task_analytics_invalid_period(self, client, auth_headers):
        """Test analytics with invalid period"""
        response = client.get("/api/analytics/tasks?days=0", headers=auth_headers)
        assert response.status_code == 422

        response = client.get("/api/analytics/tasks?days=100", headers=auth_headers)
        assert response.status_code == 422


class TestGoalAnalytics:
    """Test goal analytics endpoint"""

    def test_get_goal_analytics_empty(self, client, auth_headers):
        """Test analytics with no goals"""
        response = client.get("/api/analytics/goals", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_goals"] == 0
        assert data["active_goals"] == 0
        assert data["completed_goals"] == 0
        assert data["average_progress"] == 0
        assert data["goals_near_completion"] == 0
        assert data["goals_at_risk"] == 0

    def test_get_goal_analytics_with_data(self, client, auth_headers, test_user, db):
        """Test analytics with goal data"""
        from models import Goal

        now = datetime.utcnow()

        goals = [
            Goal(
                user_id=test_user.id,
                title="Active Yearly Goal",
                horizon="yearly",
                status="active",
                progress_percentage=50.0
            ),
            Goal(
                user_id=test_user.id,
                title="Near Completion",
                horizon="quarterly",
                status="active",
                progress_percentage=85.0
            ),
            Goal(
                user_id=test_user.id,
                title="Completed Goal",
                horizon="monthly",
                status="completed",
                progress_percentage=100.0
            ),
            Goal(
                user_id=test_user.id,
                title="On Hold",
                horizon="weekly",
                status="on_hold",
                progress_percentage=20.0
            ),
        ]
        db.add_all(goals)
        db.commit()

        response = client.get("/api/analytics/goals", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_goals"] == 4
        assert data["active_goals"] == 2
        assert data["completed_goals"] == 1
        assert data["on_hold_goals"] == 1
        assert data["goals_near_completion"] == 1  # Only 85% goal
        assert data["by_horizon"]["yearly"] == 1
        assert data["by_horizon"]["quarterly"] == 1
        assert data["by_horizon"]["monthly"] == 1
        assert data["by_horizon"]["weekly"] == 1

    def test_get_goal_analytics_average_progress(self, client, auth_headers, test_user, db):
        """Test average progress calculation"""
        from models import Goal

        goals = [
            Goal(
                user_id=test_user.id,
                title="Goal 1",
                horizon="monthly",
                status="active",
                progress_percentage=30.0
            ),
            Goal(
                user_id=test_user.id,
                title="Goal 2",
                horizon="monthly",
                status="active",
                progress_percentage=70.0
            ),
        ]
        db.add_all(goals)
        db.commit()

        response = client.get("/api/analytics/goals", headers=auth_headers)

        assert response.status_code == 200
        # Average of 30 and 70 = 50
        assert response.json()["average_progress"] == 50.0

    def test_get_goal_analytics_at_risk(self, client, auth_headers, test_user, db):
        """Test goals at risk detection"""
        from models import Goal

        now = datetime.utcnow()

        goals = [
            Goal(
                user_id=test_user.id,
                title="At Risk Goal",
                horizon="monthly",
                status="active",
                progress_percentage=10.0,
                target_date=now + timedelta(days=15)  # Less than 30 days
            ),
            Goal(
                user_id=test_user.id,
                title="Not At Risk",
                horizon="monthly",
                status="active",
                progress_percentage=10.0,
                target_date=now + timedelta(days=60)  # More than 30 days
            ),
        ]
        db.add_all(goals)
        db.commit()

        response = client.get("/api/analytics/goals", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["goals_at_risk"] == 1


class TestVelocityMetrics:
    """Test velocity metrics endpoint"""

    def test_get_velocity_empty(self, client, auth_headers):
        """Test velocity with no tasks"""
        response = client.get("/api/analytics/velocity", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["velocity"] == 0
        assert data["tasks_per_day"] == 0
        assert data["daily_breakdown"] == []
        assert data["best_day"] is None
        assert data["worst_day"] is None

    def test_get_velocity_with_data(self, client, auth_headers, test_user, db):
        """Test velocity calculation with task data"""
        from models import Task

        now = datetime.utcnow()

        # Create 10 tasks completed over 30 days
        tasks = [
            Task(
                user_id=test_user.id,
                title=f"Task {i}",
                priority=1,
                status="completed",
                completed_at=now - timedelta(days=i % 30),
                created_at=now - timedelta(days=30)
            )
            for i in range(10)
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/analytics/velocity?days=30", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["velocity"] > 0
        assert data["tasks_per_day"] > 0
        assert len(data["daily_breakdown"]) > 0

    def test_get_velocity_best_worst_day(self, client, auth_headers, test_user, db):
        """Test best and worst day detection"""
        from models import Task

        now = datetime.utcnow()

        # Day 1: 3 tasks completed
        day1 = now - timedelta(days=5)
        # Day 2: 1 task completed
        day2 = now - timedelta(days=3)

        tasks = [
            Task(
                user_id=test_user.id,
                title="Task 1",
                priority=1,
                status="completed",
                completed_at=day1,
                created_at=now - timedelta(days=10)
            ),
            Task(
                user_id=test_user.id,
                title="Task 2",
                priority=1,
                status="completed",
                completed_at=day1,
                created_at=now - timedelta(days=10)
            ),
            Task(
                user_id=test_user.id,
                title="Task 3",
                priority=1,
                status="completed",
                completed_at=day1,
                created_at=now - timedelta(days=10)
            ),
            Task(
                user_id=test_user.id,
                title="Task 4",
                priority=1,
                status="completed",
                completed_at=day2,
                created_at=now - timedelta(days=10)
            ),
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/analytics/velocity?days=30", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["best_day"] is not None
        assert data["best_day"]["tasks_completed"] == 3
        assert data["worst_day"] is not None
        assert data["worst_day"]["tasks_completed"] == 1

    def test_get_velocity_trend_improving(self, client, auth_headers, test_user, db):
        """Test improving trend detection"""
        from models import Task

        now = datetime.utcnow()

        # First half: 2 tasks, Second half: 5 tasks
        tasks = [
            Task(
                user_id=test_user.id,
                title=f"Old Task {i}",
                priority=1,
                status="completed",
                completed_at=now - timedelta(days=25),
                created_at=now - timedelta(days=30)
            )
            for i in range(2)
        ] + [
            Task(
                user_id=test_user.id,
                title=f"New Task {i}",
                priority=1,
                status="completed",
                completed_at=now - timedelta(days=5),
                created_at=now - timedelta(days=10)
            )
            for i in range(5)
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/analytics/velocity?days=30", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["completion_trend"] == "improving"

    def test_get_velocity_productivity_score(self, client, auth_headers, test_user, db):
        """Test productivity score calculation"""
        from models import Task

        now = datetime.utcnow()

        # Create high priority completed tasks
        tasks = [
            Task(
                user_id=test_user.id,
                title=f"High Priority Task {i}",
                priority=1,  # High priority
                status="completed",
                completed_at=now - timedelta(days=i + 1),
                created_at=now - timedelta(days=30)
            )
            for i in range(5)
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/analytics/velocity?days=30", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["productivity_score"] > 0
        assert data["productivity_score"] <= 100


class TestTrendAnalysis:
    """Test trend analysis endpoint"""

    def test_get_trends_empty(self, client, auth_headers):
        """Test trends with no data"""
        response = client.get("/api/analytics/trends", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        # Even with no data, trends endpoint returns weekly structure
        assert "completion_trend" in data
        assert "category_trends" in data
        assert "insights" in data

    def test_get_trends_with_data(self, client, auth_headers, test_user, db):
        """Test trends with task data"""
        from models import Task

        now = datetime.utcnow()

        # Create tasks across weeks
        tasks = []
        for week in range(4):
            for i in range(3):
                tasks.append(Task(
                    user_id=test_user.id,
                    title=f"Week {week} Task {i}",
                    priority=(week % 3) + 1,
                    status="completed",
                    category="development",
                    completed_at=now - timedelta(days=week * 7 + i),
                    created_at=now - timedelta(days=30)
                ))
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/analytics/trends?days=30", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["completion_trend"]) > 0
        assert "development" in data["category_trends"]

    def test_get_trends_custom_period(self, client, auth_headers):
        """Test trends with custom period"""
        response = client.get("/api/analytics/trends?days=90", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["period_days"] == 90

    def test_get_trends_invalid_period(self, client, auth_headers):
        """Test trends with invalid period"""
        response = client.get("/api/analytics/trends?days=5", headers=auth_headers)
        assert response.status_code == 422

        response = client.get("/api/analytics/trends?days=100", headers=auth_headers)
        assert response.status_code == 422


class TestAnalyticsAuthorization:
    """Test analytics authorization"""

    def test_user_only_sees_own_analytics(self, client, test_user, test_user2, db):
        """Test users only see their own data in analytics"""
        from models import Task, Goal
        from api.main import app
        from api.auth import get_current_user, TokenData

        now = datetime.utcnow()

        # Create tasks for both users
        user1_task = Task(
            user_id=test_user.id,
            title="User 1 Task",
            priority=1,
            status="completed",
            completed_at=now - timedelta(days=1),
            created_at=now - timedelta(days=2)
        )
        user2_task = Task(
            user_id=test_user2.id,
            title="User 2 Task",
            priority=1,
            status="completed",
            completed_at=now - timedelta(days=1),
            created_at=now - timedelta(days=2)
        )
        db.add_all([user1_task, user2_task])
        db.commit()

        # Set up user 1 auth
        token_data = TokenData(
            user_id=test_user.id, username=test_user.username,
            email=test_user.email, is_admin=False, exp=9999999999
        )
        app.dependency_overrides[get_current_user] = lambda: token_data

        # User 1 should only see their own analytics
        response = client.get("/api/analytics/tasks", headers={"Authorization": "Bearer fake"})
        assert response.status_code == 200
        assert response.json()["tasks_completed"] == 1

        # Switch to user 2
        token_data2 = TokenData(
            user_id=test_user2.id, username=test_user2.username,
            email=test_user2.email, is_admin=False, exp=9999999999
        )
        app.dependency_overrides[get_current_user] = lambda: token_data2

        # User 2 should also only see their own analytics
        response = client.get("/api/analytics/tasks", headers={"Authorization": "Bearer fake"})
        assert response.status_code == 200
        assert response.json()["tasks_completed"] == 1
