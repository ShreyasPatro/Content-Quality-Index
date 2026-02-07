"""Evaluation Pipeline Orchestrator.

This module coordinates the full evaluation lifecycle:
1. AI Likeness Detection (Stage 5)
2. AEO Scoring (Stage 6)

REGULATORY CONSTRAINTS:
- INSERT-ONLY database operations
- Deterministic scoring (no ML inference)
- Full audit trail preservation
- Idempotent task execution
- No silent failures

FORBIDDEN:
- No UPDATE/DELETE on score tables
- No parallel execution of scorers
- No optimistic status updates
- No hidden defaults
"""

import logging
import asyncio
from uuid import UUID
from datetime import datetime
from typing import Optional

from celery import shared_task
from sqlalchemy import select, update

from app.db.connection import get_db_connection
from app.models import evaluation_runs

logger = logging.getLogger(__name__)


async def _run_full_evaluation_impl(
    evaluation_run_id: UUID, blog_version_id: UUID
) -> None:
    """Async implementation of full evaluation workflow.
    
    REGULATORY: This function orchestrates deterministic scoring only.
    No approval, rewrite, or publishing logic is executed.
    
    Args:
        evaluation_run_id: UUID of the evaluation run
        blog_version_id: UUID of the blog version to evaluate
        
    Raises:
        Exception: On critical failures (logged and status updated)
    """
    logger.info(
        f"Starting full evaluation: run_id={evaluation_run_id} "
        f"version_id={blog_version_id}"
    )
    
    async with get_db_connection() as conn:
        try:
            # STEP 1: Mark as processing
            # REGULATORY: This is an allowed status transition
            logger.info("Updating evaluation_runs status to 'processing'")
            await conn.execute(
                update(evaluation_runs)
                .where(evaluation_runs.c.id == evaluation_run_id)
                .values(status="processing")
            )
            await conn.commit()
            
            # STEP 2: Run AI Likeness Detection
            # REGULATORY: Deterministic rubric-based scoring
            logger.info("Running AI Likeness detection...")
            from app.workflows.ai_detection import run_ai_detection_sync
            
            try:
                run_ai_detection_sync(evaluation_run_id, blog_version_id)
                logger.info("AI Likeness detection completed successfully")
            except Exception as e:
                logger.error(f"AI Likeness detection failed: {e}", exc_info=True)
                # Continue to AEO scoring (partial failure allowed)
            
            # STEP 3: Run AEO Scoring
            # REGULATORY: Deterministic signal extraction + scoring
            logger.info("Running AEO scoring...")
            from app.workflows.aeo_scoring import run_aeo_scoring_sync
            
            try:
                run_aeo_scoring_sync(evaluation_run_id, blog_version_id)
                logger.info("AEO scoring completed successfully")
            except Exception as e:
                logger.error(f"AEO scoring failed: {e}", exc_info=True)
                # Partial failure is acceptable
            
            # STEP 4: Mark as completed
            # REGULATORY: Final status transition with timestamp
            logger.info("Marking evaluation as completed")
            await conn.execute(
                update(evaluation_runs)
                .where(evaluation_runs.c.id == evaluation_run_id)
                .values(
                    status="completed",
                    completed_at=datetime.utcnow()
                )
            )
            await conn.commit()
            
            logger.info(f"Full evaluation completed: run_id={evaluation_run_id}")
            
        except Exception as e:
            # CRITICAL FAILURE: Mark as failed
            logger.error(
                f"Evaluation pipeline failed: run_id={evaluation_run_id}",
                exc_info=True
            )
            
            try:
                await conn.execute(
                    update(evaluation_runs)
                    .where(evaluation_runs.c.id == evaluation_run_id)
                    .values(
                        status="failed",
                        completed_at=datetime.utcnow()
                    )
                )
                await conn.commit()
            except Exception as update_error:
                logger.error(
                    f"Failed to update status to 'failed': {update_error}",
                    exc_info=True
                )
            
            raise


def run_full_evaluation_sync(
    evaluation_run_id: UUID, blog_version_id: UUID
) -> None:
    """Synchronous wrapper for evaluation orchestrator.
    
    Used for:
    - Synchronous fallback mode (no Celery)
    - Testing
    - Direct invocation
    
    Args:
        evaluation_run_id: UUID of the evaluation run
        blog_version_id: UUID of the blog version to evaluate
    """
    asyncio.run(_run_full_evaluation_impl(evaluation_run_id, blog_version_id))


@shared_task(
    name="workflows.run_full_evaluation",
    bind=True,
    max_retries=0,  # No automatic retries (idempotency handled internally)
    acks_late=True,
)
def run_full_evaluation_task(
    self, evaluation_run_id: str, blog_version_id: str
) -> dict:
    """Celery task for full evaluation pipeline.
    
    REGULATORY: This task is idempotent and safe to retry manually.
    Scoring workflows handle duplicate detection internally.
    
    Args:
        evaluation_run_id: String UUID of the evaluation run
        blog_version_id: String UUID of the blog version
        
    Returns:
        Task result summary
        
    Raises:
        Exception: On critical failures (task will be marked as failed)
    """
    logger.info(
        f"Celery task started: run_full_evaluation_task "
        f"run_id={evaluation_run_id} version_id={blog_version_id}"
    )
    
    try:
        run_full_evaluation_sync(
            UUID(evaluation_run_id),
            UUID(blog_version_id)
        )
        
        return {
            "status": "completed",
            "evaluation_run_id": evaluation_run_id,
            "blog_version_id": blog_version_id,
        }
        
    except Exception as e:
        logger.error(
            f"Celery task failed: run_full_evaluation_task "
            f"run_id={evaluation_run_id}",
            exc_info=True
        )
        raise
