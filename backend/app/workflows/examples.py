"""Example task implementations (placeholders).

This file demonstrates how to create tasks using the base task classes.
"""

from uuid import UUID

from celery_worker import celery_app
from app.core.logging import get_logger
from app.workflows.base import BaseTask, CriticalTask, IdempotentTask

logger = get_logger(__name__)


# ============================================================================
# Evaluation Tasks (Idempotent)
# ============================================================================


@celery_app.task(name="workflows.evaluation.evaluate_version", base=IdempotentTask, bind=True)
def evaluate_version(self, run_id: str) -> dict:
    """Evaluate a blog version with AI detectors and AEO scoring.

    This task is idempotent - it checks if evaluation is already completed
    before running detectors.

    Args:
        run_id: Evaluation run UUID

    Returns:
        Evaluation results
    """
    logger.info(f"Starting evaluation for run_id={run_id}")
    
    # TODO: Implement evaluation logic
    # 1. Check if run is already completed (idempotency)
    # 2. Fetch blog version content
    # 3. Run AI detector tasks in parallel
    # 4. Run AEO scoring tasks in parallel
    # 5. Finalize evaluation run
    # 6. Check for score regression and escalate if needed
    
    raise NotImplementedError("Evaluation task not yet implemented")


# ============================================================================
# Rewrite Tasks (Critical - no auto-retry)
# ============================================================================


@celery_app.task(name="workflows.rewrite.orchestrate_rewrite", base=CriticalTask, bind=True)
def orchestrate_rewrite(self, cycle_id: str, config: dict) -> dict:
    """Orchestrate AI rewrite generation.

    This task is critical and does not auto-retry because LLM calls are
    expensive and may have already succeeded partially.

    Args:
        cycle_id: Rewrite cycle UUID
        config: Rewrite configuration

    Returns:
        Rewrite results
    """
    logger.info(f"Starting rewrite for cycle_id={cycle_id}")
    
    # TODO: Implement rewrite logic
    # 1. Re-check approval state (TOCTOU protection)
    # 2. Fetch source version content
    # 3. Call LLM API with prompt template
    # 4. Store suggestion in rewrite_suggestions
    # 5. Update rewrite_cycle.completed_at
    
    raise NotImplementedError("Rewrite task not yet implemented")


# ============================================================================
# Escalation Tasks (Idempotent)
# ============================================================================


@celery_app.task(name="workflows.escalation.escalate_to_human", base=IdempotentTask, bind=True)
def escalate_to_human(self, blog_id: str, version_id: str, reason: str, details: dict) -> dict:
    """Escalate a blog version to human review.

    This task is idempotent - it checks for existing escalations before creating.

    Args:
        blog_id: Blog UUID
        version_id: Version UUID
        reason: Escalation reason
        details: Additional details

    Returns:
        Escalation record
    """
    logger.info(f"Escalating blog_id={blog_id}, reason={reason}")
    
    # TODO: Implement escalation logic
    # 1. Check for existing escalation (idempotency)
    # 2. Insert escalation record
    # 3. Send notification to reviewers
    
    raise NotImplementedError("Escalation task not yet implemented")
