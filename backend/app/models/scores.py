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
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.models.base import metadata

ai_detector_scores = Table(
    "ai_detector_scores",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column("run_id", UUID, ForeignKey("evaluation_runs.id"), nullable=False),
    Column("provider", String(50), nullable=False),
    Column("score", Numeric(5, 2), nullable=False),
    Column("details", JSONB, nullable=True),
    CheckConstraint(
        "score >= 0 AND score <= 100",
        name="chk_ai_detector_scores_score",
    ),
    UniqueConstraint("run_id", "provider", name="uq_detector_score"),
)

Index("idx_detector_scores_run", ai_detector_scores.c.run_id)

aeo_scores = Table(
    "aeo_scores",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column("run_id", UUID, ForeignKey("evaluation_runs.id"), nullable=False),
    Column("query_intent", Text, nullable=False),
    Column("score", Numeric(5, 2), nullable=False),
    Column("rationale", Text, nullable=True),
    CheckConstraint(
        "score >= 0 AND score <= 100",
        name="chk_aeo_scores_score",
    ),
    UniqueConstraint("run_id", "query_intent", name="uq_aeo_score"),
)

Index("idx_aeo_scores_run", aeo_scores.c.run_id)
