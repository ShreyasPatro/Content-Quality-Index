"""Base task class and utilities for Celery workflows."""

from typing import Any

from celery import Task

from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseTask(Task):
    """Base task class with common functionality.

    Provides:
    - Structured logging
    - Automatic retry with exponential backoff
    - Error handling
    - Task metadata tracking
    """

    # Default retry configuration
    autoretry_for = (Exception,)  # Retry on any exception
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True  # Exponential backoff
    retry_backoff_max = 600  # Max 10 minutes between retries
    retry_jitter = True  # Add randomness to backoff

    def on_failure(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: Any) -> None:
        """Handle task failure.

        Args:
            exc: Exception that caused failure
            task_id: Task ID
            args: Task positional arguments
            kwargs: Task keyword arguments
            einfo: Exception info
        """
        logger.error(
            f"Task {self.name} failed",
            extra={
                "task_id": task_id,
                "exception": str(exc),
                "args": args,
                "kwargs": kwargs,
            },
            exc_info=einfo,
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc: Exception, task_id: str, args: tuple, kwargs: dict, einfo: Any) -> None:
        """Handle task retry.

        Args:
            exc: Exception that caused retry
            task_id: Task ID
            args: Task positional arguments
            kwargs: Task keyword arguments
            einfo: Exception info
        """
        logger.warning(
            f"Task {self.name} retrying",
            extra={
                "task_id": task_id,
                "exception": str(exc),
                "retry_count": self.request.retries,
                "max_retries": self.max_retries,
            },
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval: Any, task_id: str, args: tuple, kwargs: dict) -> None:
        """Handle task success.

        Args:
            retval: Task return value
            task_id: Task ID
            args: Task positional arguments
            kwargs: Task keyword arguments
        """
        logger.info(
            f"Task {self.name} succeeded",
            extra={
                "task_id": task_id,
                "result": retval,
            },
        )
        super().on_success(retval, task_id, args, kwargs)


class IdempotentTask(BaseTask):
    """Task that can be safely retried (idempotent).

    Use this for tasks that check state before executing to avoid duplicate work.
    """

    # More aggressive retry for idempotent tasks
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 5}


class CriticalTask(BaseTask):
    """Task that should not be retried automatically.

    Use this for tasks where retries could cause issues (e.g., external API calls).
    """

    autoretry_for = ()  # No automatic retry
    retry_kwargs = {"max_retries": 0}
