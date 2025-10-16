"""Tests for terminal charts with plotext (TDD)"""

import pytest
from datetime import datetime, timedelta
from agent.tasks import TaskManager
from agent.planner import BusinessPlanner
from agent.charts import ChartGenerator


class TestChartGenerator:
    """Tests for terminal chart generation with plotext"""

    @pytest.fixture
    def chart_gen(self, test_session):
        """Create ChartGenerator with test session"""
        chart_gen = ChartGenerator()
        chart_gen.task_mgr.session = test_session
        chart_gen.planner.session = test_session
        yield chart_gen
        chart_gen.close()

    @pytest.fixture
    def historical_tasks(self, test_session):
        """Create tasks over past 14 days for chart testing"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        tasks = []
        # Create 2 tasks per day for 14 days
        for day in range(14):
            for i in range(2):
                task = task_mgr.create_task(
                    title=f"Day {day} Task {i}",
                    category="testing"
                )
                # Complete tasks with staggered times
                completion_time = datetime.now() - timedelta(days=day, hours=i*6)
                task.completed_at = completion_time
                task.status = 'completed'
                test_session.add(task)
                tasks.append(task)

        test_session.commit()
        return tasks

    def test_velocity_chart_basic(self, chart_gen, historical_tasks):
        """Test generating basic velocity trend chart"""
        # Should return string representation of chart
        chart_output = chart_gen.velocity_chart(days=14)

        assert chart_output is not None
        assert isinstance(chart_output, str)
        assert len(chart_output) > 0

    def test_velocity_chart_with_custom_days(self, chart_gen, historical_tasks):
        """Test velocity chart with custom time period"""
        chart_7day = chart_gen.velocity_chart(days=7)
        chart_30day = chart_gen.velocity_chart(days=30)

        assert isinstance(chart_7day, str)
        assert isinstance(chart_30day, str)
        # Different time periods should produce different charts
        assert chart_7day != chart_30day

    def test_velocity_chart_no_data(self, chart_gen):
        """Test velocity chart with no completed tasks"""
        chart_output = chart_gen.velocity_chart(days=7)

        # Should still return a chart, even if empty
        assert chart_output is not None
        assert isinstance(chart_output, str)

    def test_goal_progress_chart(self, chart_gen, test_session):
        """Test generating goal progress comparison chart"""
        planner = BusinessPlanner()
        planner.session = test_session

        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create 3 goals with different progress levels
        for i, progress in enumerate([25, 50, 75]):
            goal = planner.create_goal(
                title=f"Goal {i+1}",
                description=f"Goal at {progress}% completion",
                horizon="monthly"
            )

            # Create tasks to match progress level
            total_tasks = 4
            completed_tasks = progress // 25  # 1, 2, or 3 completed

            for j in range(total_tasks):
                task = task_mgr.create_task(
                    title=f"Goal {i+1} Task {j+1}",
                    parent_goal_id=goal.id
                )
                if j < completed_tasks:
                    task_mgr.complete_task(task.id)

        chart_output = chart_gen.goal_progress_chart()

        assert chart_output is not None
        assert isinstance(chart_output, str)
        assert len(chart_output) > 0

    def test_goal_progress_chart_no_goals(self, chart_gen):
        """Test goal progress chart with no active goals"""
        chart_output = chart_gen.goal_progress_chart()

        # Should handle empty state gracefully
        assert chart_output is not None
        assert isinstance(chart_output, str)

    def test_category_distribution_chart(self, chart_gen, test_session):
        """Test category distribution pie chart"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create tasks in different categories
        categories = {
            "development": 10,
            "testing": 5,
            "documentation": 3,
            "meeting": 2
        }

        for category, count in categories.items():
            for i in range(count):
                task = task_mgr.create_task(
                    title=f"{category} task {i}",
                    category=category
                )
                task.completed_at = datetime.now() - timedelta(days=i)
                task.status = 'completed'
                test_session.add(task)

        test_session.commit()

        chart_output = chart_gen.category_distribution(days=30)

        assert chart_output is not None
        assert isinstance(chart_output, str)
        assert len(chart_output) > 0

    def test_category_distribution_no_categories(self, chart_gen, test_session):
        """Test category distribution with tasks that have no category"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create tasks without categories
        for i in range(5):
            task = task_mgr.create_task(title=f"No category task {i}")
            task.completed_at = datetime.now()
            task.status = 'completed'
            test_session.add(task)

        test_session.commit()

        chart_output = chart_gen.category_distribution(days=7)

        assert chart_output is not None
        assert isinstance(chart_output, str)

    def test_burndown_chart(self, chart_gen, test_session):
        """Test burndown chart for goal"""
        planner = BusinessPlanner()
        planner.session = test_session

        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create goal with target date
        goal = planner.create_goal(
            title="Sprint Goal",
            description="Goal for burndown testing",
            horizon="weekly",
            target_date=datetime.now() + timedelta(days=7)
        )

        # Create 10 tasks, complete 6 with staggered dates
        for i in range(10):
            task = task_mgr.create_task(
                title=f"Sprint task {i}",
                parent_goal_id=goal.id
            )
            if i < 6:
                task.completed_at = datetime.now() - timedelta(days=6-i)
                task.status = 'completed'
                test_session.add(task)

        test_session.commit()

        chart_output = chart_gen.burndown_chart(goal.id)

        assert chart_output is not None
        assert isinstance(chart_output, str)
        assert len(chart_output) > 0

    def test_burndown_chart_invalid_goal(self, chart_gen):
        """Test burndown chart with invalid goal ID"""
        chart_output = chart_gen.burndown_chart(999999)

        # Should handle error gracefully
        assert chart_output is not None
        assert isinstance(chart_output, str)

    def test_productivity_heatmap(self, chart_gen, historical_tasks):
        """Test productivity heatmap by hour and day"""
        chart_output = chart_gen.productivity_heatmap(days=14)

        assert chart_output is not None
        assert isinstance(chart_output, str)
        assert len(chart_output) > 0

    def test_productivity_heatmap_no_data(self, chart_gen):
        """Test heatmap with no completed tasks"""
        chart_output = chart_gen.productivity_heatmap(days=7)

        assert chart_output is not None
        assert isinstance(chart_output, str)

    def test_priority_breakdown_chart(self, chart_gen, test_session):
        """Test priority breakdown chart"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create tasks with different priorities
        priorities = {1: 5, 2: 10, 3: 15}

        for priority, count in priorities.items():
            for i in range(count):
                task = task_mgr.create_task(
                    title=f"Priority {priority} task {i}",
                    priority=priority
                )
                task.completed_at = datetime.now()
                task.status = 'completed'
                test_session.add(task)

        test_session.commit()

        chart_output = chart_gen.priority_breakdown(days=30)

        assert chart_output is not None
        assert isinstance(chart_output, str)
        assert len(chart_output) > 0

    def test_comparison_chart(self, chart_gen, test_session):
        """Test comparison of current vs previous period"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create tasks in current period (last 7 days)
        for i in range(10):
            task = task_mgr.create_task(title=f"Current task {i}")
            task.completed_at = datetime.now() - timedelta(days=i % 7)
            task.status = 'completed'
            test_session.add(task)

        # Create tasks in previous period (8-14 days ago)
        for i in range(5):
            task = task_mgr.create_task(title=f"Previous task {i}")
            task.completed_at = datetime.now() - timedelta(days=7 + i)
            task.status = 'completed'
            test_session.add(task)

        test_session.commit()

        chart_output = chart_gen.comparison_chart(days=7)

        assert chart_output is not None
        assert isinstance(chart_output, str)
        assert len(chart_output) > 0
