"""Celery application for background task processing."""

from celery import Celery
from celery.signals import after_setup_logger, task_failure, task_success

from app.core.config import settings
from app.core.logging import get_logger, setup_logging

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create Celery app
celery_app = Celery(
    "content_quality_engine",
    broker=str(settings.celery_broker_url),
    backend=str(settings.celery_result_backend),
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_track_started=True,
    task_time_limit=300,  # 5 minutes hard limit
    task_soft_time_limit=270,  # 4.5 minutes soft limit
    task_acks_late=True,  # Acknowledge after task completion
    task_reject_on_worker_lost=True,  # Reject if worker crashes
    
    # Retry defaults
    task_default_retry_delay=60,  # 1 minute between retries
    task_max_retries=3,  # Max 3 retries by default
    
    # Worker configuration
    worker_prefetch_multiplier=1,  # Disable prefetching for long tasks
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    worker_disable_rate_limits=False,
    
    # Result backend
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,  # Store additional task metadata
    
    # Task routing (optional)
    task_routes={
        "app.workflows.evaluation.*": {"queue": "evaluation"},
        "app.workflows.rewrite.*": {"queue": "rewrite"},
        "app.workflows.escalation.*": {"queue": "escalation"},
    },
)

# Task autodiscovery
celery_app.autodiscover_tasks(["app.workflows"])

logger.info("Celery app initialized with task autodiscovery")


# Signal handlers for structured logging
@after_setup_logger.connect
def setup_celery_logging(logger, *args, **kwargs):
    """Configure Celery logging to use application logging."""
    setup_logging()


@task_success.connect
def log_task_success(sender=None, result=None, **kwargs):
    """Log successful task completion."""
    logger.info(f"Task {sender.name} completed successfully", extra={"result": result})


@task_failure.connect
def log_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    """Log task failure."""
    logger.error(
        f"Task {sender.name} failed",
        extra={"task_id": task_id, "exception": str(exception)},
        exc_info=True,
    )


# Health check task
@celery_app.task(name="tasks.health_check", bind=True)
def health_check(self):
    """Health check task for Celery.

    Returns:
        Health status
    """
    logger.info("Celery health check executed")
    return {"status": "healthy", "worker": "celery", "task_id": self.request.id}
