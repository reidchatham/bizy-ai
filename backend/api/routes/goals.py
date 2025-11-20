"""
Goal CRUD API Routes

RESTful API endpoints for goal management with user authentication.
All endpoints require JWT authentication and filter by user_id.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from api.auth import get_current_user, TokenData
from api.dependencies import get_db
from models import Goal as GoalModel, Task as TaskModel


router = APIRouter()


# Request/Response Models

class GoalBase(BaseModel):
    """Base goal fields"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    horizon: str = Field(..., pattern="^(yearly|quarterly|monthly|weekly)$")
    target_date: Optional[datetime] = None
    status: str = Field(default="active", pattern="^(active|completed|on_hold|cancelled)$")
    success_criteria: Optional[str] = None
    parent_goal_id: Optional[int] = None
    metrics: Optional[dict] = None


class GoalCreate(GoalBase):
    """Goal creation request"""
    pass


class GoalUpdate(BaseModel):
    """Goal update request (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    horizon: Optional[str] = Field(None, pattern="^(yearly|quarterly|monthly|weekly)$")
    target_date: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|on_hold|cancelled)$")
    success_criteria: Optional[str] = None
    parent_goal_id: Optional[int] = None
    metrics: Optional[dict] = None


class GoalResponse(GoalBase):
    """Goal response with metadata"""
    id: int
    user_id: int
    progress_percentage: float
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    task_count: Optional[int] = None
    subgoal_count: Optional[int] = None

    class Config:
        from_attributes = True


class GoalBreakdownRequest(BaseModel):
    """Request for AI to breakdown a goal into tasks"""
    max_tasks: int = Field(default=10, ge=1, le=50)
    include_description: bool = Field(default=True)


class TaskSuggestion(BaseModel):
    """AI-suggested task"""
    title: str
    description: Optional[str] = None
    priority: int = Field(ge=1, le=5)
    estimated_hours: Optional[float] = None
    category: Optional[str] = None


class GoalBreakdownResponse(BaseModel):
    """Response from AI goal breakdown"""
    goal_id: int
    goal_title: str
    suggested_tasks: List[TaskSuggestion]
    reasoning: str


# Routes

@router.get("/", response_model=List[GoalResponse])
async def list_goals(
    status: Optional[str] = Query(None, pattern="^(active|completed|on_hold|cancelled)$"),
    horizon: Optional[str] = Query(None, pattern="^(yearly|quarterly|monthly|weekly)$"),
    parent_goal_id: Optional[int] = None,
    search: Optional[str] = Query(None, max_length=200),
    include_counts: bool = Query(False),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's goals with optional filters

    Filters:
    - status: Filter by goal status (active, completed, on_hold, cancelled)
    - horizon: Filter by time horizon (yearly, quarterly, monthly, weekly)
    - parent_goal_id: Filter by parent goal (None for top-level goals)
    - search: Search in title and description
    - include_counts: Include task/subgoal counts (slower)
    - limit: Max results to return (default 100)
    - offset: Pagination offset (default 0)

    Returns:
        List of goals for the authenticated user
    """
    # Base query - only user's goals
    query = db.query(GoalModel).filter(GoalModel.user_id == current_user.user_id)

    # Apply filters
    if status:
        query = query.filter(GoalModel.status == status)

    if horizon:
        query = query.filter(GoalModel.horizon == horizon)

    if parent_goal_id is not None:
        query = query.filter(GoalModel.parent_goal_id == parent_goal_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                GoalModel.title.ilike(search_term),
                GoalModel.description.ilike(search_term)
            )
        )

    # Order by: target_date (earliest first), then created_at
    query = query.order_by(
        GoalModel.target_date.asc().nullslast(),
        GoalModel.created_at.desc()
    )

    # Pagination
    goals = query.offset(offset).limit(limit).all()

    # Add counts if requested
    if include_counts:
        for goal in goals:
            goal.task_count = db.query(func.count(TaskModel.id)).filter(
                TaskModel.parent_goal_id == goal.id
            ).scalar()
            goal.subgoal_count = db.query(func.count(GoalModel.id)).filter(
                GoalModel.parent_goal_id == goal.id
            ).scalar()

    return goals


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal: GoalCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new goal

    Args:
        goal: Goal details

    Returns:
        Created goal object

    Raises:
        400: Invalid parent_goal_id (if goal doesn't exist or doesn't belong to user)
    """
    # Validate parent goal if provided
    if goal.parent_goal_id is not None:
        parent_goal = db.query(GoalModel).filter(
            and_(
                GoalModel.id == goal.parent_goal_id,
                GoalModel.user_id == current_user.user_id
            )
        ).first()

        if not parent_goal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent goal {goal.parent_goal_id} not found or doesn't belong to you"
            )

    # Create goal
    db_goal = GoalModel(
        user_id=current_user.user_id,
        progress_percentage=0.0,
        **goal.model_dump()
    )

    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)

    return db_goal


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: int,
    include_counts: bool = Query(False),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific goal by ID

    Args:
        goal_id: Goal ID
        include_counts: Include task/subgoal counts

    Returns:
        Goal object

    Raises:
        404: Goal not found or doesn't belong to user
    """
    goal = db.query(GoalModel).filter(
        and_(
            GoalModel.id == goal_id,
            GoalModel.user_id == current_user.user_id
        )
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal {goal_id} not found"
        )

    # Add counts if requested
    if include_counts:
        goal.task_count = db.query(func.count(TaskModel.id)).filter(
            TaskModel.parent_goal_id == goal.id
        ).scalar()
        goal.subgoal_count = db.query(func.count(GoalModel.id)).filter(
            GoalModel.parent_goal_id == goal.id
        ).scalar()

    return goal


@router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a goal

    Only provided fields will be updated (partial update).

    Args:
        goal_id: Goal ID
        goal_update: Fields to update

    Returns:
        Updated goal object

    Raises:
        404: Goal not found or doesn't belong to user
        400: Invalid parent_goal_id or circular reference
    """
    # Get goal
    goal = db.query(GoalModel).filter(
        and_(
            GoalModel.id == goal_id,
            GoalModel.user_id == current_user.user_id
        )
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal {goal_id} not found"
        )

    # Validate parent goal if being changed
    update_data = goal_update.model_dump(exclude_unset=True)

    if "parent_goal_id" in update_data and update_data["parent_goal_id"] is not None:
        # Prevent circular references
        if update_data["parent_goal_id"] == goal_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A goal cannot be its own parent"
            )

        parent_goal = db.query(GoalModel).filter(
            and_(
                GoalModel.id == update_data["parent_goal_id"],
                GoalModel.user_id == current_user.user_id
            )
        ).first()

        if not parent_goal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent goal {update_data['parent_goal_id']} not found or doesn't belong to you"
            )

        # Check if parent_goal is a descendant of current goal (would create cycle)
        def is_descendant(parent_id: int, descendant_id: int) -> bool:
            """Check if descendant_id is a descendant of parent_id"""
            current = db.query(GoalModel).filter(GoalModel.id == parent_id).first()
            while current and current.parent_goal_id:
                if current.parent_goal_id == descendant_id:
                    return True
                current = db.query(GoalModel).filter(GoalModel.id == current.parent_goal_id).first()
            return False

        if is_descendant(update_data["parent_goal_id"], goal_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create circular reference: parent goal is a descendant of this goal"
            )

    # Update fields
    for field, value in update_data.items():
        setattr(goal, field, value)

    # Update timestamp
    goal.updated_at = datetime.utcnow()

    # If status changed to completed, set completed_at
    if "status" in update_data and update_data["status"] == "completed" and not goal.completed_at:
        goal.completed_at = datetime.utcnow()
        goal.progress_percentage = 100.0

    db.commit()
    db.refresh(goal)

    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a goal

    This will also update all tasks and subgoals to remove their parent_goal_id reference.

    Args:
        goal_id: Goal ID

    Raises:
        404: Goal not found or doesn't belong to user
    """
    goal = db.query(GoalModel).filter(
        and_(
            GoalModel.id == goal_id,
            GoalModel.user_id == current_user.user_id
        )
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal {goal_id} not found"
        )

    db.delete(goal)
    db.commit()

    return None


@router.post("/{goal_id}/calculate-progress", response_model=GoalResponse)
async def calculate_goal_progress(
    goal_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate and update goal progress based on completed tasks and subgoals

    Progress is calculated as:
    - 50% weight from direct tasks completion rate
    - 50% weight from subgoals average progress

    Args:
        goal_id: Goal ID

    Returns:
        Updated goal object with new progress_percentage

    Raises:
        404: Goal not found or doesn't belong to user
    """
    goal = db.query(GoalModel).filter(
        and_(
            GoalModel.id == goal_id,
            GoalModel.user_id == current_user.user_id
        )
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal {goal_id} not found"
        )

    # Calculate task completion rate
    total_tasks = db.query(func.count(TaskModel.id)).filter(
        TaskModel.parent_goal_id == goal_id
    ).scalar()

    completed_tasks = db.query(func.count(TaskModel.id)).filter(
        and_(
            TaskModel.parent_goal_id == goal_id,
            TaskModel.status == "completed"
        )
    ).scalar()

    task_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Calculate average subgoal progress
    subgoals = db.query(GoalModel).filter(
        GoalModel.parent_goal_id == goal_id
    ).all()

    subgoal_progress = 0
    if subgoals:
        subgoal_progress = sum(sg.progress_percentage for sg in subgoals) / len(subgoals)

    # Weighted average (50% tasks, 50% subgoals)
    if total_tasks > 0 and subgoals:
        progress = (task_progress * 0.5) + (subgoal_progress * 0.5)
    elif total_tasks > 0:
        progress = task_progress
    elif subgoals:
        progress = subgoal_progress
    else:
        progress = 0

    # Update progress
    goal.progress_percentage = round(progress, 2)
    goal.updated_at = datetime.utcnow()

    # Auto-complete if 100%
    if goal.progress_percentage >= 100.0 and goal.status == "active":
        goal.status = "completed"
        goal.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(goal)

    return goal


@router.post("/{goal_id}/breakdown", response_model=GoalBreakdownResponse)
async def breakdown_goal(
    goal_id: int,
    request: GoalBreakdownRequest = GoalBreakdownRequest(),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Use AI to breakdown a goal into suggested tasks

    This endpoint uses Claude AI to analyze the goal and suggest actionable tasks.

    Args:
        goal_id: Goal ID
        request: Breakdown parameters (max_tasks, include_description)

    Returns:
        AI-suggested tasks for the goal

    Raises:
        404: Goal not found or doesn't belong to user
        500: AI service error
        503: ANTHROPIC_API_KEY not configured
    """
    import os
    from anthropic import Anthropic

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured (ANTHROPIC_API_KEY missing)"
        )

    # Get goal
    goal = db.query(GoalModel).filter(
        and_(
            GoalModel.id == goal_id,
            GoalModel.user_id == current_user.user_id
        )
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal {goal_id} not found"
        )

    # Build AI prompt
    prompt = f"""You are a business planning assistant. Break down the following goal into {request.max_tasks} concrete, actionable tasks.

Goal: {goal.title}
Horizon: {goal.horizon}
Description: {goal.description or 'No description provided'}
Success Criteria: {goal.success_criteria or 'Not specified'}

For each task, provide:
1. A clear, specific title (action-oriented)
2. {'A brief description (1-2 sentences)' if request.include_description else 'No description needed'}
3. Priority (1=highest, 5=lowest) based on dependencies and importance
4. Estimated hours if applicable
5. Category/type of work

Respond in JSON format:
{{
    "tasks": [
        {{
            "title": "Task title",
            "description": "Task description",
            "priority": 1-5,
            "estimated_hours": float or null,
            "category": "category name"
        }}
    ],
    "reasoning": "Brief explanation of the breakdown strategy"
}}"""

    try:
        # Call Claude API
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response
        import json
        response_text = response.content[0].text

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        ai_response = json.loads(response_text)

        # Convert to response format
        suggested_tasks = [
            TaskSuggestion(
                title=task["title"],
                description=task.get("description"),
                priority=task["priority"],
                estimated_hours=task.get("estimated_hours"),
                category=task.get("category")
            )
            for task in ai_response["tasks"][:request.max_tasks]
        ]

        return GoalBreakdownResponse(
            goal_id=goal_id,
            goal_title=goal.title,
            suggested_tasks=suggested_tasks,
            reasoning=ai_response.get("reasoning", "AI breakdown completed")
        )

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse AI response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}"
        )


@router.post("/{goal_id}/breakdown/create-tasks", response_model=List[dict])
async def create_tasks_from_breakdown(
    goal_id: int,
    tasks: List[TaskSuggestion],
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create actual tasks from AI suggestions

    Args:
        goal_id: Goal ID to attach tasks to
        tasks: List of task suggestions from breakdown

    Returns:
        List of created task IDs

    Raises:
        404: Goal not found or doesn't belong to user
    """
    # Verify goal exists and belongs to user
    goal = db.query(GoalModel).filter(
        and_(
            GoalModel.id == goal_id,
            GoalModel.user_id == current_user.user_id
        )
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal {goal_id} not found"
        )

    # Create tasks
    created_tasks = []
    for task_suggestion in tasks:
        db_task = TaskModel(
            user_id=current_user.user_id,
            parent_goal_id=goal_id,
            title=task_suggestion.title,
            description=task_suggestion.description,
            priority=task_suggestion.priority,
            estimated_hours=task_suggestion.estimated_hours,
            category=task_suggestion.category,
            status="pending"
        )
        db.add(db_task)
        db.flush()  # Get ID without committing
        created_tasks.append({"id": db_task.id, "title": db_task.title})

    db.commit()

    return created_tasks


@router.get("/stats/summary")
async def get_goal_stats(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get goal statistics for the current user

    Returns:
        Goal counts by status, horizon, and average progress
    """
    # Total counts
    total = db.query(func.count(GoalModel.id)).filter(
        GoalModel.user_id == current_user.user_id
    ).scalar()

    # By status
    by_status = db.query(
        GoalModel.status,
        func.count(GoalModel.id)
    ).filter(
        GoalModel.user_id == current_user.user_id
    ).group_by(GoalModel.status).all()

    # By horizon
    by_horizon = db.query(
        GoalModel.horizon,
        func.count(GoalModel.id)
    ).filter(
        GoalModel.user_id == current_user.user_id
    ).group_by(GoalModel.horizon).all()

    # Average progress
    avg_progress = db.query(func.avg(GoalModel.progress_percentage)).filter(
        and_(
            GoalModel.user_id == current_user.user_id,
            GoalModel.status == "active"
        )
    ).scalar() or 0

    # Goals near completion (>= 80% progress)
    near_completion = db.query(func.count(GoalModel.id)).filter(
        and_(
            GoalModel.user_id == current_user.user_id,
            GoalModel.progress_percentage >= 80,
            GoalModel.status == "active"
        )
    ).scalar()

    return {
        "total": total,
        "by_status": {status: count for status, count in by_status},
        "by_horizon": {horizon: count for horizon, count in by_horizon},
        "average_progress": round(avg_progress, 2),
        "near_completion": near_completion
    }
