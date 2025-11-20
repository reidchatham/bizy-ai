"""
Briefing API Routes

AI-powered briefing endpoints for morning, evening, and research briefings.
All endpoints require JWT authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import os

from api.auth import get_current_user, TokenData
from api.dependencies import get_db
from models import Goal as GoalModel, Task as TaskModel


router = APIRouter()


# Request/Response Models

class MorningBriefingResponse(BaseModel):
    """Morning briefing response"""
    date: datetime
    greeting: str
    yesterday_recap: dict
    todays_mission: list[dict]
    watch_out_for: list[str]
    pro_tip: str
    tasks_today: list[dict]
    active_goals: list[dict]
    overdue_tasks: list[dict]


class EveningReviewRequest(BaseModel):
    """Evening review input"""
    wins: Optional[str] = None
    blockers: Optional[str] = None
    learnings: Optional[str] = None
    energy_level: Optional[int] = Field(None, ge=1, le=10)


class EveningReviewResponse(BaseModel):
    """Evening review response"""
    date: datetime
    day_analysis: str
    wins_recognition: str
    improvement_suggestions: list[str]
    tomorrow_prep: str
    completion_stats: dict


class ResearchBriefingRequest(BaseModel):
    """Research briefing request"""
    topic: str = Field(..., min_length=3, max_length=500)
    focus_areas: Optional[list[str]] = None
    max_insights: int = Field(default=5, ge=1, le=10)


class ResearchBriefingResponse(BaseModel):
    """Research briefing response"""
    topic: str
    key_insights: list[str]
    action_items: list[str]
    relevant_goals: list[dict]
    relevant_tasks: list[dict]


# Helper Functions

def get_yesterday_summary(db: Session, user_id: int) -> dict:
    """Get yesterday's task summary"""
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    yesterday_start = datetime.combine(yesterday, datetime.min.time())
    yesterday_end = datetime.combine(yesterday, datetime.max.time())

    total_tasks = db.query(func.count(TaskModel.id)).filter(
        and_(
            TaskModel.user_id == user_id,
            TaskModel.created_at <= yesterday_end,
            TaskModel.due_date >= yesterday_start if TaskModel.due_date else True
        )
    ).scalar() or 0

    completed_tasks = db.query(func.count(TaskModel.id)).filter(
        and_(
            TaskModel.user_id == user_id,
            TaskModel.status == "completed",
            TaskModel.completed_at >= yesterday_start,
            TaskModel.completed_at <= yesterday_end
        )
    ).scalar() or 0

    completion_rate = (completed_tasks / total_tasks) if total_tasks > 0 else 0

    return {
        "tasks_completed": completed_tasks,
        "tasks_due": total_tasks,
        "completion_rate": completion_rate
    }


def get_todays_tasks(db: Session, user_id: int) -> list[dict]:
    """Get today's scheduled tasks"""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    tasks = db.query(TaskModel).filter(
        and_(
            TaskModel.user_id == user_id,
            TaskModel.status.in_(["pending", "in_progress"]),
            or_(
                TaskModel.due_date.between(today_start, today_end),
                TaskModel.due_date.is_(None)
            )
        )
    ).order_by(TaskModel.priority.asc()).limit(20).all()

    return [
        {
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "status": t.status,
            "category": t.category,
            "estimated_hours": t.estimated_hours,
            "due_date": t.due_date.isoformat() if t.due_date else None
        }
        for t in tasks
    ]


def get_active_goals(db: Session, user_id: int) -> list[dict]:
    """Get active goals"""
    goals = db.query(GoalModel).filter(
        and_(
            GoalModel.user_id == user_id,
            GoalModel.status == "active"
        )
    ).order_by(GoalModel.horizon.asc()).limit(10).all()

    return [
        {
            "id": g.id,
            "title": g.title,
            "horizon": g.horizon,
            "progress_percentage": g.progress_percentage,
            "target_date": g.target_date.isoformat() if g.target_date else None
        }
        for g in goals
    ]


def get_overdue_tasks(db: Session, user_id: int) -> list[dict]:
    """Get overdue tasks"""
    now = datetime.utcnow()

    tasks = db.query(TaskModel).filter(
        and_(
            TaskModel.user_id == user_id,
            TaskModel.status != "completed",
            TaskModel.due_date < now
        )
    ).order_by(TaskModel.due_date.asc()).limit(10).all()

    return [
        {
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "due_date": t.due_date.isoformat(),
            "days_overdue": (now.date() - t.due_date.date()).days
        }
        for t in tasks
    ]


def generate_morning_briefing_ai(
    tasks_today: list[dict],
    yesterday_summary: dict,
    goals: list[dict],
    overdue_tasks: list[dict]
) -> dict:
    """Generate AI-powered morning briefing"""
    from anthropic import Anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured (ANTHROPIC_API_KEY missing)"
        )

    client = Anthropic(api_key=api_key)

    # Format data for prompt
    tasks_str = "\n".join([
        f"- [{t['priority']}] {t['title']} ({t.get('estimated_hours', '?')}h) - {t['category'] or 'uncategorized'}"
        for t in tasks_today[:10]
    ]) or "No tasks scheduled"

    goals_str = "\n".join([
        f"- {g['title']} ({g['horizon']}) - {g['progress_percentage']}% complete"
        for g in goals
    ]) or "No active goals"

    overdue_str = "\n".join([
        f"- {t['title']} ({t['days_overdue']} days overdue)"
        for t in overdue_tasks[:5]
    ]) or "None"

    prompt = f"""You are a business execution assistant. Generate an energizing and focused morning briefing.

TODAY'S DATE: {datetime.now().strftime('%A, %B %d, %Y')}

YESTERDAY'S SUMMARY:
Tasks Completed: {yesterday_summary['tasks_completed']} of {yesterday_summary['tasks_due']}
Completion Rate: {yesterday_summary['completion_rate']:.0%}

ACTIVE GOALS:
{goals_str}

TODAY'S SCHEDULED TASKS:
{tasks_str}

OVERDUE TASKS:
{overdue_str}

Create a JSON response with this structure:
{{
    "greeting": "Brief motivational opener (1-2 sentences)",
    "todays_mission": [
        {{
            "priority": 1,
            "task": "Task name",
            "why_it_matters": "Explanation",
            "estimated_time": "2h"
        }}
    ],
    "watch_out_for": ["Potential blocker 1", "Potential blocker 2"],
    "pro_tip": "One specific, actionable suggestion"
}}

Focus on the top 3 priorities. Be concise, energizing, and actionable."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        response_text = response.content[0].text

        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        return json.loads(response_text)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )


def generate_evening_review_ai(
    completed_tasks: list[dict],
    planned_tasks: list[dict],
    wins: Optional[str],
    blockers: Optional[str],
    learnings: Optional[str],
    energy_level: Optional[int]
) -> dict:
    """Generate AI-powered evening review"""
    from anthropic import Anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured (ANTHROPIC_API_KEY missing)"
        )

    client = Anthropic(api_key=api_key)

    completion_rate = (len(completed_tasks) / len(planned_tasks)) if planned_tasks else 0

    completed_str = "\n".join([
        f"- {t['title']} ({t.get('category', 'uncategorized')})"
        for t in completed_tasks
    ]) or "None"

    incomplete_str = "\n".join([
        f"- {t['title']} (Status: {t['status']})"
        for t in planned_tasks if t['status'] != 'completed'
    ]) or "All completed!"

    prompt = f"""Analyze today's business execution and provide insights.

DATE: {datetime.now().strftime('%A, %B %d, %Y')}
COMPLETION RATE: {completion_rate:.0%} ({len(completed_tasks)}/{len(planned_tasks)} tasks)

COMPLETED TASKS:
{completed_str}

PLANNED BUT NOT COMPLETED:
{incomplete_str}

USER'S REFLECTION:
- Wins: {wins or 'Not specified'}
- Blockers: {blockers or 'None mentioned'}
- Learnings: {learnings or 'Not specified'}
- Energy Level: {energy_level or 'Not specified'}/10

Create a JSON response:
{{
    "day_analysis": "Honest assessment of today's productivity (2-3 sentences)",
    "wins_recognition": "Celebrate what went well",
    "improvement_suggestions": ["Suggestion 1", "Suggestion 2"],
    "tomorrow_prep": "What to prioritize tomorrow"
}}

Be encouraging but honest. Focus on actionable insights."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        response_text = response.content[0].text

        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        return json.loads(response_text)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )


# Routes

@router.get("/morning", response_model=MorningBriefingResponse)
async def get_morning_briefing(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered morning briefing

    Provides:
    - Yesterday's recap
    - Today's mission (top 3 priorities)
    - Potential blockers
    - Pro tip for the day
    - Task list
    - Active goals
    - Overdue tasks

    Returns:
        Morning briefing with AI-generated insights
    """
    # Gather data
    yesterday_summary = get_yesterday_summary(db, current_user.user_id)
    tasks_today = get_todays_tasks(db, current_user.user_id)
    active_goals = get_active_goals(db, current_user.user_id)
    overdue_tasks = get_overdue_tasks(db, current_user.user_id)

    # Generate AI briefing
    ai_briefing = generate_morning_briefing_ai(
        tasks_today=tasks_today,
        yesterday_summary=yesterday_summary,
        goals=active_goals,
        overdue_tasks=overdue_tasks
    )

    return MorningBriefingResponse(
        date=datetime.now(),
        greeting=ai_briefing["greeting"],
        yesterday_recap=yesterday_summary,
        todays_mission=ai_briefing["todays_mission"],
        watch_out_for=ai_briefing["watch_out_for"],
        pro_tip=ai_briefing["pro_tip"],
        tasks_today=tasks_today,
        active_goals=active_goals,
        overdue_tasks=overdue_tasks
    )


@router.post("/evening", response_model=EveningReviewResponse)
async def post_evening_review(
    review: EveningReviewRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered evening review

    User provides optional reflection:
    - Wins of the day
    - Blockers encountered
    - Learnings
    - Energy level (1-10)

    Returns:
        Evening review with AI analysis and suggestions
    """
    # Get today's tasks
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    # Completed tasks
    completed = db.query(TaskModel).filter(
        and_(
            TaskModel.user_id == current_user.user_id,
            TaskModel.status == "completed",
            TaskModel.completed_at >= today_start,
            TaskModel.completed_at <= today_end
        )
    ).all()

    # Planned tasks
    planned = db.query(TaskModel).filter(
        and_(
            TaskModel.user_id == current_user.user_id,
            or_(
                TaskModel.due_date.between(today_start, today_end) if TaskModel.due_date else False,
                TaskModel.created_at.between(today_start, today_end)
            )
        )
    ).all()

    completed_data = [{"title": t.title, "category": t.category} for t in completed]
    planned_data = [{"title": t.title, "status": t.status} for t in planned]

    # Generate AI review
    ai_review = generate_evening_review_ai(
        completed_tasks=completed_data,
        planned_tasks=planned_data,
        wins=review.wins,
        blockers=review.blockers,
        learnings=review.learnings,
        energy_level=review.energy_level
    )

    completion_stats = {
        "completed": len(completed),
        "planned": len(planned),
        "completion_rate": (len(completed) / len(planned)) if planned else 0
    }

    return EveningReviewResponse(
        date=datetime.now(),
        day_analysis=ai_review["day_analysis"],
        wins_recognition=ai_review["wins_recognition"],
        improvement_suggestions=ai_review["improvement_suggestions"],
        tomorrow_prep=ai_review["tomorrow_prep"],
        completion_stats=completion_stats
    )


@router.post("/research", response_model=ResearchBriefingResponse)
async def post_research_briefing(
    request: ResearchBriefingRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI research briefing on a topic

    Provides insights on a business topic and connects it to:
    - Relevant active goals
    - Relevant tasks
    - Action items

    Args:
        request: Research topic and focus areas

    Returns:
        Research insights with actionable next steps
    """
    from anthropic import Anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured (ANTHROPIC_API_KEY missing)"
        )

    # Get user's goals and tasks for context
    active_goals = get_active_goals(db, current_user.user_id)
    recent_tasks = get_todays_tasks(db, current_user.user_id)

    # Build context
    goals_context = "\n".join([
        f"- {g['title']} ({g['horizon']})"
        for g in active_goals
    ]) or "No active goals"

    focus_str = ", ".join(request.focus_areas) if request.focus_areas else "general overview"

    prompt = f"""Research the following business topic and provide actionable insights.

TOPIC: {request.topic}
FOCUS AREAS: {focus_str}

USER'S CURRENT GOALS:
{goals_context}

Provide {request.max_insights} key insights about this topic that are:
1. Specific and actionable
2. Relevant to a business context
3. Connected to the user's goals where applicable

Create a JSON response:
{{
    "key_insights": [
        "Insight 1 with specific details",
        "Insight 2 with specific details"
    ],
    "action_items": [
        "Specific action 1",
        "Specific action 2"
    ]
}}

Be concise but informative. Focus on practical application."""

    try:
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        response_text = response.content[0].text

        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        ai_response = json.loads(response_text)

        # Find relevant goals and tasks
        topic_lower = request.topic.lower()
        relevant_goals = [
            g for g in active_goals
            if any(word in g['title'].lower() for word in topic_lower.split())
        ]

        relevant_tasks = [
            t for t in recent_tasks
            if any(word in t['title'].lower() for word in topic_lower.split())
        ]

        return ResearchBriefingResponse(
            topic=request.topic,
            key_insights=ai_response["key_insights"][:request.max_insights],
            action_items=ai_response["action_items"],
            relevant_goals=relevant_goals,
            relevant_tasks=relevant_tasks
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )
