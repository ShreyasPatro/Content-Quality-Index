"""Score table definitions (AI detector and AEO)."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
import sqlalchemy
import uuid

from app.models.base import metadata

ai_detector_scores = Table(
    "ai_detector_scores",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("run_id", String(36), ForeignKey("evaluation_runs.id"), nullable=False),
    Column("provider", String(50), nullable=False),
    Column("score", Numeric(5, 2), nullable=False),
    Column("details", sqlalchemy.JSON, nullable=True),
    CheckConstraint(
        "score >= 0 AND score <= 100",
        name="chk_ai_detector_scores_score",
    ),
    UniqueConstraint("run_id", "provider", name="uq_detector_score"),
)

Index("idx_detector_scores_run", ai_detector_scores.c.run_id)

ai_likeness_rubric_scores = Table(
    "ai_likeness_rubric_scores",
    metadata,
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("run_id", String(36), ForeignKey("evaluation_runs.id"), nullable=False),
    Column("score", Numeric(5, 2), nullable=False),
    Column("details", sqlalchemy.JSON, nullable=False),
    Column(
        "created_at",
        String,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    ),
    CheckConstraint(
        "score >= 0 AND score <= 100",
        name="chk_rubric_scores_score",
    ),
    UniqueConstraint("run_id", name="uq_rubric_score_run_id"),
)

Index("idx_rubric_scores_run", ai_likeness_rubric_scores.c.run_id)
