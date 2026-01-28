"""Human review action table definitions."""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, String, Table, Text, text
from sqlalchemy.dialects.postgresql import TIMESTAMPTZ, UUID

from app.models.base import metadata

human_review_actions = Table(
    "human_review_actions",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column(
        "blog_version_id",
        UUID,
        ForeignKey("blog_versions.id"),
        nullable=False,
    ),
    Column("reviewer_id", UUID, ForeignKey("users.id"), nullable=False),
    Column("action", String(50), nullable=False),
    Column("comments", Text, nullable=True),
    Column("performed_at", TIMESTAMPTZ, nullable=False, server_default=text("NOW()")),
    CheckConstraint(
        "action IN ('APPROVE', 'REJECT', 'COMMENT', 'REQUEST_CHANGES', 'APPROVE_INTENT')",
        name="chk_human_review_actions_action",
    ),
)

Index("idx_review_actions_version", human_review_actions.c.blog_version_id)
Index("idx_review_actions_reviewer", human_review_actions.c.reviewer_id)
Index("idx_review_actions_performed_at", human_review_actions.c.performed_at)
