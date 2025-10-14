"""Analytics and Predictions for Bizy AI

Provides velocity-based predictions and analytics:
- Goal completion date predictions
- Task completion forecasts
- Velocity trends
- Burndown charts
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from agent.tasks import TaskManager
from agent.planner import BusinessPlanner
from agent.models import Task, Goal


class VelocityPredictor:
    """Predicts goal completion dates based on historical velocity"""

    def __init__(self):
        self.task_mgr = TaskManager()
        self.planner = BusinessPlanner()

    def close(self):
        """Close database connections"""
        self.task_mgr.close()
        self.planner.close()

    def predict_goal_completion(self, goal_id: int, velocity_days: int = 30) -> Dict:
        """Predict when a goal will be completed based on current velocity

        Args:
            goal_id: Goal ID to predict
            velocity_days: Number of days to calculate velocity over

        Returns:
            Dictionary with prediction details
        """
        goal = self.planner.get_goal(goal_id)
        if not goal:
            return {"error": "Goal not found"}

        # Get remaining tasks for this goal
        remaining_tasks = self.task_mgr.session.query(Task).filter(
            Task.parent_goal_id == goal_id,
            Task.status.in_(['pending', 'in_progress'])
        ).all()

        if not remaining_tasks:
            return {
                "goal_id": goal_id,
                "goal_title": goal.title,
                "status": "complete",
                "message": "All tasks completed!",
                "remaining_tasks": 0
            }

        # Calculate velocity
        velocity = self.task_mgr.get_task_velocity(days=velocity_days)

        if velocity == 0:
            return {
                "goal_id": goal_id,
                "goal_title": goal.title,
                "status": "no_velocity",
                "message": "No completed tasks to calculate velocity",
                "remaining_tasks": len(remaining_tasks)
            }

        # Calculate days needed
        days_needed = len(remaining_tasks) / velocity
        predicted_completion = datetime.now() + timedelta(days=days_needed)

        # Calculate if on track
        on_track = True
        warning = None
        if goal.target_date:
            days_until_target = (goal.target_date - datetime.now()).days
            if days_needed > days_until_target:
                on_track = False
                days_over = days_needed - days_until_target
                warning = f"⚠️  {days_over:.0f} days behind schedule"

        return {
            "goal_id": goal_id,
            "goal_title": goal.title,
            "remaining_tasks": len(remaining_tasks),
            "current_velocity": velocity,
            "days_needed": days_needed,
            "predicted_completion": predicted_completion,
            "target_date": goal.target_date,
            "on_track": on_track,
            "warning": warning,
            "status": "predicted"
        }

    def get_all_goal_predictions(self) -> List[Dict]:
        """Get predictions for all active goals

        Returns:
            List of prediction dictionaries
        """
        goals = self.planner.get_active_goals()
        predictions = []

        for goal in goals:
            prediction = self.predict_goal_completion(goal.id)
            predictions.append(prediction)

        return predictions

    def calculate_required_velocity(self, goal_id: int) -> Dict:
        """Calculate the velocity needed to complete a goal on time

        Args:
            goal_id: Goal ID

        Returns:
            Dictionary with required velocity info
        """
        goal = self.planner.get_goal(goal_id)
        if not goal:
            return {"error": "Goal not found"}

        if not goal.target_date:
            return {"error": "Goal has no target date"}

        # Get remaining tasks
        remaining_tasks = self.task_mgr.session.query(Task).filter(
            Task.parent_goal_id == goal_id,
            Task.status.in_(['pending', 'in_progress'])
        ).count()

        if remaining_tasks == 0:
            return {
                "goal_id": goal_id,
                "goal_title": goal.title,
                "status": "complete",
                "message": "All tasks completed!"
            }

        # Calculate days until target
        days_until_target = (goal.target_date - datetime.now()).days

        if days_until_target <= 0:
            return {
                "goal_id": goal_id,
                "goal_title": goal.title,
                "status": "overdue",
                "remaining_tasks": remaining_tasks,
                "message": "Goal target date has passed"
            }

        # Calculate required velocity
        required_velocity = remaining_tasks / days_until_target
        current_velocity = self.task_mgr.get_task_velocity(days=7)

        # Compare with current velocity
        velocity_gap = required_velocity - current_velocity
        feasible = velocity_gap <= current_velocity * 0.5  # Allow 50% increase

        return {
            "goal_id": goal_id,
            "goal_title": goal.title,
            "remaining_tasks": remaining_tasks,
            "days_until_target": days_until_target,
            "required_velocity": required_velocity,
            "current_velocity": current_velocity,
            "velocity_gap": velocity_gap,
            "feasible": feasible,
            "status": "calculated"
        }

    def get_velocity_trend(self, days: int = 30) -> List[Tuple[datetime, float]]:
        """Get velocity trend over time using a rolling window

        Args:
            days: Number of days to analyze

        Returns:
            List of (date, velocity) tuples
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        trend_data = []
        window_size = 7  # 7-day rolling window

        # Calculate velocity for each day using a rolling window
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
            trend_data.append((window_end.date(), velocity))

        return trend_data

    def analyze_productivity_patterns(self) -> Dict:
        """Analyze productivity patterns by day of week and time of day

        Returns:
            Dictionary with pattern analysis
        """
        # Get all completed tasks from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        completed_tasks = self.task_mgr.session.query(Task).filter(
            Task.status == 'completed',
            Task.completed_at >= thirty_days_ago
        ).all()

        if not completed_tasks:
            return {"message": "Not enough data for pattern analysis"}

        # Analyze by day of week
        day_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}  # Monday=0, Sunday=6
        for task in completed_tasks:
            day_counts[task.completed_at.weekday()] += 1

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        best_day = max(day_counts.items(), key=lambda x: x[1])
        worst_day = min(day_counts.items(), key=lambda x: x[1])

        # Analyze by hour of day
        hour_counts = {h: 0 for h in range(24)}
        for task in completed_tasks:
            hour_counts[task.completed_at.hour] += 1

        peak_hour = max(hour_counts.items(), key=lambda x: x[1])

        return {
            "total_tasks_analyzed": len(completed_tasks),
            "days_analyzed": 30,
            "by_day_of_week": {day_names[day]: count for day, count in day_counts.items()},
            "best_day": {
                "name": day_names[best_day[0]],
                "tasks_completed": best_day[1]
            },
            "worst_day": {
                "name": day_names[worst_day[0]],
                "tasks_completed": worst_day[1]
            },
            "peak_hour": {
                "hour": peak_hour[0],
                "tasks_completed": peak_hour[1],
                "time_display": f"{peak_hour[0]:02d}:00"
            }
        }
