"""Evaluation workflow tasks.

This module handles the evaluation pipeline:
1. Create evaluation_run record
2. Check approval state (reject if approved)
3. Trigger downstream detection tasks (AI detectors, AEO scoring)
4. Finalize evaluation and check for regressions
"""

from uuid import UUID

from sqlalchemy import select, text

from app.core.logging import get_logger
from app.db import get_db_connection
from app.models import approval_states, blog_versions, evaluation_runs
from app.workflows.base import IdempotentTask
from app.workflows.exceptions import (
    BlogAlreadyApprovedError,
    EvaluationAlreadyRunningError,
    VersionNotFoundError,
)
from celery_worker import celery_app

logger = get_logger(__name__)


async def start_evaluation(version_id: UUID, triggered_by: UUID | None = None) -> UUID:
    """Start evaluation for a blog version.

    This is the entry point for the evaluation workflow. It:
    1. Validates the version exists
    2. Checks if blog is already approved (rejects if so)
    3. Creates evaluation_run record
    4. Enqueues evaluation task

    Args:
        version_id: Version UUID to evaluate
        triggered_by: User who triggered evaluation (optional)

    Returns:
        Evaluation run UUID

    Raises:
        VersionNotFoundError: If version does not exist
        BlogAlreadyApprovedError: If blog is already approved
    """
    async with get_db_connection() as conn:
        # 1. Fetch version and verify it exists
        version_result = await conn.execute(
            select(blog_versions.c.id, blog_versions.c.blog_id).where(
                blog_versions.c.id == version_id
            )
        )
        version_row = version_result.fetchone()

        if not version_row:
            raise VersionNotFoundError(str(version_id))

        blog_id = version_row.blog_id

        # 2. Check if blog is already approved
        approval_result = await conn.execute(
            select(approval_states.c.id, approval_states.c.approved_version_id)
            .where(approval_states.c.blog_id == blog_id)
            .where(approval_states.c.revoked_at.is_(None))
            .order_by(approval_states.c.approved_at.desc())
            .limit(1)
        )
        approval_row = approval_result.fetchone()

        if approval_row:
            raise BlogAlreadyApprovedError(
                blog_id=str(blog_id),
                approved_version_id=str(approval_row.approved_version_id),
            )

        # 3. Create evaluation_run record
        insert_result = await conn.execute(
            evaluation_runs.insert()
            .values(
                blog_version_id=version_id,
                triggered_by=triggered_by,
                status="processing",
            )
            .returning(evaluation_runs.c.id)
        )
        run_id = insert_result.fetchone()[0]

        logger.info(
            f"Created evaluation run {run_id} for version {version_id}",
            extra={"run_id": str(run_id), "version_id": str(version_id)},
        )

        # 4. Enqueue evaluation task
        evaluate_version.delay(str(run_id))

        return run_id


@celery_app.task(name="workflows.evaluation.evaluate_version", base=IdempotentTask, bind=True)
def evaluate_version(self, run_id: str) -> dict:
    """Evaluate a blog version with AI detectors and AEO scoring.

    This task is idempotent - it checks if evaluation is already completed
    before running detectors.

    Args:
        run_id: Evaluation run UUID

    Returns:
        Evaluation results

    Workflow:
        1. Check if evaluation is already completed (idempotency)
        2. Fetch blog version content
        3. Run AI detector tasks in parallel (TODO)
        4. Run AEO scoring tasks in parallel (TODO)
        5. Finalize evaluation run
        6. Check for score regression and escalate if needed (TODO)
    """
    import asyncio

    logger.info(f"Starting evaluation for run_id={run_id}")

    async def _run_evaluation():
        async with get_db_connection() as conn:
            # 1. Check if already completed (idempotency)
            run_result = await conn.execute(
                select(
                    evaluation_runs.c.id,
                    evaluation_runs.c.status,
                    evaluation_runs.c.completed_at,
                    evaluation_runs.c.blog_version_id,
                ).where(evaluation_runs.c.id == UUID(run_id))
            )
            run_row = run_result.fetchone()

            if not run_row:
                raise ValueError(f"Evaluation run {run_id} not found")

            if run_row.completed_at is not None:
                logger.info(f"Evaluation {run_id} already completed, skipping")
                return {"status": "already_completed", "run_id": run_id}

            version_id = run_row.blog_version_id

            # 2. Fetch version content
            version_result = await conn.execute(
                select(blog_versions.c.content).where(blog_versions.c.id == version_id)
            )
            version_row = version_result.fetchone()
            content = version_row.content

            logger.info(
                f"Fetched content for version {version_id}",
                extra={"version_id": str(version_id), "content_keys": list(content.keys())},
            )

            # TODO: 3. Run AI detector tasks in parallel
            # detector_tasks = [
            #     run_originality_detector.delay(run_id, content),
            #     run_gptzero_detector.delay(run_id, content),
            # ]

            # TODO: 4. Run AEO scoring tasks in parallel
            # aeo_tasks = [
            #     run_aeo_scoring.delay(run_id, content, query_intent)
            #     for query_intent in get_query_intents(version_id)
            # ]

            # TODO: 5. Wait for all tasks to complete
            # results = await asyncio.gather(*detector_tasks, *aeo_tasks)

            # 6. Finalize evaluation run (placeholder)
            await conn.execute(
                evaluation_runs.update()
                .where(evaluation_runs.c.id == UUID(run_id))
                .values(status="completed", completed_at=text("NOW()"))
            )

            logger.info(f"Evaluation {run_id} completed successfully")

            # TODO: 7. Check for score regression and escalate if needed
            # await check_score_regression(run_id, version_id)

            return {
                "status": "completed",
                "run_id": run_id,
                "version_id": str(version_id),
                "detectors_run": 0,  # Placeholder
                "aeo_scores": 0,  # Placeholder
            }

    return asyncio.run(_run_evaluation())


@celery_app.task(name="workflows.evaluation.finalize_evaluation", base=IdempotentTask)
def finalize_evaluation(run_id: str, results: dict) -> dict:
    """Finalize evaluation run after all detectors complete.

    Args:
        run_id: Evaluation run UUID
        results: Aggregated results from detectors

    Returns:
        Finalization status
    """
    # TODO: Implement finalization logic
    # 1. Aggregate detector results
    # 2. Update evaluation_run status
    # 3. Check for score regression
    # 4. Trigger escalation if needed
    raise NotImplementedError("Finalize evaluation not yet implemented")
