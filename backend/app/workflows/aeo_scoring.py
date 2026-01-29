"""
AEO Scoring Execution Runner.

This module orchestrates the AEO evaluation pipeline:
1. Checks idempotency (prevents duplicate scoring).
2. Fetches blog content.
3. Extracts signals (pure).
4. Computes scores (pure).
5. Persists results (INSERT-ONLY).

# FORBIDDEN IN THIS MODULE:
# - No rewrite logic
# - No approval logic
# - No thresholds that block publishing
# - No environment access
# - No configuration reads
"""

import logging
import asyncio
from uuid import UUID
from datetime import datetime
from dataclasses import asdict

from celery import shared_task
from sqlalchemy import select, insert

from app.db.connection import get_db_connection
from app.models import blog_versions, aeo_scores
from app.aeo.signals import extract_aeo_signals
from app.aeo.scorer import score_aeo

logger = logging.getLogger(__name__)


async def _run_aeo_scoring_impl(
    evaluation_run_id: UUID, blog_version_id: UUID
) -> None:
    """Async implementation of AEO scoring workflow."""
    logger.info(
        f"Starting AEO scoring: run_id={evaluation_run_id} blog_version={blog_version_id}"
    )

    async with get_db_connection() as conn:
        try:
            # 1. Idempotency Check
            # Prevent duplicate scoring for the same run.
            logger.info("Checking for existing AEO scores...")
            existing_score = await conn.execute(
                select(aeo_scores.c.id).where(
                    aeo_scores.c.run_id == evaluation_run_id
                )
            )
            if existing_score.scalar_one_or_none():
                logger.info(
                    f"AEO scores already exist for run {evaluation_run_id} — skipping execution"
                )
                return

            # 2. Fetch Blog Content
            logger.info("Fetching blog content...")
            content_stmt = select(blog_versions.c.content).where(
                blog_versions.c.id == blog_version_id
            )
            result = await conn.execute(content_stmt)
            content = result.scalar_one_or_none()

            if not content:
                logger.error(f"Blog version {blog_version_id} not found or empty.")
                # We do not fail the run here, just abort AEO scoring.
                return

            # 3. Extract Signals (Pure)
            logger.info("Extracting AEO signals...")
            signals = extract_aeo_signals(content)

            # 4. Compute Scores (Pure)
            logger.info("Computing AEO scores...")
            score_result = score_aeo(signals)

            # 5. Persist Results (INSERT-ONLY)
            logger.info("Persisting AEO scores...")
            
            # Remap pillar scores to DB columns
            pillars = score_result.pillars
            
            insert_stmt = insert(aeo_scores).values(
                run_id=evaluation_run_id,
                rubric_version=score_result.rubric_version,
                aeo_total=score_result.total_score,
                
                # Pillar Columns
                aeo_answerability=pillars["aeo_answerability"].score,
                aeo_structure=pillars["aeo_structure"].score,
                aeo_specificity=pillars["aeo_specificity"].score,
                aeo_trust=pillars["aeo_trust"].score,
                aeo_coverage=pillars["aeo_coverage"].score,
                aeo_freshness=pillars["aeo_freshness"].score,
                aeo_readability=pillars["aeo_readability"].score,
                
                # Full Details (Signals + Pillar Breakdowns)
                details=score_result.details
            )
            
            await conn.execute(insert_stmt)
            logger.info(f"AEO scoring completed successfully for run {evaluation_run_id}")

        except Exception as e:
            logger.error(f"AEO Scoring Failed: {e}", exc_info=True)
            # We re-raise to ensure Celery marks this task as failed if needed,
            # though AEO failure generally shouldn't block the pipeline?
            # Prompt implies "Runs after AI detection", usually as a separate step.
            # Best practice: raise so monitoring sees it.
            raise


def run_aeo_scoring(evaluation_run_id: UUID, blog_version_id: UUID) -> None:
    """
    Execute AEO scoring workflow (Synchronous Entry Point).
    Bridged to async implementation for DB access.
    """
    try:
        asyncio.run(_run_aeo_scoring_impl(evaluation_run_id, blog_version_id))
    except Exception as e:
        logger.error(f"run_aeo_scoring failed: {e}")
        raise


@shared_task
def run_aeo_scoring_task(evaluation_run_id: UUID, blog_version_id: UUID):
    """Celery task wrapper for AEO scoring."""
    run_aeo_scoring(evaluation_run_id, blog_version_id)
