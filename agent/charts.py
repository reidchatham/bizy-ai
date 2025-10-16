"""Terminal Charts for Bizy AI using plotext

Provides beautiful terminal-based visualizations:
- Velocity trend charts
- Goal progress comparisons
- Category distribution
- Burndown charts
- Productivity heatmaps
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import plotext as plt
from agent.tasks import TaskManager
from agent.planner import BusinessPlanner
from agent.models import Task, Goal


class ChartGenerator:
    """Generate terminal-based charts using plotext"""

    def __init__(self):
        self.task_mgr = TaskManager()
        self.planner = BusinessPlanner()

    def close(self):
        """Close database connections"""
        self.task_mgr.close()
        self.planner.close()

    def velocity_chart(self, days: int = 30) -> str:
        """Generate velocity trend chart over time

        Args:
            days: Number of days to analyze

        Returns:
            String representation of the chart
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Calculate 7-day rolling velocity
        date_labels = []
        velocities = []
        window_size = 7

        for i in range(days - window_size + 1):
            window_end = start_date + timedelta(days=i + window_size)
            window_start = window_end - timedelta(days=window_size)

            # Get tasks completed in this window
            completed_tasks = self.task_mgr.session.query(Task).filter(
                Task.status == 'completed',
                Task.completed_at >= window_start,
                Task.completed_at < window_end
            ).count()

            velocity = completed_tasks / window_size
            date_labels.append(window_end.strftime('%m/%d'))
            velocities.append(velocity)

        # Clear any previous plots
        plt.clear_figure()

        if not velocities:
            plt.text("No data available", 0, 0)
            return plt.build()

        # Use numeric x-axis
        x_values = list(range(len(velocities)))

        # Create line chart
        plt.plot(x_values, velocities, marker="braille", color="cyan")
        plt.title(f"Task Velocity (7-day rolling average) - Last {days} days")
        plt.xlabel("Date")
        plt.ylabel("Tasks/Day")

        # Set reasonable y-axis limits
        max_vel = max(velocities)
        plt.ylim(0, max_vel * 1.2 if max_vel > 0 else 1)

        # Show date labels at regular intervals
        step = max(1, len(date_labels) // 10)
        label_indices = list(range(0, len(date_labels), step))
        plt.xticks(label_indices, [date_labels[i] for i in label_indices])

        # Build chart string
        return plt.build()

    def goal_progress_chart(self) -> str:
        """Generate horizontal bar chart of goal progress

        Returns:
            String representation of the chart
        """
        goals = self.planner.get_active_goals()

        if not goals:
            plt.clear_figure()
            plt.text("No active goals", 0, 0)
            return plt.build()

        # Sort by progress
        goals = sorted(goals, key=lambda g: g.progress_percentage, reverse=True)

        # Limit to top 10 goals
        goals = goals[:10]

        goal_titles = [g.title[:30] for g in goals]
        progress_values = [g.progress_percentage for g in goals]

        plt.clear_figure()
        plt.bar(goal_titles, progress_values, orientation="horizontal", color="green")
        plt.title("Goal Progress Overview")
        plt.xlabel("Progress (%)")
        plt.xlim(0, 100)

        return plt.build()

    def category_distribution(self, days: int = 30) -> str:
        """Generate pie chart of task completion by category

        Args:
            days: Number of days to analyze

        Returns:
            String representation of the chart
        """
        start_date = datetime.now() - timedelta(days=days)

        # Get completed tasks in time period
        completed_tasks = self.task_mgr.session.query(Task).filter(
            Task.status == 'completed',
            Task.completed_at >= start_date
        ).all()

        if not completed_tasks:
            plt.clear_figure()
            plt.text("No completed tasks in this period", 0, 0)
            return plt.build()

        # Count by category
        category_counts = defaultdict(int)
        for task in completed_tasks:
            category = task.category or "Uncategorized"
            category_counts[category] += 1

        categories = list(category_counts.keys())
        counts = list(category_counts.values())

        plt.clear_figure()

        # plotext doesn't have pie charts, use horizontal bar instead
        plt.bar(categories, counts, orientation="horizontal", color="yellow")
        plt.title(f"Task Distribution by Category (Last {days} days)")
        plt.xlabel("Task Count")

        return plt.build()

    def burndown_chart(self, goal_id: int) -> str:
        """Generate burndown chart for a specific goal

        Args:
            goal_id: Goal ID to create burndown for

        Returns:
            String representation of the chart
        """
        goal = self.planner.get_goal(goal_id)

        if not goal:
            plt.clear_figure()
            plt.text(f"Goal {goal_id} not found", 0, 0)
            return plt.build()

        # Get all tasks for this goal
        tasks = self.task_mgr.session.query(Task).filter(
            Task.parent_goal_id == goal_id
        ).order_by(Task.completed_at.asc()).all()

        if not tasks:
            plt.clear_figure()
            plt.text("No tasks for this goal", 0, 0)
            return plt.build()

        # Calculate burndown data
        total_tasks = len(tasks)
        completed_tasks = [t for t in tasks if t.status == 'completed' and t.completed_at]

        if not completed_tasks:
            plt.clear_figure()
            plt.text("No completed tasks yet", 0, 0)
            return plt.build()

        # Get date range
        start_date = min(t.completed_at for t in completed_tasks).date()
        end_date = datetime.now().date()

        # Calculate remaining tasks per day
        date_labels = []
        remaining = []
        current_date = start_date
        completed_count = 0

        while current_date <= end_date:
            # Count tasks completed up to this date
            completed_count = sum(
                1 for t in completed_tasks
                if t.completed_at.date() <= current_date
            )

            date_labels.append(current_date.strftime('%m/%d'))
            remaining.append(total_tasks - completed_count)
            current_date += timedelta(days=1)

        plt.clear_figure()

        # Use numeric x-axis
        x_values = list(range(len(remaining)))
        plt.plot(x_values, remaining, marker="braille", color="red")
        plt.title(f"Burndown Chart: {goal.title[:40]}")
        plt.xlabel("Date")
        plt.ylabel("Tasks Remaining")

        # Show date labels at regular intervals
        step = max(1, len(date_labels) // 10)
        label_indices = list(range(0, len(date_labels), step))
        plt.xticks(label_indices, [date_labels[i] for i in label_indices])

        # Add ideal line if target date exists
        if goal.target_date:
            ideal_x = [0, len(x_values) - 1]
            ideal_remaining = [total_tasks, 0]
            plt.plot(ideal_x, ideal_remaining, marker="braille", color="blue", label="Ideal")

        return plt.build()

    def productivity_heatmap(self, days: int = 30) -> str:
        """Generate productivity heatmap by day of week and hour

        Args:
            days: Number of days to analyze

        Returns:
            String representation of the chart
        """
        start_date = datetime.now() - timedelta(days=days)

        completed_tasks = self.task_mgr.session.query(Task).filter(
            Task.status == 'completed',
            Task.completed_at >= start_date
        ).all()

        if not completed_tasks:
            plt.clear_figure()
            plt.text("No completed tasks in this period", 0, 0)
            return plt.build()

        # Count by day of week
        day_counts = defaultdict(int)
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for task in completed_tasks:
            day_counts[day_names[task.completed_at.weekday()]] += 1

        # Fill in missing days with 0
        for day in day_names:
            if day not in day_counts:
                day_counts[day] = 0

        days_ordered = [day_names[i] for i in range(7)]
        counts = [day_counts[day] for day in days_ordered]

        plt.clear_figure()
        plt.bar(days_ordered, counts, color="magenta")
        plt.title(f"Productivity by Day of Week (Last {days} days)")
        plt.xlabel("Day")
        plt.ylabel("Tasks Completed")

        return plt.build()

    def priority_breakdown(self, days: int = 30) -> str:
        """Generate priority distribution chart

        Args:
            days: Number of days to analyze

        Returns:
            String representation of the chart
        """
        start_date = datetime.now() - timedelta(days=days)

        completed_tasks = self.task_mgr.session.query(Task).filter(
            Task.status == 'completed',
            Task.completed_at >= start_date
        ).all()

        if not completed_tasks:
            plt.clear_figure()
            plt.text("No completed tasks in this period", 0, 0)
            return plt.build()

        # Count by priority
        priority_counts = defaultdict(int)
        priority_labels = {1: "High (1)", 2: "Medium (2)", 3: "Low (3)"}

        for task in completed_tasks:
            priority = task.priority or 3
            priority_counts[priority] += 1

        # Ensure all priorities are represented
        for p in [1, 2, 3]:
            if p not in priority_counts:
                priority_counts[p] = 0

        priorities = sorted(priority_counts.keys())
        labels = [priority_labels[p] for p in priorities]
        counts = [priority_counts[p] for p in priorities]

        plt.clear_figure()
        plt.bar(labels, counts, color=["red", "yellow", "green"])
        plt.title(f"Tasks by Priority (Last {days} days)")
        plt.xlabel("Priority")
        plt.ylabel("Tasks Completed")

        return plt.build()

    def comparison_chart(self, days: int = 7) -> str:
        """Compare current period vs previous period

        Args:
            days: Number of days per period

        Returns:
            String representation of the chart
        """
        now = datetime.now()

        # Current period
        current_start = now - timedelta(days=days)
        current_tasks = self.task_mgr.session.query(Task).filter(
            Task.status == 'completed',
            Task.completed_at >= current_start
        ).count()

        # Previous period
        previous_start = now - timedelta(days=days * 2)
        previous_end = current_start
        previous_tasks = self.task_mgr.session.query(Task).filter(
            Task.status == 'completed',
            Task.completed_at >= previous_start,
            Task.completed_at < previous_end
        ).count()

        periods = [f"Previous\n{days} days", f"Current\n{days} days"]
        counts = [previous_tasks, current_tasks]

        plt.clear_figure()
        plt.bar(periods, counts, color=["blue", "green"])
        plt.title("Period Comparison")
        plt.ylabel("Tasks Completed")

        return plt.build()
