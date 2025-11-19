"""
User model for authentication and multi-user support
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime)
    email_verified_at = Column(DateTime)

    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self, include_email=False):
        """Convert user to dictionary (excludes sensitive data by default)"""
        data = {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
        }

        # Only include email if explicitly requested (e.g., for own profile)
        if include_email:
            data['email'] = self.email
            data['email_verified_at'] = self.email_verified_at.isoformat() if self.email_verified_at else None

        return data

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
