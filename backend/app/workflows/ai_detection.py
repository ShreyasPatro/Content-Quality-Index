"""
AI Detection Execution Runner (Stage 5.5 — PASS 2).

This module contains the execution logic for the AI detection pipeline.
It is an advisory-only system that runs:
1. Internal generic rubric scoring
2. External AI detectors (via registry)

Key Characteristics:
- Advisory-Only: Failures in detectors do not block the pipeline unless ALL fail.
- Audit-Safe: Uses INSERT-ONLY patterns for scores.
- Immutable-Compliant: Only updates status/timestamps on evaluation_runs.
- Partial Failure Support: Continues execution even if individual detectors fail.
- Robustness: Timeouts, limited retries, and failure accounting.

Architecture:
- run_ai_detection: Pure function (synchronous entry point) containing the logic.
- run_ai_detection_task: Thin Celery wrapper.

Failure Semantics:
- Rubric: No retries. Logs failure.
- Detectors: Max 1 retry on Timeout/Unavailable.
- Final Status: 'completed' if ANY detector (or rubric) succeeds. 'partial_failure' if ALL fail.

# FORBIDDEN IN THIS MODULE:
# - No rewrite logic
# - No approval logic
# - No thresholds that block publishing
# - No detector prioritization
# - No environment access
# - No configuration reads
"""

import logging
import asyncio
import time
import contextlib
from typing import Optional, List, Dict, Any, Type
from uuid import UUID
from datetime import datetime

from celery import shared_task
import sqlalchemy as sa
from sqlalchemy import select, update, insert

from app.db.connection import get_db_connection
from app.models import blog_versions, evaluation_runs, ai_detector_scores, ai_likeness_rubric_scores
# from app.models import ai_likeness_rubric_scores

from app.ai_detection.rubric.score_ai_likeness import score_ai_likeness
from app.services.ai_detectors.registry import get_global_registry
from app.services.ai_detectors.base import (
    DetectorError,
    DetectorTimeout,
    DetectorUnavailable,
    DetectorInvalidResponse,
)

# Constants
DETECTOR_TIMEOUT_SECONDS = 10
MAX_RETRIES = 1

# Configure logger
logger = logging.getLogger(__name__)


async def _run_detector_with_timeout(detector: Any, content: str) -> Any:
    """Run detector with timeout enforcement using default executor."""
    loop = asyncio.get_running_loop()
    try:
        # Run blocking detector in thread pool to allow timeout
        return await asyncio.wait_for(
            loop.run_in_executor(None, detector.detect, content),
            timeout=DETECTOR_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        logger.warning(
            f"Detector {detector.name} timed out after {DETECTOR_TIMEOUT_SECONDS}s"
        )
        raise DetectorTimeout(f"Exceeded {DETECTOR_TIMEOUT_SECONDS}s limit")


async def _process_detector(
    conn: Any,
    evaluation_run_id: UUID,
    detector: Any,
    blog_content: str
) -> bool:
    """
    Execute a single detector with retries and error handling.
    Returns True if successful, False otherwise.
    """
    # Idempotency check: prevent duplicate execution on Celery retry
    existing_score = await conn.execute(
        select(ai_detector_scores.c.id).where(
            ai_detector_scores.c.run_id == evaluation_run_id,
            # PROVIDER IDENTITY INVARIANT:
            # The provider used for insertion MUST match the detector.name.
            # This combination (run_id, provider) acts as the uniqueness boundary.
            ai_detector_scores.c.provider == detector.name,
        )
    )
    if existing_score.scalar_one_or_none():
        # Idempotency guarantee:
        # If this detector already produced a score for this run_id,
        # treat as SUCCESS to ensure retries do not downgrade status.
        logger.info(
            f"Detector {detector.name} already executed for run {evaluation_run_id} — skipping"
        )
        return True

    logger.info(f"Detector Start: name={detector.name} version={detector.version}")
    
    attempt = 0
    final_exception = None

    while attempt <= MAX_RETRIES:
        attempt += 1
        try:
            if attempt > 1:
                logger.info(f"Detector Retry: name={detector.name} attempt={attempt}")

            # Execute with timeout
            det_result = await _run_detector_with_timeout(detector, blog_content)
            
            # INSERT detector score (INSERT-ONLY)
            await conn.execute(
                insert(ai_detector_scores).values(
                    run_id=evaluation_run_id,
                    provider=detector.name,
                    score=det_result.score,
                    details=det_result.to_dict()
                )
            )
            
            logger.info(f"Detector Success: name={detector.name}")
            return True

        except (DetectorTimeout, DetectorUnavailable) as e:
            logger.warning(f"Detector Transient Failure: name={detector.name} error={e}")
            final_exception = e
            # Allow retry for these specific errors
            if attempt <= MAX_RETRIES:
                continue
        except DetectorInvalidResponse as e:
            logger.error(f"Detector Invalid Response: name={detector.name} error={e}")
            final_exception = e
            # Do NOT retry invalid response
            break
        except Exception as e:
            logger.error(
                f"Detector Unexpected Failure: name={detector.name} error={e}",
                exc_info=True
            )
            final_exception = e
            # Do NOT retry unexpected errors
            break

    # If we get here, valid attempts failed
    logger.error(
        f"Detector Final Failure: name={detector.name} after {attempt} attempts. "
        f"Last error: {final_exception}"
    )
    return False


async def _run_ai_detection_impl(
    evaluation_run_id: UUID, blog_version_id: UUID
) -> None:
    """Async implementation of the AI detection control flow."""
    # Determinism Assertion:
    # Given the same DB state and external detector responses, this function
    # must always produce the same final status. It contains no random branching.
    logger.info(
        f"Starting AI detection run: id={evaluation_run_id} blog_version={blog_version_id}"
    )

    success_count = 0
    failure_count = 0
    total_detectors = 0

    async with get_db_connection() as conn:
        try:
            # 1. Fetch Blog Content
            logger.info("Fetching blog content...")
            stmt = select(blog_versions.c.content).where(
                blog_versions.c.id == blog_version_id
            )
            result = await conn.execute(stmt)
            blog_content = result.scalar_one_or_none()

            if not blog_content:
                logger.error(f"Blog version {blog_version_id} not found or empty.")
                await _update_run_status(conn, evaluation_run_id, "failed")
                return

            # 2. Fetch Evaluation Run
            logger.info("Fetching evaluation run...")
            stmt = select(evaluation_runs).where(
                evaluation_runs.c.id == evaluation_run_id
            )
            result = await conn.execute(stmt)
            run_row = result.fetchone()

            if not run_row:
                logger.error(f"Evaluation run {evaluation_run_id} not found.")
                return

            # 3. Internal Rubric Scorer
            logger.info("Invoking internal rubric scorer...")
            try:
                # Idempotency Check:
                # Before running or inserting, check if a rubric score already exists for this run.
                # If it exists, we treat this as a SUCCESS (short-circuit) to prevent IntegrityError on retries.
                existing_rubric_score = await conn.execute(
                    select(ai_likeness_rubric_scores.c.id).where(
                        ai_likeness_rubric_scores.c.run_id == evaluation_run_id
                    )
                )
                
                if existing_rubric_score.scalar_one_or_none():
                    logger.info(f"Rubric score already exists for run {evaluation_run_id} — skipping execution")
                    # Count as success because the work is effectively done
                    success_count += 1
                else:
                    rubric_result = score_ai_likeness(blog_content)
                    
                    # INSERT rubric score (INSERT-ONLY)
                    await conn.execute(
                        insert(ai_likeness_rubric_scores).values(
                            run_id=evaluation_run_id,
                            score=rubric_result["score"],
                            details=rubric_result,
                        )
                    )
                    logger.info("Rubric scoring successful.")
                    success_count += 1

            except Exception as e:
                logger.error(f"Rubric scorer failed: {e}", exc_info=True)
                failure_count += 1

            # 4. External Detectors
            logger.info("Invoking external detectors...")
            registry = get_global_registry()
            detectors = registry.get_active_detectors(config=None)
            total_detectors = len(detectors)

            for detector in detectors:
                result = await _process_detector(
                    conn, evaluation_run_id, detector, blog_content
                )
                if result:
                    success_count += 1
                else:
                    failure_count += 1

            # 5. Determine Final Status
            # Final Status Derivation:
            # - Status is derived SOLELY from the success count of methods executed or verified.
            # - Runtime counters (success_count) include both "freshly executed" and "previously executed" (idempotent skipped).
            # - This guarantees that a retry which finds an existing score still counts it as a success, maintaining status correctness.
            # If success_count == 0 (meaning ALL detectors AND rubric failed) -> partial_failure
            # Otherwise (at least one success) -> completed
            final_status = "completed"
            if success_count == 0:
                logger.error(
                    f"All detection methods failed. rubric_failed={failure_count > 0} "
                    f"detectors_failed={failure_count}"
                )
                final_status = "partial_failure"

            logger.info(
                f"Run Summary: total_methods={1 + total_detectors} "
                f"successes={success_count} failures={failure_count} "
                f"status={final_status}"
            )

            await _update_run_status(conn, evaluation_run_id, final_status)

        except Exception as e:
            logger.error(f"Critical execution error: {e}", exc_info=True)
            try:
                await _update_run_status(conn, evaluation_run_id, "partial_failure")
            except Exception:
                pass
            raise


async def _update_run_status(conn, run_id: UUID, status: str) -> None:
    """Helper to update run status."""
    logger.info(f"Updating run {run_id} status to {status}")
    stmt = update(evaluation_runs).where(
        evaluation_runs.c.id == run_id
    ).values(
        status=status,
        completed_at=datetime.utcnow()
    )
    await conn.execute(stmt)


def run_ai_detection(evaluation_run_id: UUID, blog_version_id: UUID) -> None:
    """
    Execute AI detection workflow (Synchronous Entry Point).
    
    Bridged to async implementation for DB access.
    
    Args:
        evaluation_run_id: UUID, ID of the evaluation run
        blog_version_id: UUID, ID of the blog version to test
    """
    try:
        # Use asyncio.run to execute the async implementation
        # This is required because the database layer is asynchronous
        asyncio.run(_run_ai_detection_impl(evaluation_run_id, blog_version_id))
    except Exception as e:
        logger.error(f"run_ai_detection failed: {e}")
        raise


@shared_task
def run_ai_detection_task(evaluation_run_id: UUID, blog_version_id: UUID):
    """
    Celery task wrapper for AI detection.
    
    This task ONLY calls the pure function run_ai_detection.
    """
    run_ai_detection(evaluation_run_id, blog_version_id)
