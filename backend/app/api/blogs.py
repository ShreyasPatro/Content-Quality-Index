"""Blog ingestion endpoints.

REGULATORY CONSTRAINTS:
- Blog name is human-provided, immutable
- Content is paste-only (source='human_paste')
- Evaluation is human-initiated
- All writes are INSERT-ONLY
"""

import hashlib
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import insert, select

from app.core.security import TokenData, get_current_user
from app.db import DBConnection, get_db, get_db_connection
from app.models.blogs import blog_versions, blogs
from app.schemas import (
    BlogCreate,
    BlogResponse,
    EvaluationTriggerRequest,
    JobResponse,
    VersionCreate,
    VersionResponse,
)

router = APIRouter()


@router.post(
    "/blogs",
    response_model=BlogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new blog",
    description="REGULATORY: Blog name is human-provided and immutable after creation",
)
async def create_blog(
    data: BlogCreate,
    db: DBConnection = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> BlogResponse:
    """Create a new blog.
    
    AUDIT TRAIL: Blog name is human-entered, not auto-generated.
    
    Args:
        data: Blog creation data (name only)
        db: Database connection
        current_user: Authenticated user
        
    Returns:
        Created blog data
        
    Raises:
        HTTPException: If creation fails
    """
    # INSERT-ONLY: Create blog
    stmt = (
        insert(blogs)
        .values(
            name=data.name,
            created_by=str(current_user.user_id),
        )
        .returning(blogs.c.id, blogs.c.name, blogs.c.created_at)
    )
    
    result_proxy = await db.execute(stmt)
    result = result_proxy.mappings().one_or_none()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create blog",
        )
    
    return BlogResponse(
        id=result["id"],
        name=result["name"],
        created_at=result["created_at"],
    )


@router.post(
    "/blogs/{blog_id}/versions",
    response_model=VersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create first blog version",
    description="REGULATORY: Content is paste-only, source must be 'human_paste'",
)
async def create_version(
    blog_id: UUID,
    data: VersionCreate,
    db: DBConnection = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> VersionResponse:
    """Create first version for a blog.
    
    AUDIT TRAIL: Content is paste-only, source is enforced as 'human_paste'.
    CONSTRAINT: Only one version allowed at creation (version_number=1).
    
    Args:
        blog_id: Blog ID
        data: Version creation data (content, source)
        db: Database connection
        current_user: Authenticated user
        
    Returns:
        Created version data
        
    Raises:
        HTTPException: If blog not found or version already exists
    """
    # Verify blog exists
    blog_check = (await db.execute(
        select(blogs.c.id).where(blogs.c.id == str(blog_id))
    )).mappings().one_or_none()
    
    if not blog_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog {blog_id} not found",
        )
    
    # Check if version already exists (first version only)
    existing_version = (await db.execute(
        select(blog_versions.c.id).where(blog_versions.c.blog_id == str(blog_id))
    )).mappings().one_or_none()
    
    if existing_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Blog already has a version. Use version update endpoint for subsequent versions.",
        )
    
    # SECURITY: Enforce source='human_paste'
    if data.source != "human_paste":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source must be 'human_paste' for blog ingestion",
        )
    
    # INSERT-ONLY: Create first version
    stmt = (
        insert(blog_versions)
        .values(
            blog_id=str(blog_id),
            parent_version_id=None,  # First version has no parent
            content=data.content,
            content_hash=hashlib.sha256(data.content.encode()).hexdigest(),
            source=data.source,
            version_number=1,
            created_by=str(current_user.user_id),
        )
        .returning(
            blog_versions.c.id,
            blog_versions.c.blog_id,
            blog_versions.c.version_number,
            blog_versions.c.source,
            blog_versions.c.created_at,
        )
    )
    
    result_proxy = await db.execute(stmt)
    result = result_proxy.mappings().one_or_none()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create version",
        )
    
    # CRITICAL: Commit transaction immediately so version is visible to evaluation workflow
    # The evaluation workflow opens a new DB connection and needs to see this version
    await db.commit()
    
    return VersionResponse(
        id=result["id"],
        blog_id=result["blog_id"],
        version_number=result["version_number"],
        source=result["source"],
        created_at=result["created_at"],
    )


@router.post(
    "/evaluation-runs",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger evaluation pipeline",
    description="REGULATORY: Evaluation is human-initiated, triggers AI Likeness + AEO scoring",
)
async def trigger_evaluation(
    data: EvaluationTriggerRequest,
    db: DBConnection = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> JobResponse:
    """Trigger evaluation pipeline for a blog version.
    
    AUDIT TRAIL: Evaluation is explicitly triggered by human user.
    PIPELINE: Enqueues Celery task for AI Likeness + AEO scoring.
    
    Args:
        data: Evaluation trigger data (blog_id, version_id)
        db: Database connection
        current_user: Authenticated user
        
    Returns:
        Job response with run_id
        
    Raises:
        HTTPException: If version not found
    """
    # Verify version exists
    version_check = (await db.execute(
        select(blog_versions.c.id, blog_versions.c.blog_id)
        .where(blog_versions.c.id == str(data.version_id))
        .where(blog_versions.c.blog_id == str(data.blog_id))
    )).mappings().one_or_none()
    
    if not version_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {data.version_id} not found for blog {data.blog_id}",
        )
    
    # INSERT-ONLY: Create evaluation run
    from app.models.evaluations import evaluation_runs
    
    stmt = (
        insert(evaluation_runs)
        .values(
            blog_version_id=str(data.version_id),
            triggered_by=str(current_user.user_id),
            status="queued",
        )
        .returning(evaluation_runs.c.id, evaluation_runs.c.status)
    )
    
    result_proxy = await db.execute(stmt)
    result = result_proxy.mappings().one_or_none()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create evaluation run",
        )
    
    run_id = result["id"]
    
    # Enqueue evaluation pipeline
    # REGULATORY: This triggers deterministic AI Likeness + AEO scoring only
    try:
        import os
        from app.workflows.evaluation_orchestrator import (
            run_full_evaluation_task,
            run_full_evaluation_sync,
        )
        
        # Check if Celery is available (async mode)
        use_celery = os.getenv("USE_CELERY", "true").lower() == "true"
        
        if use_celery:
            # Async mode: Enqueue Celery task
            run_full_evaluation_task.delay(str(run_id), str(data.version_id))
        else:
            # Synchronous fallback mode: Run inline
            # WARNING: This blocks the request until evaluation completes
            import asyncio
            asyncio.create_task(
                asyncio.to_thread(
                    run_full_evaluation_sync, run_id, data.version_id
                )
            )
    except Exception as e:
        # Log error but don't fail the request
        # Evaluation run is already created with status='queued'
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to enqueue evaluation: {e}", exc_info=True)
    
    return JobResponse(
        job_id=run_id,
        status="queued",
        eta_seconds=30,  # Estimated time
    )


@router.get(
    "/evaluation-runs/{run_id}",
    response_model="EvaluationStatusResponse",
    summary="Get evaluation status",
    description="REGULATORY: Read-only status check for evaluation run",
)
async def get_evaluation_status(
    run_id: UUID,
    db: DBConnection = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> "EvaluationStatusResponse":
    """Get evaluation run status and scores.
    
    REGULATORY: Read-only endpoint, no mutations.
    Returns scores only when evaluation is completed.
    
    Args:
        run_id: UUID of the evaluation run
        db: Database connection
        current_user: Authenticated user
        
    Returns:
        Evaluation status with scores (if completed)
        
    Raises:
        HTTPException: If run not found
    """
    from app.models.evaluations import evaluation_runs
    from app.models.scores import ai_likeness_rubric_scores
    from app.models.aeo_scores import aeo_scores
    from app.schemas import EvaluationStatusResponse
    
    # Fetch evaluation run
    run = (await db.execute(
        select(evaluation_runs).where(evaluation_runs.c.id == str(run_id))
    )).mappings().one_or_none()
    
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation run {run_id} not found",
        )
    
    # Fetch scores if completed
    ai_score = None
    aeo_score_value = None
    
    if run["status"] == "completed":
        # Fetch AI Likeness score
        ai_result = (await db.execute(
            select(ai_likeness_rubric_scores.c.total_score)
            .where(ai_likeness_rubric_scores.c.evaluation_run_id == run_id)
        )).mappings().one_or_none()
        if ai_result:
            ai_score = ai_result["total_score"]
        
        # Fetch AEO score
        aeo_result = (await db.execute(
            select(aeo_scores.c.total_score)
            .where(aeo_scores.c.evaluation_run_id == run_id)
        )).mappings().one_or_none()
        if aeo_result:
            aeo_score_value = aeo_result["total_score"]
    
    return EvaluationStatusResponse(
        run_id=run_id,
        status=run["status"],
        ai_likeness_score=ai_score,
        aeo_score=aeo_score_value,
        completed_at=run.get("completed_at"),
    )
