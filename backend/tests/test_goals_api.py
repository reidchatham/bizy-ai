"""
Test suite for Goal CRUD API endpoints
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


class TestGoalCRUD:
    """Test basic CRUD operations for goals"""

    def test_create_goal(self, client, auth_headers, test_user):
        """Test creating a new goal"""
        goal_data = {
            "title": "Launch MVP Product",
            "description": "Launch minimum viable product to market",
            "horizon": "yearly",
            "status": "active",
            "success_criteria": "100 active users",
            "metrics": {"key_metric": "user_count"}
        }

        response = client.post("/api/goals/", json=goal_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Launch MVP Product"
        assert data["description"] == "Launch minimum viable product to market"
        assert data["horizon"] == "yearly"
        assert data["status"] == "active"
        assert data["user_id"] == test_user.id
        assert data["progress_percentage"] == 0.0
        assert "id" in data
        assert "created_at" in data

    def test_create_goal_with_parent(self, client, auth_headers, test_user, db):
        """Test creating a goal with parent goal"""
        from models import Goal

        # Create parent goal
        parent_goal = Goal(
            user_id=test_user.id,
            title="Parent Goal",
            horizon="yearly",
            progress_percentage=0.0
        )
        db.add(parent_goal)
        db.commit()
        db.refresh(parent_goal)

        # Create child goal
        goal_data = {
            "title": "Child Goal",
            "description": "Subgoal of parent",
            "horizon": "quarterly",
            "parent_goal_id": parent_goal.id
        }

        response = client.post("/api/goals/", json=goal_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["parent_goal_id"] == parent_goal.id

    def test_create_goal_invalid_parent(self, client, auth_headers):
        """Test creating a goal with non-existent parent"""
        goal_data = {
            "title": "Test Goal",
            "horizon": "monthly",
            "parent_goal_id": 9999
        }

        response = client.post("/api/goals/", json=goal_data, headers=auth_headers)

        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    def test_create_goal_missing_required_fields(self, client, auth_headers):
        """Test creating a goal without required fields"""
        goal_data = {
            "description": "Missing title and horizon"
        }

        response = client.post("/api/goals/", json=goal_data, headers=auth_headers)

        assert response.status_code == 422

    def test_create_goal_invalid_horizon(self, client, auth_headers):
        """Test creating a goal with invalid horizon"""
        goal_data = {
            "title": "Test Goal",
            "horizon": "invalid_horizon"
        }

        response = client.post("/api/goals/", json=goal_data, headers=auth_headers)

        assert response.status_code == 422

    def test_list_goals(self, client, auth_headers, test_user, db):
        """Test listing all goals"""
        from models import Goal

        # Create test goals
        goals = [
            Goal(user_id=test_user.id, title="Goal 1", horizon="yearly", progress_percentage=0),
            Goal(user_id=test_user.id, title="Goal 2", horizon="quarterly", progress_percentage=0),
            Goal(user_id=test_user.id, title="Goal 3", horizon="monthly", progress_percentage=0),
        ]
        db.add_all(goals)
        db.commit()

        response = client.get("/api/goals/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("title" in goal for goal in data)

    def test_list_goals_with_filters(self, client, auth_headers, test_user, db):
        """Test filtering goals"""
        from models import Goal

        goals = [
            Goal(user_id=test_user.id, title="Active Yearly", horizon="yearly", status="active", progress_percentage=0),
            Goal(user_id=test_user.id, title="Completed Yearly", horizon="yearly", status="completed", progress_percentage=100),
            Goal(user_id=test_user.id, title="Active Monthly", horizon="monthly", status="active", progress_percentage=0),
        ]
        db.add_all(goals)
        db.commit()

        # Filter by status
        response = client.get("/api/goals/?status=active", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(g["status"] == "active" for g in data)

        # Filter by horizon
        response = client.get("/api/goals/?horizon=yearly", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(g["horizon"] == "yearly" for g in data)

        # Combined filters
        response = client.get("/api/goals/?status=active&horizon=yearly", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Active Yearly"

    def test_list_goals_search(self, client, auth_headers, test_user, db):
        """Test searching goals"""
        from models import Goal

        goals = [
            Goal(user_id=test_user.id, title="Launch Product", horizon="yearly", progress_percentage=0),
            Goal(user_id=test_user.id, title="Improve Marketing", horizon="quarterly", progress_percentage=0),
            Goal(user_id=test_user.id, title="Fix Bugs", horizon="monthly", progress_percentage=0),
        ]
        db.add_all(goals)
        db.commit()

        response = client.get("/api/goals/?search=product", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Product" in data[0]["title"]

    def test_list_goals_include_counts(self, client, auth_headers, test_user, db):
        """Test including task/subgoal counts"""
        from models import Goal, Task

        # Create goal with tasks and subgoals
        parent_goal = Goal(user_id=test_user.id, title="Parent", horizon="yearly", progress_percentage=0)
        db.add(parent_goal)
        db.flush()

        subgoal = Goal(user_id=test_user.id, title="Subgoal", horizon="quarterly", parent_goal_id=parent_goal.id, progress_percentage=0)
        db.add(subgoal)
        db.flush()

        task = Task(
            user_id=test_user.id,
            title="Task 1",
            parent_goal_id=parent_goal.id,
            priority=1
        )
        db.add(task)
        db.commit()

        response = client.get(f"/api/goals/?include_counts=true", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        parent = next(g for g in data if g["title"] == "Parent")
        assert parent["task_count"] == 1
        assert parent["subgoal_count"] == 1

    def test_get_goal(self, client, auth_headers, test_user, db):
        """Test getting a specific goal"""
        from models import Goal

        goal = Goal(
            user_id=test_user.id,
            title="Test Goal",
            description="Test description",
            horizon="monthly",
            progress_percentage=50.0
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)

        response = client.get(f"/api/goals/{goal.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == goal.id
        assert data["title"] == "Test Goal"
        assert data["progress_percentage"] == 50.0

    def test_get_goal_not_found(self, client, auth_headers):
        """Test getting non-existent goal"""
        response = client.get("/api/goals/9999", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_goal_wrong_user(self, client, auth_headers, auth_headers_user2, test_user, test_user2, db):
        """Test user cannot access another user's goal"""
        from models import Goal

        goal = Goal(user_id=test_user.id, title="User 1 Goal", horizon="yearly", progress_percentage=0)
        db.add(goal)
        db.commit()
        db.refresh(goal)

        response = client.get(f"/api/goals/{goal.id}", headers=auth_headers_user2)

        assert response.status_code == 404

    def test_update_goal(self, client, auth_headers, test_user, db):
        """Test updating a goal"""
        from models import Goal

        goal = Goal(
            user_id=test_user.id,
            title="Original Title",
            horizon="yearly",
            progress_percentage=0.0
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)

        update_data = {
            "title": "Updated Title",
            "description": "New description",
            "status": "on_hold"
        }

        response = client.patch(f"/api/goals/{goal.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "New description"
        assert data["status"] == "on_hold"
        assert data["horizon"] == "yearly"  # Unchanged

    def test_update_goal_to_completed(self, client, auth_headers, test_user, db):
        """Test marking goal as completed"""
        from models import Goal

        goal = Goal(
            user_id=test_user.id,
            title="Test Goal",
            horizon="monthly",
            status="active",
            progress_percentage=90.0
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)

        update_data = {"status": "completed"}

        response = client.patch(f"/api/goals/{goal.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["progress_percentage"] == 100.0
        assert data["completed_at"] is not None

    def test_update_goal_circular_reference(self, client, auth_headers, test_user, db):
        """Test preventing circular references"""
        from models import Goal

        # Create parent and child
        parent = Goal(user_id=test_user.id, title="Parent", horizon="yearly", progress_percentage=0)
        db.add(parent)
        db.flush()

        child = Goal(user_id=test_user.id, title="Child", horizon="quarterly", parent_goal_id=parent.id, progress_percentage=0)
        db.add(child)
        db.commit()
        db.refresh(parent)
        db.refresh(child)

        # Try to make parent a child of child (circular reference)
        update_data = {"parent_goal_id": child.id}

        response = client.patch(f"/api/goals/{parent.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 400
        assert "circular" in response.json()["detail"].lower()

    def test_update_goal_self_reference(self, client, auth_headers, test_user, db):
        """Test preventing self-reference"""
        from models import Goal

        goal = Goal(user_id=test_user.id, title="Test", horizon="monthly", progress_percentage=0)
        db.add(goal)
        db.commit()
        db.refresh(goal)

        update_data = {"parent_goal_id": goal.id}

        response = client.patch(f"/api/goals/{goal.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 400
        assert "own parent" in response.json()["detail"]

    def test_delete_goal(self, client, auth_headers, test_user, db):
        """Test deleting a goal"""
        from models import Goal

        goal = Goal(user_id=test_user.id, title="To Delete", horizon="monthly", progress_percentage=0)
        db.add(goal)
        db.commit()
        db.refresh(goal)
        goal_id = goal.id

        response = client.delete(f"/api/goals/{goal_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/goals/{goal_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_goal_with_tasks(self, client, auth_headers, test_user, db):
        """Test deleting goal removes associated tasks or sets parent_goal_id to NULL"""
        from models import Goal, Task

        goal = Goal(user_id=test_user.id, title="Goal", horizon="monthly", progress_percentage=0)
        db.add(goal)
        db.flush()

        task = Task(
            user_id=test_user.id,
            title="Task",
            parent_goal_id=goal.id,
            priority=1
        )
        db.add(task)
        db.commit()
        task_id = task.id
        goal_id = goal.id

        response = client.delete(f"/api/goals/{goal_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify goal is deleted
        db.expire_all()
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        assert goal is None

        # Task behavior depends on implementation (cascade delete or set NULL)
        task = db.query(Task).filter(Task.id == task_id).first()
        # If task still exists, parent_goal_id should be NULL
        # If cascade delete is enabled, task will be None
        if task is not None:
            assert task.parent_goal_id is None


class TestGoalProgress:
    """Test goal progress calculation"""

    def test_calculate_progress_no_tasks_no_subgoals(self, client, auth_headers, test_user, db):
        """Test progress calculation with no tasks or subgoals"""
        from models import Goal

        goal = Goal(user_id=test_user.id, title="Empty Goal", horizon="monthly", progress_percentage=0)
        db.add(goal)
        db.commit()
        db.refresh(goal)

        response = client.post(f"/api/goals/{goal.id}/calculate-progress", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["progress_percentage"] == 0.0

    def test_calculate_progress_only_tasks(self, client, auth_headers, test_user, db):
        """Test progress calculation with only tasks"""
        from models import Goal, Task

        goal = Goal(user_id=test_user.id, title="Goal", horizon="monthly", progress_percentage=0)
        db.add(goal)
        db.flush()

        tasks = [
            Task(user_id=test_user.id, title="Task 1", parent_goal_id=goal.id, priority=1, status="completed"),
            Task(user_id=test_user.id, title="Task 2", parent_goal_id=goal.id, priority=1, status="completed"),
            Task(user_id=test_user.id, title="Task 3", parent_goal_id=goal.id, priority=1, status="pending"),
            Task(user_id=test_user.id, title="Task 4", parent_goal_id=goal.id, priority=1, status="pending"),
        ]
        db.add_all(tasks)
        db.commit()
        db.refresh(goal)

        response = client.post(f"/api/goals/{goal.id}/calculate-progress", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["progress_percentage"] == 50.0  # 2/4 completed

    def test_calculate_progress_only_subgoals(self, client, auth_headers, test_user, db):
        """Test progress calculation with only subgoals"""
        from models import Goal

        parent = Goal(user_id=test_user.id, title="Parent", horizon="yearly", progress_percentage=0)
        db.add(parent)
        db.flush()

        subgoals = [
            Goal(user_id=test_user.id, title="Sub 1", horizon="quarterly", parent_goal_id=parent.id, progress_percentage=100),
            Goal(user_id=test_user.id, title="Sub 2", horizon="quarterly", parent_goal_id=parent.id, progress_percentage=50),
            Goal(user_id=test_user.id, title="Sub 3", horizon="quarterly", parent_goal_id=parent.id, progress_percentage=0),
        ]
        db.add_all(subgoals)
        db.commit()
        db.refresh(parent)

        response = client.post(f"/api/goals/{parent.id}/calculate-progress", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["progress_percentage"] == 50.0  # (100+50+0)/3

    def test_calculate_progress_tasks_and_subgoals(self, client, auth_headers, test_user, db):
        """Test progress calculation with both tasks and subgoals"""
        from models import Goal, Task

        parent = Goal(user_id=test_user.id, title="Parent", horizon="yearly", progress_percentage=0)
        db.add(parent)
        db.flush()

        # 100% task completion
        tasks = [
            Task(user_id=test_user.id, title="Task 1", parent_goal_id=parent.id, priority=1, status="completed"),
            Task(user_id=test_user.id, title="Task 2", parent_goal_id=parent.id, priority=1, status="completed"),
        ]
        db.add_all(tasks)

        # 50% subgoal progress
        subgoals = [
            Goal(user_id=test_user.id, title="Sub 1", horizon="quarterly", parent_goal_id=parent.id, progress_percentage=100),
            Goal(user_id=test_user.id, title="Sub 2", horizon="quarterly", parent_goal_id=parent.id, progress_percentage=0),
        ]
        db.add_all(subgoals)
        db.commit()
        db.refresh(parent)

        response = client.post(f"/api/goals/{parent.id}/calculate-progress", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        # 50% weight tasks (100%) + 50% weight subgoals (50%) = 75%
        assert data["progress_percentage"] == 75.0

    def test_calculate_progress_auto_complete(self, client, auth_headers, test_user, db):
        """Test auto-completion when progress reaches 100%"""
        from models import Goal, Task

        goal = Goal(user_id=test_user.id, title="Goal", horizon="monthly", status="active", progress_percentage=0)
        db.add(goal)
        db.flush()

        task = Task(user_id=test_user.id, title="Task", parent_goal_id=goal.id, priority=1, status="completed")
        db.add(task)
        db.commit()
        db.refresh(goal)

        response = client.post(f"/api/goals/{goal.id}/calculate-progress", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["progress_percentage"] == 100.0
        assert data["status"] == "completed"
        assert data["completed_at"] is not None


class TestGoalBreakdown:
    """Test AI goal breakdown functionality"""

    @patch('anthropic.Anthropic')
    def test_breakdown_goal(self, mock_anthropic, client, auth_headers, test_user, db, monkeypatch):
        """Test AI goal breakdown"""
        from models import Goal

        # Set API key
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        # Mock AI response
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='''```json
{
    "tasks": [
        {
            "title": "Research market",
            "description": "Conduct market research",
            "priority": 1,
            "estimated_hours": 10.0,
            "category": "research"
        },
        {
            "title": "Build MVP",
            "description": "Build minimum viable product",
            "priority": 2,
            "estimated_hours": 40.0,
            "category": "development"
        }
    ],
    "reasoning": "Prioritized by dependencies"
}
```''')]
        mock_client.messages.create.return_value = mock_response

        goal = Goal(
            user_id=test_user.id,
            title="Launch Product",
            description="Launch new product to market",
            horizon="yearly",
            progress_percentage=0
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)

        response = client.post(
            f"/api/goals/{goal.id}/breakdown",
            json={"max_tasks": 10, "include_description": True},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["goal_id"] == goal.id
        assert data["goal_title"] == "Launch Product"
        assert len(data["suggested_tasks"]) == 2
        assert data["suggested_tasks"][0]["title"] == "Research market"
        assert data["suggested_tasks"][0]["priority"] == 1
        assert data["reasoning"] == "Prioritized by dependencies"

    def test_breakdown_goal_no_api_key(self, client, auth_headers, test_user, db, monkeypatch):
        """Test breakdown fails without API key"""
        from models import Goal

        # Clear API key
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        goal = Goal(user_id=test_user.id, title="Test", horizon="monthly", progress_percentage=0)
        db.add(goal)
        db.commit()
        db.refresh(goal)

        response = client.post(f"/api/goals/{goal.id}/breakdown", headers=auth_headers)

        assert response.status_code == 503
        assert "not configured" in response.json()["detail"]

    @patch('anthropic.Anthropic')
    def test_create_tasks_from_breakdown(self, mock_anthropic, client, auth_headers, test_user, db):
        """Test creating tasks from AI breakdown"""
        from models import Goal

        goal = Goal(user_id=test_user.id, title="Test Goal", horizon="monthly", progress_percentage=0)
        db.add(goal)
        db.commit()
        db.refresh(goal)

        task_suggestions = [
            {
                "title": "Task 1",
                "description": "First task",
                "priority": 1,
                "estimated_hours": 5.0,
                "category": "research"
            },
            {
                "title": "Task 2",
                "description": "Second task",
                "priority": 2,
                "estimated_hours": 10.0,
                "category": "development"
            }
        ]

        response = client.post(
            f"/api/goals/{goal.id}/breakdown/create-tasks",
            json=task_suggestions,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Task 1"
        assert data[1]["title"] == "Task 2"

        # Verify tasks were created
        tasks_response = client.get(f"/api/tasks/?goal_id={goal.id}", headers=auth_headers)
        assert tasks_response.status_code == 200
        tasks = tasks_response.json()
        assert len(tasks) == 2


class TestGoalStats:
    """Test goal statistics endpoint"""

    def test_get_goal_stats(self, client, auth_headers, test_user, db):
        """Test getting goal statistics"""
        from models import Goal

        goals = [
            Goal(user_id=test_user.id, title="Active Yearly", horizon="yearly", status="active", progress_percentage=30),
            Goal(user_id=test_user.id, title="Active Quarterly", horizon="quarterly", status="active", progress_percentage=90),
            Goal(user_id=test_user.id, title="Completed Monthly", horizon="monthly", status="completed", progress_percentage=100),
            Goal(user_id=test_user.id, title="On Hold", horizon="weekly", status="on_hold", progress_percentage=10),
        ]
        db.add_all(goals)
        db.commit()

        response = client.get("/api/goals/stats/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert data["by_status"]["active"] == 2
        assert data["by_status"]["completed"] == 1
        assert data["by_status"]["on_hold"] == 1
        assert data["by_horizon"]["yearly"] == 1
        assert data["by_horizon"]["quarterly"] == 1
        assert data["by_horizon"]["monthly"] == 1
        assert data["by_horizon"]["weekly"] == 1
        assert data["average_progress"] == 60.0  # (30 + 90) / 2 active goals
        assert data["near_completion"] == 1  # 1 goal >= 80%

    def test_get_goal_stats_empty(self, client, auth_headers):
        """Test stats with no goals"""
        response = client.get("/api/goals/stats/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["by_status"] == {}
        assert data["by_horizon"] == {}
        assert data["average_progress"] == 0
        assert data["near_completion"] == 0


class TestGoalAuthorization:
    """Test authorization and data isolation"""

    def test_user_cannot_see_other_user_goals(self, client, test_user, test_user2, db):
        """Test users can only see their own goals"""
        from models import Goal
        from api.main import app
        from api.auth import get_current_user, TokenData

        user1_goal = Goal(user_id=test_user.id, title="User 1 Goal", horizon="yearly", progress_percentage=0)
        user2_goal = Goal(user_id=test_user2.id, title="User 2 Goal", horizon="yearly", progress_percentage=0)
        db.add_all([user1_goal, user2_goal])
        db.commit()

        # Set up user 1 auth
        token_data_user1 = TokenData(
            user_id=test_user.id, username=test_user.username,
            email=test_user.email, is_admin=False, exp=9999999999
        )
        app.dependency_overrides[get_current_user] = lambda: token_data_user1

        # User 1 sees only their goal
        response = client.get("/api/goals/", headers={"Authorization": "Bearer fake"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "User 1 Goal"

        # Switch to user 2 auth
        token_data_user2 = TokenData(
            user_id=test_user2.id, username=test_user2.username,
            email=test_user2.email, is_admin=False, exp=9999999999
        )
        app.dependency_overrides[get_current_user] = lambda: token_data_user2

        # User 2 sees only their goal
        response = client.get("/api/goals/", headers={"Authorization": "Bearer fake"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "User 2 Goal"

    def test_user_cannot_modify_other_user_goal(self, client, test_user, test_user2, db):
        """Test users cannot modify other users' goals"""
        from models import Goal
        from api.main import app
        from api.auth import get_current_user, TokenData

        goal = Goal(user_id=test_user.id, title="User 1 Goal", horizon="yearly", progress_percentage=0)
        db.add(goal)
        db.commit()
        db.refresh(goal)

        # Set up user 2 auth
        token_data = TokenData(
            user_id=test_user2.id, username=test_user2.username,
            email=test_user2.email, is_admin=False, exp=9999999999
        )
        app.dependency_overrides[get_current_user] = lambda: token_data

        # User 2 tries to update User 1's goal
        response = client.patch(
            f"/api/goals/{goal.id}",
            json={"title": "Hacked"},
            headers={"Authorization": "Bearer fake"}
        )

        assert response.status_code == 404

        # Verify goal unchanged
        db.refresh(goal)
        assert goal.title == "User 1 Goal"
