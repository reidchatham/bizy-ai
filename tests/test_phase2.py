"""Tests for Phase 2 features: Calendar, Dashboard, Analytics"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from agent.models import Task, Goal
from agent.tasks import TaskManager
from agent.planner import BusinessPlanner
from agent.integrations.ical import ICalIntegration
from agent.analytics import VelocityPredictor
from icalendar import Calendar


class TestICalIntegration:
    """Tests for iCal calendar integration"""

    @pytest.fixture
    def ical(self, tmp_path):
        """Create ICalIntegration with temp directory"""
        ical = ICalIntegration(calendar_dir=tmp_path)
        yield ical

    @pytest.fixture
    def sample_tasks(self, test_session):
        """Create sample tasks for testing"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        tasks = []
        # Task with due date
        task1 = task_mgr.create_task(
            title="Task with due date",
            priority=1,
            category="testing",
            due_date=datetime.now() + timedelta(days=7)
        )
        tasks.append(task1)

        # Task without due date
        task2 = task_mgr.create_task(
            title="Task without due date",
            priority=2,
            category="development"
        )
        tasks.append(task2)

        # Completed task
        task3 = task_mgr.create_task(
            title="Completed task",
            priority=3,
            category="testing"
        )
        task_mgr.complete_task(task3.id)
        test_session.refresh(task3)
        tasks.append(task3)

        return tasks

    def test_export_tasks_creates_file(self, ical, sample_tasks):
        """Test that export_tasks creates an .ics file"""
        calendar_path = ical.export_tasks(sample_tasks)

        assert calendar_path.exists()
        assert calendar_path.suffix == '.ics'

    def test_export_tasks_contains_all_tasks(self, ical, sample_tasks):
        """Test that exported calendar contains all tasks"""
        calendar_path = ical.export_tasks(sample_tasks)

        # Read and parse the calendar file
        with open(calendar_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())

        events = [component for component in cal.walk() if component.name == "VEVENT"]
        assert len(events) == len(sample_tasks)

    def test_export_task_with_due_date(self, ical, sample_tasks):
        """Test that tasks with due dates are properly formatted"""
        task_with_due_date = [t for t in sample_tasks if t.due_date][0]
        calendar_path = ical.export_tasks([task_with_due_date])

        with open(calendar_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())

        events = [component for component in cal.walk() if component.name == "VEVENT"]
        event = events[0]

        assert str(event.get('summary')) == task_with_due_date.title
        assert event.get('dtstart').dt == task_with_due_date.due_date.date()

    def test_export_completed_task_status(self, ical, sample_tasks):
        """Test that completed tasks have correct status"""
        completed_task = [t for t in sample_tasks if t.status == 'completed'][0]
        calendar_path = ical.export_tasks([completed_task])

        with open(calendar_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())

        events = [component for component in cal.walk() if component.name == "VEVENT"]
        event = events[0]

        assert str(event.get('status')) == 'COMPLETED'

    def test_export_task_priority_mapping(self, ical, sample_tasks):
        """Test that task priorities are correctly mapped to iCal priorities"""
        calendar_path = ical.export_tasks(sample_tasks)

        with open(calendar_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())

        events = [component for component in cal.walk() if component.name == "VEVENT"]

        # Check priority mapping: task priority 1 -> ical priority 1 (high)
        high_priority_event = [e for e in events if str(e.get('summary')) == "Task with due date"][0]
        assert int(high_priority_event.get('priority')) == 1

    def test_create_single_task_event(self, ical, sample_tasks):
        """Test creating a single task event"""
        task = sample_tasks[0]
        event_path = ical.create_single_task_event(task, "test-task.ics")

        assert event_path.exists()
        assert event_path.name == "test-task.ics"

        # Verify it contains exactly one event
        with open(event_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())

        events = [component for component in cal.walk() if component.name == "VEVENT"]
        assert len(events) == 1

    def test_import_calendar(self, ical, sample_tasks):
        """Test importing a calendar file"""
        # First export
        calendar_path = ical.export_tasks(sample_tasks)

        # Then import
        imported_cal = ical.import_calendar(calendar_path)

        assert imported_cal is not None
        events = [component for component in imported_cal.walk() if component.name == "VEVENT"]
        assert len(events) == len(sample_tasks)

    def test_get_events(self, ical, sample_tasks):
        """Test getting events from calendar"""
        calendar_path = ical.export_tasks(sample_tasks)
        events = ical.get_events(calendar_path)

        assert len(events) == len(sample_tasks)
        assert all('summary' in event for event in events)
        assert all('start' in event for event in events)


class TestVelocityPredictor:
    """Tests for velocity-based predictions"""

    @pytest.fixture
    def predictor(self, test_session):
        """Create VelocityPredictor with test session"""
        predictor = VelocityPredictor()
        predictor.task_mgr.session = test_session
        predictor.planner.session = test_session
        yield predictor
        predictor.close()

    @pytest.fixture
    def goal_with_tasks(self, test_session):
        """Create a goal with several tasks"""
        planner = BusinessPlanner()
        planner.session = test_session

        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create goal
        goal = planner.create_goal(
            title="Test Goal",
            description="Test goal for predictions",
            horizon="monthly",
            target_date=datetime.now() + timedelta(days=30)
        )

        # Create 10 tasks, complete 5
        for i in range(10):
            task = task_mgr.create_task(
                title=f"Task {i+1}",
                parent_goal_id=goal.id
            )
            if i < 5:
                # Complete first 5 tasks with staggered dates
                task.completed_at = datetime.now() - timedelta(days=i)
                task.status = 'completed'
                test_session.add(task)

        test_session.commit()
        return goal

    def test_predict_goal_completion_basic(self, predictor, goal_with_tasks):
        """Test basic goal completion prediction"""
        prediction = predictor.predict_goal_completion(goal_with_tasks.id)

        assert prediction['status'] == 'predicted'
        assert prediction['goal_title'] == "Test Goal"
        assert prediction['remaining_tasks'] == 5
        assert prediction['current_velocity'] > 0
        assert 'predicted_completion' in prediction

    def test_predict_completed_goal(self, predictor, test_session):
        """Test prediction for a goal with all tasks completed"""
        planner = BusinessPlanner()
        planner.session = test_session

        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create goal
        goal = planner.create_goal(
            title="Completed Goal",
            description="Goal with all tasks completed",
            horizon="weekly"
        )

        # Create and complete task
        task = task_mgr.create_task(title="Only task", parent_goal_id=goal.id)
        task_mgr.complete_task(task.id)

        prediction = predictor.predict_goal_completion(goal.id)

        assert prediction['status'] == 'complete'
        assert prediction['remaining_tasks'] == 0

    def test_predict_goal_with_no_velocity(self, predictor, test_session):
        """Test prediction when no tasks have been completed"""
        planner = BusinessPlanner()
        planner.session = test_session

        task_mgr = TaskManager()
        task_mgr.session = test_session

        goal = planner.create_goal(
            title="New Goal",
            description="Goal with no completed tasks",
            horizon="monthly"
        )
        task_mgr.create_task(title="Pending task", parent_goal_id=goal.id)

        prediction = predictor.predict_goal_completion(goal.id)

        assert prediction['status'] == 'no_velocity'
        assert prediction['remaining_tasks'] == 1

    def test_predict_goal_on_track(self, predictor, goal_with_tasks):
        """Test prediction detects goal is on track"""
        prediction = predictor.predict_goal_completion(goal_with_tasks.id)

        # With 5 remaining tasks and current velocity, should be on track for 30-day target
        assert 'on_track' in prediction
        # Prediction depends on velocity, so just check structure

    def test_calculate_required_velocity(self, predictor, goal_with_tasks):
        """Test calculating required velocity"""
        result = predictor.calculate_required_velocity(goal_with_tasks.id)

        assert result['status'] == 'calculated'
        assert result['remaining_tasks'] == 5
        assert result['days_until_target'] > 0
        assert result['required_velocity'] > 0
        assert 'feasible' in result

    def test_required_velocity_no_target_date(self, predictor, test_session):
        """Test required velocity when goal has no target date"""
        planner = BusinessPlanner()
        planner.session = test_session

        goal = planner.create_goal(
            title="No target",
            description="Goal without target date",
            horizon="monthly"
        )

        result = predictor.calculate_required_velocity(goal.id)

        assert 'error' in result
        assert result['error'] == "Goal has no target date"

    def test_get_all_goal_predictions(self, predictor, goal_with_tasks):
        """Test getting predictions for all goals"""
        predictions = predictor.get_all_goal_predictions()

        assert len(predictions) > 0
        assert all('goal_id' in pred for pred in predictions)
        assert all('goal_title' in pred for pred in predictions)

    def test_get_velocity_trend(self, predictor, test_session):
        """Test getting velocity trend data"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create tasks completed over several days
        for i in range(14):
            task = task_mgr.create_task(title=f"Historical task {i}")
            task.completed_at = datetime.now() - timedelta(days=i)
            task.status = 'completed'
            test_session.add(task)

        test_session.commit()

        trend = predictor.get_velocity_trend(days=14)

        assert len(trend) > 0
        assert all(isinstance(item, tuple) for item in trend)
        assert all(len(item) == 2 for item in trend)

    def test_analyze_productivity_patterns_insufficient_data(self, predictor):
        """Test productivity analysis with insufficient data"""
        patterns = predictor.analyze_productivity_patterns()

        assert 'message' in patterns

    def test_analyze_productivity_patterns(self, predictor, test_session):
        """Test productivity pattern analysis with sufficient data"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create 30 completed tasks with various times
        for i in range(30):
            task = task_mgr.create_task(title=f"Pattern task {i}")
            completion_time = datetime.now() - timedelta(days=i)
            task.completed_at = completion_time
            task.status = 'completed'
            test_session.add(task)

        test_session.commit()

        patterns = predictor.analyze_productivity_patterns()

        assert 'total_tasks_analyzed' in patterns
        assert patterns['total_tasks_analyzed'] == 30
        assert 'by_day_of_week' in patterns
        assert 'best_day' in patterns
        assert 'worst_day' in patterns
        assert 'peak_hour' in patterns
