"""Escalation table definitions."""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, String, Table, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMPTZ, UUID

from app.models.base import metadata

escalations = Table(
    "escalations",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column("blog_id", UUID, ForeignKey("blogs.id"), nullable=False),
    Column("version_id", UUID, ForeignKey("blog_versions.id"), nullable=False),
    Column("reason", String(50), nullable=False),
    Column("details", JSONB, nullable=True),
    Column(
        "status",
        String(20),
        nullable=False,
        server_default=text("'pending_review'"),
    ),
    Column("created_at", TIMESTAMPTZ, nullable=False, server_default=text("NOW()")),
    Column("resolved_at", TIMESTAMPTZ, nullable=True),
    Column("resolved_by", UUID, ForeignKey("users.id"), nullable=True),
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
    postgresql_where=escalations.c.status == "pending_review",
)
