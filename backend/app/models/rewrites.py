"""Rewrite cycle and suggestion table definitions."""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, String, Table, text
import sqlalchemy
import uuid

from app.models.base import metadata

rewrite_cycles = Table(
    "rewrite_cycles",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column(
        "source_version_id",
        String(36),
        ForeignKey("blog_versions.id"),
        nullable=False,
    ),
    Column("target_version_id", String(36), ForeignKey("blog_versions.id"), nullable=True),
    Column("prompt_template_id", String(36), nullable=True),
    Column("llm_model", String(100), nullable=False),
    Column("started_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("completed_at", String, nullable=True),
)

Index("idx_rewrite_cycles_source", rewrite_cycles.c.source_version_id)
Index("idx_rewrite_cycles_target", rewrite_cycles.c.target_version_id)

rewrite_suggestions = Table(
    "rewrite_suggestions",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("cycle_id", String(36), ForeignKey("rewrite_cycles.id"), nullable=False),
    Column("suggested_content", sqlalchemy.JSON, nullable=False),
    Column(
        "status",
        String(30),
        nullable=False,
        server_default=text("'pending_user_acceptance'"),
    ),
    Column("created_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    CheckConstraint(
        "status IN ('pending_user_acceptance', 'accepted', 'rejected')",
        name="chk_rewrite_suggestions_status",
    ),
)

Index("idx_rewrite_suggestions_cycle", rewrite_suggestions.c.cycle_id)
