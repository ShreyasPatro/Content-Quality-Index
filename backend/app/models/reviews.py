"""Human review action table definitions."""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, String, Table, Text, text
import uuid

from app.models.base import metadata

human_review_actions = Table(
    "human_review_actions",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column(
        "blog_version_id",
        String(36),
        ForeignKey("blog_versions.id"),
        nullable=False,
    ),
    Column("reviewer_id", String(36), ForeignKey("users.id"), nullable=False),
    Column("action", String(50), nullable=False),
    Column("comments", Text, nullable=True),
    Column("performed_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    CheckConstraint(
        "action IN ('APPROVE', 'REJECT', 'COMMENT', 'REQUEST_CHANGES', 'APPROVE_INTENT')",
        name="chk_human_review_actions_action",
    ),
)

Index("idx_review_actions_version", human_review_actions.c.blog_version_id)
Index("idx_review_actions_reviewer", human_review_actions.c.reviewer_id)
Index("idx_review_actions_performed_at", human_review_actions.c.performed_at)
