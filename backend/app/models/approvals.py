"""Approval state and attempt table definitions."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    String,
    Table,
    Text,
    text,
)
import uuid

from app.models.base import metadata

approval_states = Table(
    "approval_states",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("blog_id", String(36), ForeignKey("blogs.id"), nullable=False),
    Column(
        "approved_version_id",
        String(36),
        ForeignKey("blog_versions.id"),
        nullable=False,
    ),
    Column("approver_id", String(36), ForeignKey("users.id"), nullable=False),
    Column("approved_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("revoked_at", String, nullable=True),
    Column("revoked_by", String(36), ForeignKey("users.id"), nullable=True),
    Column("revocation_reason", Text, nullable=True),
    Column("notes", Text, nullable=True),
)

Index("idx_approval_states_blog", approval_states.c.blog_id)
Index(
    "idx_approval_states_active",
    approval_states.c.blog_id,
    approval_states.c.approved_at,
    sqlite_where=approval_states.c.revoked_at.is_(None),
)

approval_attempts = Table(
    "approval_attempts",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("blog_id", String(36), ForeignKey("blogs.id"), nullable=False),
    Column("attempted_by", String(36), ForeignKey("users.id"), nullable=False),
    Column("is_human", Boolean, nullable=False),
    Column("result", String(20), nullable=False),
    Column("attempted_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("failure_reason", Text, nullable=True),
    CheckConstraint(
        "result IN ('success', 'forbidden', 'invalid_state', 'invalid_version')",
        name="chk_approval_attempts_result",
    ),
)

Index("idx_approval_attempts_blog", approval_attempts.c.blog_id)
Index("idx_approval_attempts_user", approval_attempts.c.attempted_by)
Index(
    "idx_approval_attempts_result",
    approval_attempts.c.result,
    sqlite_where=approval_attempts.c.result != "success",
)
