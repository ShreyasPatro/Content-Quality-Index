"""Evaluation run table definitions."""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, String, Table, text
import sqlalchemy
import uuid

from app.models.base import metadata

evaluation_runs = Table(
    "evaluation_runs",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column(
        "blog_version_id",
        String(36),
        ForeignKey("blog_versions.id"),
        nullable=False,
    ),
    Column("run_at", String, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
    Column("triggered_by", String(36), ForeignKey("users.id"), nullable=True),
    Column("model_config", sqlalchemy.JSON, nullable=True),
    Column("completed_at", String, nullable=True),
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
    sqlite_where=evaluation_runs.c.completed_at.is_(None),
)
