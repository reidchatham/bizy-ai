"""
Task model with user support
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Task(Base):
    """Task model for task management"""
    __tablename__ = 'tasks'

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    parent_goal_id = Column(Integer, ForeignKey('goals.id', ondelete='SET NULL'), index=True)

    # Core fields
    title = Column(String(500), nullable=False)
    description = Column(Text)
    priority = Column(Integer, default=3)  # 1=highest, 5=lowest
    status = Column(String(50), default='pending')  # pending, in_progress, completed, blocked
    category = Column(String(100), index=True)  # development, marketing, operations, etc.

    # Time tracking
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    due_date = Column(DateTime, index=True)

    # Timestamps (UTC for consistency)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)

    # Additional metadata
    dependencies = Column(JSON)  # List of task IDs this depends on
    notes = Column(Text)
    tags = Column(JSON)  # List of tags for filtering

    # Relationships
    user = relationship("User", back_populates="tasks")
    goal = relationship("Goal", back_populates="tasks")

    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_tasks_user_status', 'user_id', 'status'),
        Index('ix_tasks_user_due_date', 'user_id', 'due_date'),
        Index('ix_tasks_user_category', 'user_id', 'category'),
        Index('ix_tasks_goal_status', 'parent_goal_id', 'status'),
    )

    def to_dict(self):
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'parent_goal_id': self.parent_goal_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'category': self.category,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'dependencies': self.dependencies or [],
            'notes': self.notes,
            'tags': self.tags or []
        }

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"
