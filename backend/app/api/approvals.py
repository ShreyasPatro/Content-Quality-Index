"""Approval endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.security import TokenData, require_human
from app.db import DBConnection, get_db
from app.schemas import ApprovalRequest, ApprovalResponse

router = APIRouter()


@router.post(
    "/blogs/{blog_id}/approve",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Approve a blog version",
    description="Set the specific version as the APPROVED state for the blog. Human only.",
)
async def approve_blog(
    blog_id: UUID,
    data: ApprovalRequest,
    db: DBConnection = Depends(get_db),
    current_user: TokenData = Depends(require_human),
) -> ApprovalResponse:
    """Approve a blog version.

    Args:
        blog_id: Blog UUID
        data: Approval data
        db: Database connection
        current_user: Authenticated human user

    Returns:
        Created approval state

    Raises:
        HTTPException: If blog/version not found, version mismatch, or user is not human
    """
    # TODO: Implement approval logic
    # 1. Verify blog exists
    # 2. Verify approved_version_id belongs to blog_id
    # 3. Verify user is human (already done by require_human dependency)
    # 4. Check for fast approval (< 30 seconds since version creation)
    # 5. Log approval attempt to approval_attempts table
    # 6. Insert into approval_states table
    # 7. If fast approval, add warning to notes and log to fast_approvals
    # 8. Return created approval state
    raise NotImplementedError("Approval logic not yet implemented")
