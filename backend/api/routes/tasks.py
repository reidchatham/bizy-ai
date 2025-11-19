"""
Task CRUD API Routes

RESTful API endpoints for task management with user authentication.
All endpoints require JWT authentication and filter by user_id.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from api.auth import get_current_user, TokenData
from api.dependencies import get_db
from models import Task as TaskModel


router = APIRouter()


# Request/Response Models

class TaskBase(BaseModel):
    """Base task fields"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    priority: int = Field(default=3, ge=1, le=5)  # 1=highest, 5=lowest
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed|blocked)$")
    category: Optional[str] = Field(None, max_length=100)
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    due_date: Optional[datetime] = None
    parent_goal_id: Optional[int] = None
    dependencies: Optional[List[int]] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class TaskCreate(TaskBase):
    """Task creation request"""
    pass


class TaskUpdate(BaseModel):
    """Task update request (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|blocked)$")
    category: Optional[str] = Field(None, max_length=100)
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    due_date: Optional[datetime] = None
    parent_goal_id: Optional[int] = None
    dependencies: Optional[List[int]] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class TaskResponse(TaskBase):
    """Task response with metadata"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskCompleteRequest(BaseModel):
    """Request to mark task as complete"""
    actual_hours: Optional[float] = Field(None, ge=0)


# Routes

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = Query(None, pattern="^(pending|in_progress|completed|blocked)$"),
    category: Optional[str] = Query(None, max_length=100),
    priority: Optional[int] = Query(None, ge=1, le=5),
    goal_id: Optional[int] = None,
    search: Optional[str] = Query(None, max_length=200),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's tasks with optional filters

    Filters:
    - status: Filter by task status (pending, in_progress, completed, blocked)
    - category: Filter by category
    - priority: Filter by priority level (1-5)
    - goal_id: Filter by parent goal
    - search: Search in title and description
    - limit: Max results to return (default 100)
    - offset: Pagination offset (default 0)

    Returns:
        List of tasks for the authenticated user
    """
    # Base query - only user's tasks
    query = db.query(TaskModel).filter(TaskModel.user_id == current_user.user_id)

    # Apply filters
    if status:
        query = query.filter(TaskModel.status == status)

    if category:
        query = query.filter(TaskModel.category == category)

    if priority:
        query = query.filter(TaskModel.priority == priority)

    if goal_id is not None:
        query = query.filter(TaskModel.parent_goal_id == goal_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                TaskModel.title.ilike(search_term),
                TaskModel.description.ilike(search_term)
            )
        )

    # Order by: priority (high to low), then due_date (earliest first), then created_at
    query = query.order_by(
        TaskModel.priority.asc(),
        TaskModel.due_date.asc().nullslast(),
        TaskModel.created_at.desc()
    )

    # Pagination
    tasks = query.offset(offset).limit(limit).all()

    return tasks


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task

    Args:
        task: Task details

    Returns:
        Created task object

    Raises:
        400: Invalid goal_id (if goal doesn't exist or doesn't belong to user)
    """
    # Validate parent goal if provided
    if task.parent_goal_id is not None:
        from models import Goal as GoalModel
        goal = db.query(GoalModel).filter(
            and_(
                GoalModel.id == task.parent_goal_id,
                GoalModel.user_id == current_user.user_id
            )
        ).first()

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Goal {task.parent_goal_id} not found or doesn't belong to you"
            )

    # Create task
    db_task = TaskModel(
        user_id=current_user.user_id,
        **task.model_dump()
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific task by ID

    Args:
        task_id: Task ID

    Returns:
        Task object

    Raises:
        404: Task not found or doesn't belong to user
    """
    task = db.query(TaskModel).filter(
        and_(
            TaskModel.id == task_id,
            TaskModel.user_id == current_user.user_id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a task

    Only provided fields will be updated (partial update).

    Args:
        task_id: Task ID
        task_update: Fields to update

    Returns:
        Updated task object

    Raises:
        404: Task not found or doesn't belong to user
        400: Invalid goal_id
    """
    # Get task
    task = db.query(TaskModel).filter(
        and_(
            TaskModel.id == task_id,
            TaskModel.user_id == current_user.user_id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # Validate parent goal if being changed
    update_data = task_update.model_dump(exclude_unset=True)

    if "parent_goal_id" in update_data and update_data["parent_goal_id"] is not None:
        from models import Goal as GoalModel
        goal = db.query(GoalModel).filter(
            and_(
                GoalModel.id == update_data["parent_goal_id"],
                GoalModel.user_id == current_user.user_id
            )
        ).first()

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Goal {update_data['parent_goal_id']} not found or doesn't belong to you"
            )

    # Update fields
    for field, value in update_data.items():
        setattr(task, field, value)

    # Update timestamp
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a task

    Args:
        task_id: Task ID

    Raises:
        404: Task not found or doesn't belong to user
    """
    task = db.query(TaskModel).filter(
        and_(
            TaskModel.id == task_id,
            TaskModel.user_id == current_user.user_id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    db.delete(task)
    db.commit()

    return None


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    complete_request: TaskCompleteRequest = None,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a task as completed

    Args:
        task_id: Task ID
        complete_request: Optional actual hours spent

    Returns:
        Updated task object

    Raises:
        404: Task not found or doesn't belong to user
        400: Task already completed
    """
    task = db.query(TaskModel).filter(
        and_(
            TaskModel.id == task_id,
            TaskModel.user_id == current_user.user_id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    if task.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} is already completed"
        )

    # Mark as completed
    task.status = "completed"
    task.completed_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()

    # Set actual hours if provided
    if complete_request and complete_request.actual_hours is not None:
        task.actual_hours = complete_request.actual_hours

    db.commit()
    db.refresh(task)

    return task


@router.post("/{task_id}/uncomplete", response_model=TaskResponse)
async def uncomplete_task(
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a completed task as pending (undo completion)

    Args:
        task_id: Task ID

    Returns:
        Updated task object

    Raises:
        404: Task not found or doesn't belong to user
        400: Task is not completed
    """
    task = db.query(TaskModel).filter(
        and_(
            TaskModel.id == task_id,
            TaskModel.user_id == current_user.user_id
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    if task.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task {task_id} is not completed"
        )

    # Revert to pending
    task.status = "pending"
    task.completed_at = None
    task.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


@router.get("/stats/summary")
async def get_task_stats(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get task statistics for the current user

    Returns:
        Task counts by status, priority, category
    """
    from sqlalchemy import func

    # Total counts
    total = db.query(func.count(TaskModel.id)).filter(
        TaskModel.user_id == current_user.user_id
    ).scalar()

    # By status
    by_status = db.query(
        TaskModel.status,
        func.count(TaskModel.id)
    ).filter(
        TaskModel.user_id == current_user.user_id
    ).group_by(TaskModel.status).all()

    # By priority
    by_priority = db.query(
        TaskModel.priority,
        func.count(TaskModel.id)
    ).filter(
        TaskModel.user_id == current_user.user_id
    ).group_by(TaskModel.priority).all()

    # By category
    by_category = db.query(
        TaskModel.category,
        func.count(TaskModel.id)
    ).filter(
        TaskModel.user_id == current_user.user_id,
        TaskModel.category.isnot(None)
    ).group_by(TaskModel.category).all()

    # Overdue tasks
    now = datetime.utcnow()
    overdue = db.query(func.count(TaskModel.id)).filter(
        and_(
            TaskModel.user_id == current_user.user_id,
            TaskModel.due_date < now,
            TaskModel.status != "completed"
        )
    ).scalar()

    return {
        "total": total,
        "by_status": {status: count for status, count in by_status},
        "by_priority": {priority: count for priority, count in by_priority},
        "by_category": {category: count for category, count in by_category},
        "overdue": overdue
    }
