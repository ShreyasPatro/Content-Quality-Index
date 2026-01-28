"""Evaluation endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import TokenData, get_current_user
from app.db import DBConnection, get_db
from app.schemas import EvaluationRequest, JobResponse
from app.workflows import BlogAlreadyApprovedError, VersionNotFoundError, start_evaluation

router = APIRouter()


@router.post(
    "/versions/{version_id}/evaluate",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger evaluation",
    description="Trigger a suite of AI/AEO/Quality checks (async)",
)
async def evaluate_version(
    version_id: UUID,
    data: EvaluationRequest,
    db: DBConnection = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> JobResponse:
    """Trigger evaluation for a blog version.

    Args:
        version_id: Version UUID
        data: Evaluation configuration
        db: Database connection
        current_user: Authenticated user

    Returns:
        Job information (202 Accepted)

    Raises:
        HTTPException: If version not found or blog already approved
    """
    try:
        run_id = await start_evaluation(
            version_id=version_id,
            triggered_by=current_user.user_id,
        )

        return JobResponse(
            job_id=run_id,
            status="queued",
            eta_seconds=30,
        )

    except VersionNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_id} not found",
        )

    except BlogAlreadyApprovedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Blog is already approved (version {e.approved_version_id}). Cannot evaluate approved content.",
        )
