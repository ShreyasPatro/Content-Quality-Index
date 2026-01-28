"""Workflows package for Celery tasks.

This package contains all background task workflows organized by domain:
- evaluation: AI detector and AEO scoring tasks
- rewrite: AI rewrite generation tasks
- escalation: Human escalation tasks

All tasks use the base task classes from app.workflows.base for consistent
retry behavior and logging.
"""

from app.workflows.base import BaseTask, CriticalTask, IdempotentTask
from app.workflows.evaluation import evaluate_version, start_evaluation
from app.workflows.exceptions import (
    BlogAlreadyApprovedError,
    EvaluationAlreadyRunningError,
    InvalidStateError,
    RewriteCapExceededError,
    VersionNotFoundError,
    WorkflowError,
)

__all__ = [
    # Base classes
    "BaseTask",
    "IdempotentTask",
    "CriticalTask",
    # Evaluation
    "start_evaluation",
    "evaluate_version",
    # Exceptions
    "WorkflowError",
    "InvalidStateError",
    "BlogAlreadyApprovedError",
    "VersionNotFoundError",
    "EvaluationAlreadyRunningError",
    "RewriteCapExceededError",
]
