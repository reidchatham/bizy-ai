"""
Goal model with user support
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Goal(Base):
    """Goal model for goal management"""
    __tablename__ = 'goals'

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    parent_goal_id = Column(Integer, ForeignKey('goals.id', ondelete='SET NULL'), index=True)

    # Core fields
    title = Column(String(500), nullable=False)
    description = Column(Text)
    horizon = Column(String(50), index=True)  # yearly, quarterly, monthly, weekly
    target_date = Column(DateTime, index=True)
    status = Column(String(50), default='active')  # active, completed, on_hold, cancelled
    progress_percentage = Column(Float, default=0.0)
    success_criteria = Column(Text)

    # Timestamps (UTC for consistency)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)

    # Additional metadata
    metrics = Column(JSON)  # Key metrics to track

    # Relationships
    user = relationship("User", back_populates="goals")
    tasks = relationship("Task", back_populates="goal", cascade="all, delete-orphan")

    # Self-referential relationship for goal hierarchy
    parent = relationship("Goal", remote_side=[id], back_populates="subgoals")
    subgoals = relationship("Goal", back_populates="parent", remote_side=[parent_goal_id])

    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_goals_user_status', 'user_id', 'status'),
        Index('ix_goals_user_horizon', 'user_id', 'horizon'),
        Index('ix_goals_user_target_date', 'user_id', 'target_date'),
    )

    def to_dict(self):
        """Convert goal to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'parent_goal_id': self.parent_goal_id,
            'title': self.title,
            'description': self.description,
            'horizon': self.horizon,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'success_criteria': self.success_criteria,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metrics': self.metrics or {}
        }

    def __repr__(self):
        return f"<Goal(id={self.id}, title='{self.title}', progress={self.progress_percentage}%)>"
