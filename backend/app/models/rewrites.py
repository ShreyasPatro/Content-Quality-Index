"""Rewrite cycle and suggestion table definitions."""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, String, Table, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMPTZ, UUID

from app.models.base import metadata

rewrite_cycles = Table(
    "rewrite_cycles",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column(
        "source_version_id",
        UUID,
        ForeignKey("blog_versions.id"),
        nullable=False,
    ),
    Column("target_version_id", UUID, ForeignKey("blog_versions.id"), nullable=True),
    Column("prompt_template_id", UUID, nullable=True),
    Column("llm_model", String(100), nullable=False),
    Column("started_at", TIMESTAMPTZ, nullable=False, server_default=text("NOW()")),
    Column("completed_at", TIMESTAMPTZ, nullable=True),
)

Index("idx_rewrite_cycles_source", rewrite_cycles.c.source_version_id)
Index("idx_rewrite_cycles_target", rewrite_cycles.c.target_version_id)

rewrite_suggestions = Table(
    "rewrite_suggestions",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column("cycle_id", UUID, ForeignKey("rewrite_cycles.id"), nullable=False),
    Column("suggested_content", JSONB, nullable=False),
    Column(
        "status",
        String(30),
        nullable=False,
        server_default=text("'pending_user_acceptance'"),
    ),
    Column("created_at", TIMESTAMPTZ, nullable=False, server_default=text("NOW()")),
    CheckConstraint(
        "status IN ('pending_user_acceptance', 'accepted', 'rejected')",
        name="chk_rewrite_suggestions_status",
    ),
)

Index("idx_rewrite_suggestions_cycle", rewrite_suggestions.c.cycle_id)
