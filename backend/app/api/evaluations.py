"""Evaluation endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import TokenData, get_current_user
from app.db import DBConnection, get_db
from app.schemas import EvaluationRequest, JobResponse
from app.models.evaluations import evaluation_runs
from app.schemas import EvaluationRequest, EvaluationStatusResponse, JobResponse
from app.workflows import BlogAlreadyApprovedError, VersionNotFoundError, start_evaluation
from sqlalchemy import select

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


@router.get(
    "/evaluation-runs/{run_id}",
    response_model=EvaluationStatusResponse,
    summary="Get evaluation status",
    description="Poll for evaluation status",
)
async def get_evaluation_status(
    run_id: UUID,
    db: DBConnection = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> EvaluationStatusResponse:
    """Get status of an evaluation run.
    
    Args:
        run_id: Evaluation run UUID
        
    Returns:
        Status and scores (if completed)
    """
    stmt = select(evaluation_runs).where(evaluation_runs.c.id == run_id)
    run = await db.fetch_one(stmt)
    
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
        
    # TODO: Fetch and aggregate scores if completed
    # For now, return status to unblock UI polling
    
    return EvaluationStatusResponse(
        run_id=run["id"],
        status=run["status"],
        ai_likeness_score=None,
        aeo_score=None,
        completed_at=run["completed_at"],
    )
