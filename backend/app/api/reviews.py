"""Human review endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.security import TokenData, require_human
from app.db import DBConnection, get_db
from app.schemas import ReviewActionRequest, ReviewActionResponse

router = APIRouter()


@router.post(
    "/versions/{version_id}/review",
    response_model=ReviewActionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log human review action",
    description="Log a human review action (Comment, Request Changes, Reject). Human only.",
)
async def review_version(
    version_id: UUID,
    data: ReviewActionRequest,
    db: DBConnection = Depends(get_db),
    current_user: TokenData = Depends(require_human),
) -> ReviewActionResponse:
    """Log a human review action.

    Args:
        version_id: Version UUID
        data: Review action data
        db: Database connection
        current_user: Authenticated human user

    Returns:
        Created review action

    Raises:
        HTTPException: If version not found or user is not human
    """
    # TODO: Implement review action logging
    # 1. Verify version exists
    # 2. Verify user is human (already done by require_human dependency)
    # 3. Insert into human_review_actions table
    # 4. Return created action
    raise NotImplementedError("Review action logging not yet implemented")
