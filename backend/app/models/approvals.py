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
from sqlalchemy.dialects.postgresql import TIMESTAMPTZ, UUID

from app.models.base import metadata

approval_states = Table(
    "approval_states",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column("blog_id", UUID, ForeignKey("blogs.id"), nullable=False),
    Column(
        "approved_version_id",
        UUID,
        ForeignKey("blog_versions.id"),
        nullable=False,
    ),
    Column("approver_id", UUID, ForeignKey("users.id"), nullable=False),
    Column("approved_at", TIMESTAMPTZ, nullable=False, server_default=text("NOW()")),
    Column("revoked_at", TIMESTAMPTZ, nullable=True),
    Column("revoked_by", UUID, ForeignKey("users.id"), nullable=True),
    Column("revocation_reason", Text, nullable=True),
    Column("notes", Text, nullable=True),
    # Ensure approver is human (subquery check)
    CheckConstraint(
        "approver_id IN (SELECT id FROM users WHERE is_human = true)",
        name="chk_approver_is_human",
    ),
)

Index("idx_approval_states_blog", approval_states.c.blog_id)
Index(
    "idx_approval_states_active",
    approval_states.c.blog_id,
    approval_states.c.approved_at,
    postgresql_where=approval_states.c.revoked_at.is_(None),
)

approval_attempts = Table(
    "approval_attempts",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column("blog_id", UUID, ForeignKey("blogs.id"), nullable=False),
    Column("attempted_by", UUID, ForeignKey("users.id"), nullable=False),
    Column("is_human", Boolean, nullable=False),
    Column("result", String(20), nullable=False),
    Column("attempted_at", TIMESTAMPTZ, nullable=False, server_default=text("NOW()")),
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
    postgresql_where=approval_attempts.c.result != "success",
)
