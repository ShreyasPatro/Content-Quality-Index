"""AI detection table definitions.

This module provides SQLAlchemy Core table definitions for AI detection scoring.
These tables are INSERT-ONLY and store immutable evaluation results.

Tables:
- ai_detector_scores: Scores from third-party AI detectors (Originality.ai, GPTZero, etc.)
- aeo_scores: Answer Engine Optimization scores
- evaluation_runs: Reference to evaluation orchestration (defined in evaluations.py)

Note: These tables are already defined in app/models/scores.py and app/models/evaluations.py.
This module provides a consolidated import point for AI detection-related tables.
"""

from app.models.evaluations import evaluation_runs
from app.models.scores import ai_detector_scores
from app.models.aeo_scores import aeo_scores

__all__ = [
    "ai_detector_scores",
    "aeo_scores",
    "evaluation_runs",
]


# Table Documentation
# ===================

# ai_detector_scores
# ------------------
# Stores scores from third-party AI content detectors.
#
# Columns:
#   - id: UUID primary key
#   - run_id: Foreign key to evaluation_runs
#   - provider: Detector provider name (e.g., "originality_ai", "gptzero")
#   - score: AI likelihood score (0-100)
#   - details: JSONB containing:
#       * model_version: Detector model version (for drift tracking)
#       * raw_response: Full API response
#       * timestamp: Detection timestamp
#       * confidence: Confidence level (if provided)
#
# Constraints:
#   - UNIQUE(run_id, provider): One score per provider per evaluation
#   - CHECK(score >= 0 AND score <= 100): Valid score range
#
# Indexes:
#   - idx_detector_scores_run: Fast lookup by evaluation run
#
# Immutability:
#   - INSERT-ONLY table (enforced by database trigger)
#   - No UPDATE or DELETE operations allowed
#   - Detector drift tracked via details.model_version


# aeo_scores
# ----------
# Stores Answer Engine Optimization scores for query intents.
#
# Columns:
#   - id: UUID primary key
#   - run_id: Foreign key to evaluation_runs
#   - query_intent: Target query/question the content answers
#   - score: AEO quality score (0-100)
#   - rationale: LLM explanation of score
#
# Constraints:
#   - UNIQUE(run_id, query_intent): One score per query per evaluation
#   - CHECK(score >= 0 AND score <= 100): Valid score range
#
# Indexes:
#   - idx_aeo_scores_run: Fast lookup by evaluation run
#
# Immutability:
#   - INSERT-ONLY table (enforced by database trigger)
#   - No UPDATE or DELETE operations allowed


# evaluation_runs
# ---------------
# Orchestrates evaluation pipeline execution.
#
# Columns:
#   - id: UUID primary key
#   - blog_version_id: Foreign key to blog_versions
#   - run_at: Evaluation start timestamp
#   - triggered_by: User who triggered evaluation (optional)
#   - model_config: Snapshot of model/prompt config (JSONB)
#   - completed_at: Evaluation completion timestamp
#   - status: Workflow status (processing, completed, partial_failure, failed)
#
# Status Transitions:
#   - processing: Evaluation in progress
#   - completed: All detectors succeeded
#   - partial_failure: Some detectors failed
#   - failed: All detectors failed
#
# Partial Immutability:
#   - Core data (blog_version_id, run_at, model_config) is immutable
#   - Workflow metadata (status, completed_at) is updatable
#   - See immutability_policy.md for rationale


# Usage Examples
# ==============

# Query AI detector scores for an evaluation run:
# ------------------------------------------------
# from sqlalchemy import select
# from app.models.ai_detection import ai_detector_scores
#
# stmt = select(ai_detector_scores).where(
#     ai_detector_scores.c.run_id == run_id
# )
# result = await conn.execute(stmt)
# scores = result.fetchall()


# Insert AI detector score:
# -------------------------
# from app.models.ai_detection import ai_detector_scores
#
# await conn.execute(
#     ai_detector_scores.insert().values(
#         run_id=run_id,
#         provider="originality_ai",
#         score=85.5,
#         details={
#             "model_version": "3.0",
#             "raw_response": {...},
#             "timestamp": "2026-01-29T11:16:52Z",
#             "confidence": "high"
#         }
#     )
# )


# Query AEO scores for an evaluation run:
# ----------------------------------------
# from sqlalchemy import select
# from app.models.ai_detection import aeo_scores
#
# stmt = select(aeo_scores).where(
#     aeo_scores.c.run_id == run_id
# )
# result = await conn.execute(stmt)
# scores = result.fetchall()


# Check evaluation run status:
# ----------------------------
# from sqlalchemy import select
# from app.models.ai_detection import evaluation_runs
#
# stmt = select(evaluation_runs).where(
#     evaluation_runs.c.id == run_id
# )
# result = await conn.execute(stmt)
# run = result.fetchone()
# if run.status == "completed":
#     # All detectors succeeded
#     pass
