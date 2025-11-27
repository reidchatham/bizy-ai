"""
Test suite for Task CRUD API endpoints
"""

import pytest
from datetime import datetime, timedelta


class TestTaskCRUD:
    """Test basic CRUD operations for tasks"""

    def test_create_task(self, client, auth_headers, test_user):
        """Test creating a new task"""
        task_data = {
            "title": "Test Task",
            "description": "A test task description",
            "priority": 1,
            "status": "pending",
            "category": "development",
            "estimated_hours": 5.0,
            "tags": ["urgent", "backend"]
        }

        response = client.post("/api/tasks/", json=task_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "A test task description"
        assert data["priority"] == 1
        assert data["status"] == "pending"
        assert data["category"] == "development"
        assert data["user_id"] == test_user.id
        assert "id" in data
        assert "created_at" in data

    def test_create_task_with_goal(self, client, auth_headers, test_user, sample_goal):
        """Test creating a task linked to a goal"""
        task_data = {
            "title": "Task with Goal",
            "priority": 2,
            "parent_goal_id": sample_goal.id
        }

        response = client.post("/api/tasks/", json=task_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["parent_goal_id"] == sample_goal.id

    def test_create_task_invalid_goal(self, client, auth_headers):
        """Test creating a task with non-existent goal"""
        task_data = {
            "title": "Task with Invalid Goal",
            "priority": 1,
            "parent_goal_id": 9999
        }

        response = client.post("/api/tasks/", json=task_data, headers=auth_headers)

        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    def test_create_task_missing_required_fields(self, client, auth_headers):
        """Test creating a task without required fields"""
        task_data = {
            "description": "Missing title"
        }

        response = client.post("/api/tasks/", json=task_data, headers=auth_headers)

        assert response.status_code == 422

    def test_create_task_invalid_priority(self, client, auth_headers):
        """Test creating a task with invalid priority"""
        task_data = {
            "title": "Test Task",
            "priority": 10  # Invalid: should be 1-5
        }

        response = client.post("/api/tasks/", json=task_data, headers=auth_headers)

        assert response.status_code == 422

    def test_create_task_invalid_status(self, client, auth_headers):
        """Test creating a task with invalid status"""
        task_data = {
            "title": "Test Task",
            "status": "invalid_status"
        }

        response = client.post("/api/tasks/", json=task_data, headers=auth_headers)

        assert response.status_code == 422

    def test_create_task_with_due_date(self, client, auth_headers, test_user):
        """Test creating a task with due date"""
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Task with Due Date",
            "priority": 2,
            "due_date": due_date
        }

        response = client.post("/api/tasks/", json=task_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] is not None

    def test_list_tasks(self, client, auth_headers, test_user, db):
        """Test listing all tasks"""
        from models import Task

        tasks = [
            Task(user_id=test_user.id, title="Task 1", priority=1),
            Task(user_id=test_user.id, title="Task 2", priority=2),
            Task(user_id=test_user.id, title="Task 3", priority=3),
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/tasks/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("title" in task for task in data)

    def test_get_task(self, client, auth_headers, sample_task):
        """Test getting a specific task"""
        response = client.get(f"/api/tasks/{sample_task.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_task.id
        assert data["title"] == "Sample Task"

    def test_get_task_not_found(self, client, auth_headers):
        """Test getting non-existent task"""
        response = client.get("/api/tasks/9999", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_task(self, client, auth_headers, sample_task):
        """Test updating a task"""
        update_data = {
            "title": "Updated Task Title",
            "description": "Updated description",
            "priority": 1
        }

        response = client.patch(f"/api/tasks/{sample_task.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task Title"
        assert data["description"] == "Updated description"
        assert data["priority"] == 1

    def test_update_task_partial(self, client, auth_headers, sample_task):
        """Test partial update - only change one field"""
        update_data = {
            "status": "in_progress"
        }

        response = client.patch(f"/api/tasks/{sample_task.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["title"] == "Sample Task"  # Unchanged

    def test_update_task_with_goal(self, client, auth_headers, sample_task, sample_goal):
        """Test updating task to link to a goal"""
        update_data = {
            "parent_goal_id": sample_goal.id
        }

        response = client.patch(f"/api/tasks/{sample_task.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["parent_goal_id"] == sample_goal.id

    def test_update_task_invalid_goal(self, client, auth_headers, sample_task):
        """Test updating task with invalid goal"""
        update_data = {
            "parent_goal_id": 9999
        }

        response = client.patch(f"/api/tasks/{sample_task.id}", json=update_data, headers=auth_headers)

        assert response.status_code == 400

    def test_update_task_not_found(self, client, auth_headers):
        """Test updating non-existent task"""
        update_data = {"title": "New Title"}

        response = client.patch("/api/tasks/9999", json=update_data, headers=auth_headers)

        assert response.status_code == 404

    def test_delete_task(self, client, auth_headers, sample_task, db):
        """Test deleting a task"""
        task_id = sample_task.id

        response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_task_not_found(self, client, auth_headers):
        """Test deleting non-existent task"""
        response = client.delete("/api/tasks/9999", headers=auth_headers)

        assert response.status_code == 404


class TestTaskFiltering:
    """Test task filtering and search functionality"""

    def test_filter_by_status(self, client, auth_headers, test_user, db):
        """Test filtering tasks by status"""
        from models import Task

        tasks = [
            Task(user_id=test_user.id, title="Pending Task", priority=1, status="pending"),
            Task(user_id=test_user.id, title="Completed Task", priority=1, status="completed"),
            Task(user_id=test_user.id, title="In Progress Task", priority=1, status="in_progress"),
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/tasks/?status=pending", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"

    def test_filter_by_category(self, client, auth_headers, test_user, db):
        """Test filtering tasks by category"""
        from models import Task

        tasks = [
            Task(user_id=test_user.id, title="Dev Task", priority=1, category="development"),
            Task(user_id=test_user.id, title="Test Task", priority=1, category="testing"),
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/tasks/?category=development", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "development"

    def test_filter_by_priority(self, client, auth_headers, test_user, db):
        """Test filtering tasks by priority"""
        from models import Task

        tasks = [
            Task(user_id=test_user.id, title="High Priority", priority=1),
            Task(user_id=test_user.id, title="Low Priority", priority=5),
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/tasks/?priority=1", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["priority"] == 1

    def test_filter_by_goal(self, client, auth_headers, test_user, sample_goal, db):
        """Test filtering tasks by parent goal"""
        from models import Task

        tasks = [
            Task(user_id=test_user.id, title="Goal Task", priority=1, parent_goal_id=sample_goal.id),
            Task(user_id=test_user.id, title="No Goal Task", priority=1),
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get(f"/api/tasks/?goal_id={sample_goal.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["parent_goal_id"] == sample_goal.id

    def test_search_tasks(self, client, auth_headers, test_user, db):
        """Test searching tasks by title/description"""
        from models import Task

        tasks = [
            Task(user_id=test_user.id, title="Build Feature", description="Build the login feature", priority=1),
            Task(user_id=test_user.id, title="Fix Bug", description="Fix the checkout bug", priority=1),
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/tasks/?search=feature", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Feature" in data[0]["title"]

    def test_search_in_description(self, client, auth_headers, test_user, db):
        """Test searching in task description"""
        from models import Task

        task = Task(
            user_id=test_user.id,
            title="Generic Task",
            description="This task involves authentication",
            priority=1
        )
        db.add(task)
        db.commit()

        response = client.get("/api/tasks/?search=authentication", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_combined_filters(self, client, auth_headers, test_user, db):
        """Test combining multiple filters"""
        from models import Task

        tasks = [
            Task(user_id=test_user.id, title="Active Dev", priority=1, status="pending", category="development"),
            Task(user_id=test_user.id, title="Completed Dev", priority=1, status="completed", category="development"),
            Task(user_id=test_user.id, title="Active Test", priority=1, status="pending", category="testing"),
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/tasks/?status=pending&category=development", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Active Dev"

    def test_pagination(self, client, auth_headers, test_user, db):
        """Test pagination with limit and offset"""
        from models import Task

        tasks = [Task(user_id=test_user.id, title=f"Task {i}", priority=i % 5 + 1) for i in range(10)]
        db.add_all(tasks)
        db.commit()

        # First page
        response = client.get("/api/tasks/?limit=3&offset=0", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Second page
        response = client.get("/api/tasks/?limit=3&offset=3", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


class TestTaskCompletion:
    """Test task completion and uncomplete operations"""

    def test_complete_task(self, client, auth_headers, sample_task):
        """Test marking a task as completed"""
        response = client.post(f"/api/tasks/{sample_task.id}/complete", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    def test_complete_task_with_actual_hours(self, client, auth_headers, sample_task):
        """Test completing task with actual hours"""
        response = client.post(
            f"/api/tasks/{sample_task.id}/complete",
            json={"actual_hours": 3.5},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["actual_hours"] == 3.5

    def test_complete_already_completed_task(self, client, auth_headers, test_user, db):
        """Test completing an already completed task"""
        from models import Task

        task = Task(
            user_id=test_user.id,
            title="Completed Task",
            priority=1,
            status="completed",
            completed_at=datetime.utcnow()
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        response = client.post(f"/api/tasks/{task.id}/complete", headers=auth_headers)

        assert response.status_code == 400
        assert "already completed" in response.json()["detail"]

    def test_complete_task_not_found(self, client, auth_headers):
        """Test completing non-existent task"""
        response = client.post("/api/tasks/9999/complete", headers=auth_headers)

        assert response.status_code == 404

    def test_uncomplete_task(self, client, auth_headers, test_user, db):
        """Test marking a completed task as pending"""
        from models import Task

        task = Task(
            user_id=test_user.id,
            title="Completed Task",
            priority=1,
            status="completed",
            completed_at=datetime.utcnow()
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        response = client.post(f"/api/tasks/{task.id}/uncomplete", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["completed_at"] is None

    def test_uncomplete_pending_task(self, client, auth_headers, sample_task):
        """Test uncompleting a task that's not completed"""
        response = client.post(f"/api/tasks/{sample_task.id}/uncomplete", headers=auth_headers)

        assert response.status_code == 400
        assert "not completed" in response.json()["detail"]

    def test_uncomplete_task_not_found(self, client, auth_headers):
        """Test uncompleting non-existent task"""
        response = client.post("/api/tasks/9999/uncomplete", headers=auth_headers)

        assert response.status_code == 404


class TestTaskStats:
    """Test task statistics endpoint"""

    def test_get_task_stats(self, client, auth_headers, test_user, db):
        """Test getting task statistics"""
        from models import Task

        tasks = [
            Task(user_id=test_user.id, title="Pending 1", priority=1, status="pending", category="dev"),
            Task(user_id=test_user.id, title="Pending 2", priority=2, status="pending", category="dev"),
            Task(user_id=test_user.id, title="Completed", priority=1, status="completed", category="test"),
            Task(user_id=test_user.id, title="In Progress", priority=3, status="in_progress"),
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/tasks/stats/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert data["by_status"]["pending"] == 2
        assert data["by_status"]["completed"] == 1
        assert data["by_status"]["in_progress"] == 1
        assert data["by_priority"]["1"] == 2  # JSON keys are strings
        assert data["by_priority"]["2"] == 1
        assert data["by_category"]["dev"] == 2
        assert data["by_category"]["test"] == 1

    def test_get_task_stats_empty(self, client, auth_headers):
        """Test stats with no tasks"""
        response = client.get("/api/tasks/stats/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["by_status"] == {}
        assert data["by_priority"] == {}

    def test_get_task_stats_overdue(self, client, auth_headers, test_user, db):
        """Test overdue task count in statistics"""
        from models import Task

        tasks = [
            Task(
                user_id=test_user.id,
                title="Overdue Task",
                priority=1,
                status="pending",
                due_date=datetime.utcnow() - timedelta(days=1)
            ),
            Task(
                user_id=test_user.id,
                title="Future Task",
                priority=1,
                status="pending",
                due_date=datetime.utcnow() + timedelta(days=1)
            ),
            Task(
                user_id=test_user.id,
                title="Completed Overdue",
                priority=1,
                status="completed",
                due_date=datetime.utcnow() - timedelta(days=1)
            ),
        ]
        db.add_all(tasks)
        db.commit()

        response = client.get("/api/tasks/stats/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["overdue"] == 1  # Only pending overdue tasks count


class TestTaskAuthorization:
    """Test authorization and data isolation"""

    def test_user_cannot_see_other_user_tasks(self, client, test_user, test_user2, db):
        """Test users can only see their own tasks"""
        from models import Task
        from api.main import app
        from api.auth import get_current_user, TokenData

        user1_task = Task(user_id=test_user.id, title="User 1 Task", priority=1)
        user2_task = Task(user_id=test_user2.id, title="User 2 Task", priority=1)
        db.add_all([user1_task, user2_task])
        db.commit()

        # Set up user 1 auth
        token_data_user1 = TokenData(
            user_id=test_user.id, username=test_user.username,
            email=test_user.email, is_admin=False, exp=9999999999
        )
        app.dependency_overrides[get_current_user] = lambda: token_data_user1

        # User 1 sees only their task
        response = client.get("/api/tasks/", headers={"Authorization": "Bearer fake"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "User 1 Task"

        # Switch to user 2 auth
        token_data_user2 = TokenData(
            user_id=test_user2.id, username=test_user2.username,
            email=test_user2.email, is_admin=False, exp=9999999999
        )
        app.dependency_overrides[get_current_user] = lambda: token_data_user2

        # User 2 sees only their task
        response = client.get("/api/tasks/", headers={"Authorization": "Bearer fake"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "User 2 Task"

    def test_user_cannot_get_other_user_task(self, client, test_user, test_user2, db):
        """Test user cannot access another user's task by ID"""
        from models import Task
        from api.main import app
        from api.auth import get_current_user, TokenData

        task = Task(user_id=test_user.id, title="User 1 Task", priority=1)
        db.add(task)
        db.commit()
        db.refresh(task)

        # Set up user 2 auth
        token_data = TokenData(
            user_id=test_user2.id, username=test_user2.username,
            email=test_user2.email, is_admin=False, exp=9999999999
        )
        app.dependency_overrides[get_current_user] = lambda: token_data

        # User 2 tries to get User 1's task
        response = client.get(f"/api/tasks/{task.id}", headers={"Authorization": "Bearer fake"})

        assert response.status_code == 404

    def test_user_cannot_modify_other_user_task(self, client, test_user, test_user2, db):
        """Test user cannot modify another user's task"""
        from models import Task
        from api.main import app
        from api.auth import get_current_user, TokenData

        task = Task(user_id=test_user.id, title="User 1 Task", priority=1)
        db.add(task)
        db.commit()
        db.refresh(task)

        # Set up user 2 auth
        token_data = TokenData(
            user_id=test_user2.id, username=test_user2.username,
            email=test_user2.email, is_admin=False, exp=9999999999
        )
        app.dependency_overrides[get_current_user] = lambda: token_data

        # User 2 tries to update User 1's task
        response = client.patch(
            f"/api/tasks/{task.id}",
            json={"title": "Hacked"},
            headers={"Authorization": "Bearer fake"}
        )

        assert response.status_code == 404

        # Verify task unchanged
        db.refresh(task)
        assert task.title == "User 1 Task"

    def test_user_cannot_delete_other_user_task(self, client, test_user, test_user2, db):
        """Test user cannot delete another user's task"""
        from models import Task
        from api.main import app
        from api.auth import get_current_user, TokenData

        task = Task(user_id=test_user.id, title="User 1 Task", priority=1)
        db.add(task)
        db.commit()
        db.refresh(task)

        # Set up user 2 auth
        token_data = TokenData(
            user_id=test_user2.id, username=test_user2.username,
            email=test_user2.email, is_admin=False, exp=9999999999
        )
        app.dependency_overrides[get_current_user] = lambda: token_data

        # User 2 tries to delete User 1's task
        response = client.delete(f"/api/tasks/{task.id}", headers={"Authorization": "Bearer fake"})

        assert response.status_code == 404

        # Verify task still exists
        db.refresh(task)
        assert task is not None

    def test_user_cannot_complete_other_user_task(self, client, test_user, test_user2, db):
        """Test user cannot complete another user's task"""
        from models import Task
        from api.main import app
        from api.auth import get_current_user, TokenData

        task = Task(user_id=test_user.id, title="User 1 Task", priority=1, status="pending")
        db.add(task)
        db.commit()
        db.refresh(task)

        # Set up user 2 auth
        token_data = TokenData(
            user_id=test_user2.id, username=test_user2.username,
            email=test_user2.email, is_admin=False, exp=9999999999
        )
        app.dependency_overrides[get_current_user] = lambda: token_data

        # User 2 tries to complete User 1's task
        response = client.post(f"/api/tasks/{task.id}/complete", headers={"Authorization": "Bearer fake"})

        assert response.status_code == 404

        # Verify task unchanged
        db.refresh(task)
        assert task.status == "pending"

    def test_user_cannot_link_task_to_other_user_goal(self, client, auth_headers, test_user, test_user2, db):
        """Test user cannot link task to another user's goal"""
        from models import Goal

        other_goal = Goal(user_id=test_user2.id, title="Other User Goal", horizon="monthly", progress_percentage=0)
        db.add(other_goal)
        db.commit()
        db.refresh(other_goal)

        task_data = {
            "title": "My Task",
            "priority": 1,
            "parent_goal_id": other_goal.id
        }

        response = client.post("/api/tasks/", json=task_data, headers=auth_headers)

        assert response.status_code == 400
        assert "not found" in response.json()["detail"]
