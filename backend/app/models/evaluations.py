"""Evaluation run table definitions."""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, String, Table, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMPTZ, UUID

from app.models.base import metadata

evaluation_runs = Table(
    "evaluation_runs",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column(
        "blog_version_id",
        UUID,
        ForeignKey("blog_versions.id"),
        nullable=False,
    ),
    Column("run_at", TIMESTAMPTZ, nullable=False, server_default=text("NOW()")),
    Column("triggered_by", UUID, ForeignKey("users.id"), nullable=True),
    Column("model_config", JSONB, nullable=True),
    Column("completed_at", TIMESTAMPTZ, nullable=True),
    Column(
        "status",
        String(20),
        nullable=False,
        server_default=text("'processing'"),
    ),
    CheckConstraint(
        "status IN ('processing', 'completed', 'partial_failure', 'failed')",
        name="chk_evaluation_runs_status",
    ),
)

Index("idx_eval_runs_version", evaluation_runs.c.blog_version_id)
Index(
    "idx_eval_runs_status",
    evaluation_runs.c.status,
    postgresql_where=evaluation_runs.c.completed_at.is_(None),
)
