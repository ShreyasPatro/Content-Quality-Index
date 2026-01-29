"""SQLAlchemy Core table definitions.

This package contains all table definitions using SQLAlchemy Core.
Tables are organized by domain and use a central metadata registry.

Usage:
    from app.models import users, blogs, blog_versions
    from sqlalchemy import select

    # Query example
    stmt = select(users).where(users.c.email == "user@example.com")
"""

from app.models.ai_detection import (
    ai_detector_scores,
    evaluation_runs,
)
from app.models.aeo_scores import aeo_scores
from app.models.approvals import approval_attempts, approval_states
from app.models.base import metadata
from app.models.blogs import blog_versions, blogs
from app.models.escalations import escalations
from app.models.reviews import human_review_actions
from app.models.rewrites import rewrite_cycles, rewrite_suggestions
from app.models.users import users

__all__ = [
    # Metadata
    "metadata",
    # Users
    "users",
    # Blogs
    "blogs",
    "blog_versions",
    # AI Detection
    "evaluation_runs",
    "ai_detector_scores",
    "aeo_scores",
    # Rewrites
    "rewrite_cycles",
    "rewrite_suggestions",
    # Reviews
    "human_review_actions",
    # Approvals
    "approval_states",
    "approval_attempts",
    # Escalations
    "escalations",
]
