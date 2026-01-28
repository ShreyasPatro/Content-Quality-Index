"""Rewrite endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.security import TokenData, get_current_user
from app.db import DBConnection, get_db
from app.schemas import JobResponse, RewriteRequest

router = APIRouter()


@router.post(
    "/versions/{version_id}/rewrite",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request AI rewrite",
    description="Request AI to generate a suggestion for a rewrite (async, advisory only)",
)
async def rewrite_version(
    version_id: UUID,
    data: RewriteRequest,
    db: DBConnection = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> JobResponse:
    """Request AI rewrite for a blog version.

    Args:
        version_id: Version UUID
        data: Rewrite configuration
        db: Database connection
        current_user: Authenticated user

    Returns:
        Job information (202 Accepted)

    Raises:
        HTTPException: If version not found, already approved, or rewrite cap exceeded
    """
    # TODO: Implement rewrite trigger logic
    # 1. Verify version exists
    # 2. Check if blog is approved (reject if approved)
    # 3. Check rewrite cap (max 10 cycles per blog)
    # 4. Create rewrite_cycle record
    # 5. Enqueue Celery task: orchestrate_rewrite.delay(cycle_id, config)
    # 6. Return job_id and status
    raise NotImplementedError("Rewrite trigger not yet implemented")
