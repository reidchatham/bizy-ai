"""
Analytics API Routes

Comprehensive analytics endpoints for tasks, goals, velocity, and productivity metrics.
All endpoints require JWT authentication.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from api.auth import get_current_user, TokenData
from api.dependencies import get_db
from models import Goal as GoalModel, Task as TaskModel


router = APIRouter()


# Response Models

class TaskAnalyticsResponse(BaseModel):
    """Task analytics response"""
    period_days: int
    tasks_completed: int
    tasks_created: int
    tasks_pending: int
    tasks_in_progress: int
    tasks_blocked: int
    completion_rate: float
    total_estimated_hours: float
    total_actual_hours: float
    by_category: dict
    by_priority: dict
    by_status: dict
    overdue_count: int


class GoalAnalyticsResponse(BaseModel):
    """Goal analytics response"""
    total_goals: int
    active_goals: int
    completed_goals: int
    on_hold_goals: int
    cancelled_goals: int
    average_progress: float
    by_horizon: dict
    goals_near_completion: int
    goals_at_risk: int


class VelocityMetricsResponse(BaseModel):
    """Velocity and productivity metrics"""
    period_days: int
    velocity: float
    tasks_per_day: float
    completion_trend: str
    productivity_score: float
    best_day: Optional[dict]
    worst_day: Optional[dict]
    daily_breakdown: list[dict]


class TrendAnalysisResponse(BaseModel):
    """Trend analysis over time"""
    period_days: int
    completion_trend: list[dict]
    category_trends: dict
    priority_distribution: list[dict]
    goal_progress_trend: list[dict]
    insights: list[str]


# Routes

@router.get("/tasks", response_model=TaskAnalyticsResponse)
async def get_task_analytics(
    days: int = Query(default=7, ge=1, le=90, description="Number of days to analyze"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive task analytics

    Provides:
    - Completion statistics
    - Time tracking (estimated vs actual)
    - Breakdown by category, priority, status
    - Overdue task count

    Args:
        days: Number of days to analyze (default: 7, max: 90)

    Returns:
        Task analytics for the specified period
    """
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)

    # Tasks completed in period
    completed_tasks = db.query(TaskModel).filter(
        and_(
            TaskModel.user_id == current_user.user_id,
            TaskModel.status == "completed",
            TaskModel.completed_at >= start_date,
            TaskModel.completed_at <= now
        )
    ).all()

    # Tasks created in period
    created_count = db.query(func.count(TaskModel.id)).filter(
        and_(
            TaskModel.user_id == current_user.user_id,
            TaskModel.created_at >= start_date,
            TaskModel.created_at <= now
        )
    ).scalar() or 0

    # Current task counts by status
    status_counts = db.query(
        TaskModel.status,
        func.count(TaskModel.id)
    ).filter(
        TaskModel.user_id == current_user.user_id
    ).group_by(TaskModel.status).all()

    by_status = {status: count for status, count in status_counts}

    # Completion rate
    completion_rate = (len(completed_tasks) / created_count * 100) if created_count > 0 else 0

    # Time tracking
    total_estimated = sum(t.estimated_hours or 0 for t in completed_tasks)
    total_actual = sum(t.actual_hours or 0 for t in completed_tasks)

    # By category
    by_category = {}
    for task in completed_tasks:
        category = task.category or "uncategorized"
        by_category[category] = by_category.get(category, 0) + 1

    # By priority
    by_priority = {}
    for task in completed_tasks:
        priority = str(task.priority)
        by_priority[priority] = by_priority.get(priority, 0) + 1

    # Overdue tasks
    overdue_count = db.query(func.count(TaskModel.id)).filter(
        and_(
            TaskModel.user_id == current_user.user_id,
            TaskModel.status != "completed",
            TaskModel.due_date < now
        )
    ).scalar() or 0

    return TaskAnalyticsResponse(
        period_days=days,
        tasks_completed=len(completed_tasks),
        tasks_created=created_count,
        tasks_pending=by_status.get("pending", 0),
        tasks_in_progress=by_status.get("in_progress", 0),
        tasks_blocked=by_status.get("blocked", 0),
        completion_rate=round(completion_rate, 2),
        total_estimated_hours=round(total_estimated, 2),
        total_actual_hours=round(total_actual, 2),
        by_category=by_category,
        by_priority=by_priority,
        by_status=by_status,
        overdue_count=overdue_count
    )


@router.get("/goals", response_model=GoalAnalyticsResponse)
async def get_goal_analytics(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive goal analytics

    Provides:
    - Goal counts by status
    - Average progress
    - Breakdown by horizon
    - Goals near completion (>= 80%)
    - Goals at risk (< 20% progress, past mid-point)

    Returns:
        Goal analytics for all user goals
    """
    # Total goals
    total_goals = db.query(func.count(GoalModel.id)).filter(
        GoalModel.user_id == current_user.user_id
    ).scalar() or 0

    # By status
    status_counts = db.query(
        GoalModel.status,
        func.count(GoalModel.id)
    ).filter(
        GoalModel.user_id == current_user.user_id
    ).group_by(GoalModel.status).all()

    status_dict = {status: count for status, count in status_counts}
    active_goals = status_dict.get("active", 0)
    completed_goals = status_dict.get("completed", 0)
    on_hold_goals = status_dict.get("on_hold", 0)
    cancelled_goals = status_dict.get("cancelled", 0)

    # Average progress (active goals only)
    avg_progress = db.query(func.avg(GoalModel.progress_percentage)).filter(
        and_(
            GoalModel.user_id == current_user.user_id,
            GoalModel.status == "active"
        )
    ).scalar() or 0

    # By horizon
    horizon_counts = db.query(
        GoalModel.horizon,
        func.count(GoalModel.id)
    ).filter(
        GoalModel.user_id == current_user.user_id
    ).group_by(GoalModel.horizon).all()

    by_horizon = {horizon: count for horizon, count in horizon_counts}

    # Goals near completion (>= 80% progress, active)
    near_completion = db.query(func.count(GoalModel.id)).filter(
        and_(
            GoalModel.user_id == current_user.user_id,
            GoalModel.status == "active",
            GoalModel.progress_percentage >= 80
        )
    ).scalar() or 0

    # Goals at risk (< 20% progress with target date past mid-point)
    now = datetime.utcnow()
    at_risk = db.query(func.count(GoalModel.id)).filter(
        and_(
            GoalModel.user_id == current_user.user_id,
            GoalModel.status == "active",
            GoalModel.progress_percentage < 20,
            GoalModel.target_date < now + timedelta(days=30)  # Less than 30 days to target
        )
    ).scalar() or 0

    return GoalAnalyticsResponse(
        total_goals=total_goals,
        active_goals=active_goals,
        completed_goals=completed_goals,
        on_hold_goals=on_hold_goals,
        cancelled_goals=cancelled_goals,
        average_progress=round(avg_progress, 2),
        by_horizon=by_horizon,
        goals_near_completion=near_completion,
        goals_at_risk=at_risk
    )


@router.get("/velocity", response_model=VelocityMetricsResponse)
async def get_velocity_metrics(
    days: int = Query(default=30, ge=7, le=90, description="Number of days to analyze"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get velocity and productivity metrics

    Calculates:
    - Tasks completed per day (velocity)
    - Productivity score
    - Best and worst days
    - Daily breakdown
    - Completion trend (improving/declining/stable)

    Args:
        days: Number of days to analyze (default: 30, max: 90)

    Returns:
        Velocity and productivity metrics
    """
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)

    # Get completed tasks with dates
    completed_tasks = db.query(TaskModel).filter(
        and_(
            TaskModel.user_id == current_user.user_id,
            TaskModel.status == "completed",
            TaskModel.completed_at >= start_date,
            TaskModel.completed_at <= now
        )
    ).all()

    # Calculate velocity
    velocity = len(completed_tasks) / days if days > 0 else 0

    # Daily breakdown
    daily_counts = {}
    for task in completed_tasks:
        date_key = task.completed_at.date()
        daily_counts[date_key] = daily_counts.get(date_key, 0) + 1

    daily_breakdown = [
        {
            "date": date.isoformat(),
            "tasks_completed": count
        }
        for date, count in sorted(daily_counts.items())
    ]

    # Best and worst days
    best_day = None
    worst_day = None
    if daily_counts:
        best_date = max(daily_counts, key=daily_counts.get)
        best_day = {
            "date": best_date.isoformat(),
            "tasks_completed": daily_counts[best_date]
        }

        # Only set worst day if there are multiple days
        if len(daily_counts) > 1:
            worst_date = min(daily_counts, key=daily_counts.get)
            worst_day = {
                "date": worst_date.isoformat(),
                "tasks_completed": daily_counts[worst_date]
            }

    # Calculate completion trend (first half vs second half)
    midpoint = start_date + timedelta(days=days/2)
    first_half = [t for t in completed_tasks if t.completed_at < midpoint]
    second_half = [t for t in completed_tasks if t.completed_at >= midpoint]

    first_half_velocity = len(first_half) / (days/2)
    second_half_velocity = len(second_half) / (days/2)

    if second_half_velocity > first_half_velocity * 1.1:
        trend = "improving"
    elif second_half_velocity < first_half_velocity * 0.9:
        trend = "declining"
    else:
        trend = "stable"

    # Productivity score (0-100)
    # Based on: velocity, trend, completion rate of high priority tasks
    high_priority_completed = len([t for t in completed_tasks if t.priority <= 2])
    high_priority_ratio = high_priority_completed / len(completed_tasks) if completed_tasks else 0

    productivity_score = min(100, (
        (velocity * 10) * 0.5 +  # Velocity component
        (high_priority_ratio * 100) * 0.3 +  # Priority component
        (50 if trend == "improving" else 30 if trend == "stable" else 10) * 0.2  # Trend component
    ))

    return VelocityMetricsResponse(
        period_days=days,
        velocity=round(velocity, 2),
        tasks_per_day=round(velocity, 2),
        completion_trend=trend,
        productivity_score=round(productivity_score, 1),
        best_day=best_day,
        worst_day=worst_day,
        daily_breakdown=daily_breakdown
    )


@router.get("/trends", response_model=TrendAnalysisResponse)
async def get_trend_analysis(
    days: int = Query(default=30, ge=7, le=90, description="Number of days to analyze"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get trend analysis over time

    Analyzes:
    - Weekly completion trends
    - Category trends over time
    - Priority distribution changes
    - Goal progress trends
    - AI-generated insights

    Args:
        days: Number of days to analyze (default: 30, max: 90)

    Returns:
        Trend analysis with insights
    """
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)

    # Get completed tasks
    completed_tasks = db.query(TaskModel).filter(
        and_(
            TaskModel.user_id == current_user.user_id,
            TaskModel.status == "completed",
            TaskModel.completed_at >= start_date,
            TaskModel.completed_at <= now
        )
    ).all()

    # Weekly completion trend
    weeks = days // 7
    weekly_trends = []

    for week in range(weeks):
        week_start = start_date + timedelta(days=week * 7)
        week_end = week_start + timedelta(days=7)

        week_tasks = [
            t for t in completed_tasks
            if week_start <= t.completed_at < week_end
        ]

        weekly_trends.append({
            "week": week + 1,
            "week_start": week_start.date().isoformat(),
            "week_end": week_end.date().isoformat(),
            "tasks_completed": len(week_tasks),
            "total_hours": sum(t.estimated_hours or 0 for t in week_tasks)
        })

    # Category trends (top 5 categories)
    category_weekly = {}
    for task in completed_tasks:
        category = task.category or "uncategorized"
        if category not in category_weekly:
            category_weekly[category] = []

        week_num = (task.completed_at - start_date).days // 7
        if week_num < len(category_weekly[category]):
            category_weekly[category][week_num] += 1
        else:
            while len(category_weekly[category]) <= week_num:
                category_weekly[category].append(0)
            category_weekly[category][week_num] = 1

    # Get top 5 categories by total count
    category_totals = {cat: sum(counts) for cat, counts in category_weekly.items()}
    top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]

    category_trends = {
        cat: category_weekly[cat]
        for cat, _ in top_categories
    }

    # Priority distribution over time
    priority_dist = []
    for week in range(weeks):
        week_start = start_date + timedelta(days=week * 7)
        week_end = week_start + timedelta(days=7)

        week_tasks = [
            t for t in completed_tasks
            if week_start <= t.completed_at < week_end
        ]

        priority_counts = {}
        for task in week_tasks:
            priority_counts[task.priority] = priority_counts.get(task.priority, 0) + 1

        priority_dist.append({
            "week": week + 1,
            "high_priority": priority_counts.get(1, 0) + priority_counts.get(2, 0),
            "medium_priority": priority_counts.get(3, 0),
            "low_priority": priority_counts.get(4, 0) + priority_counts.get(5, 0)
        })

    # Goal progress trend (if goals exist)
    goals = db.query(GoalModel).filter(
        GoalModel.user_id == current_user.user_id
    ).all()

    goal_progress_trend = [
        {
            "goal_id": g.id,
            "goal_title": g.title,
            "current_progress": g.progress_percentage,
            "horizon": g.horizon
        }
        for g in goals if g.status == "active"
    ]

    # Generate insights
    insights = []

    # Velocity insight
    if len(weekly_trends) >= 2:
        recent_velocity = weekly_trends[-1]["tasks_completed"]
        prev_velocity = weekly_trends[-2]["tasks_completed"]

        if recent_velocity > prev_velocity * 1.2:
            insights.append("📈 Productivity spike: Last week showed 20%+ increase in task completion")
        elif recent_velocity < prev_velocity * 0.8:
            insights.append("📉 Productivity dip: Last week showed 20%+ decrease in task completion")

    # Category insight
    if top_categories:
        top_cat, top_count = top_categories[0]
        insights.append(f"🎯 Top focus area: '{top_cat}' accounts for {top_count} completed tasks")

    # Priority insight
    high_priority_count = sum(1 for t in completed_tasks if t.priority <= 2)
    if high_priority_count / len(completed_tasks) > 0.6 if completed_tasks else False:
        insights.append("⭐ Strong priority discipline: 60%+ of completed tasks were high priority")

    # Goal insight
    if goal_progress_trend:
        avg_goal_progress = sum(g["current_progress"] for g in goal_progress_trend) / len(goal_progress_trend)
        if avg_goal_progress >= 70:
            insights.append(f"🎉 Goals on track: Average progress is {avg_goal_progress:.0f}%")
        elif avg_goal_progress < 30:
            insights.append(f"⚠️ Goals need attention: Average progress is only {avg_goal_progress:.0f}%")

    return TrendAnalysisResponse(
        period_days=days,
        completion_trend=weekly_trends,
        category_trends=category_trends,
        priority_distribution=priority_dist,
        goal_progress_trend=goal_progress_trend,
        insights=insights
    )
