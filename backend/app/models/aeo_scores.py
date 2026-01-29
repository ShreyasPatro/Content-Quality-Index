"""AEO Score Persistence Model (Target Stage 6).

This module defines the storage schema for Answer Engine Optimization (AEO) scores.
It is strictly INSERT-ONLY and locked to a specific rubric version.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Numeric,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.models.base import metadata

aeo_scores = Table(
    "aeo_scores",
    metadata,
    Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()")),
    Column("run_id", UUID, ForeignKey("evaluation_runs.id"), nullable=False),
    Column("rubric_version", Text, nullable=False),
    
    # Top-Level Aggregate
    Column("aeo_total", Numeric(5, 2), nullable=False),
    
    # Pillar Scores (Explicit Columns for Analytics)
    Column("aeo_answerability", Numeric(5, 2), nullable=False),
    Column("aeo_structure", Numeric(5, 2), nullable=False),
    Column("aeo_specificity", Numeric(5, 2), nullable=False),
    Column("aeo_trust", Numeric(5, 2), nullable=False),
    Column("aeo_coverage", Numeric(5, 2), nullable=False),
    Column("aeo_freshness", Numeric(5, 2), nullable=False),
    Column("aeo_readability", Numeric(5, 2), nullable=False),
    
    # Detailed Evidence
    Column("details", JSONB, nullable=False),
    
    # Constraints
    CheckConstraint("aeo_total >= 0 AND aeo_total <= 100", name="chk_aeo_total"),
    UniqueConstraint("run_id", name="uq_aeo_run_id"),
)

Index("idx_aeo_scores_run_id", aeo_scores.c.run_id)
