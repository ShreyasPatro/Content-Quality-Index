"""Escalation table definitions."""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, String, Table, text
import sqlalchemy
import uuid

from app.models.base import metadata

escalations = Table(
    "escalations",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("blog_id", String(36), ForeignKey("blogs.id"), nullable=False),
    Column("version_id", String(36), ForeignKey("blog_versions.id"), nullable=False),
    Column("reason", String(50), nullable=False),
    Column("details", sqlalchemy.JSON, nullable=True),
    Column(
        "status",
        String(20),
        nullable=False,
        server_default=text("'pending_review'"),
    ),
    Column("created_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("resolved_at", String, nullable=True),
    Column("resolved_by", String(36), ForeignKey("users.id"), nullable=True),
    CheckConstraint(
        "reason IN ('score_regression', 'policy_violation', 'ambiguity', 'low_quality')",
        name="chk_escalations_reason",
    ),
    CheckConstraint(
        "status IN ('pending_review', 'resolved', 'dismissed')",
        name="chk_escalations_status",
    ),
)

Index("idx_escalations_blog", escalations.c.blog_id)
Index("idx_escalations_status", escalations.c.status)
Index(
    "idx_escalations_pending",
    escalations.c.blog_id,
    sqlite_where=escalations.c.status == "pending_review",
)
