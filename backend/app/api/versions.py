"""Blog version management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.security import TokenData, get_current_user
from app.db import DBConnection, get_db
from app.schemas import VersionCreate, VersionResponse

router = APIRouter()


@router.post(
    "/blogs/{blog_id}/versions",
    response_model=VersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new blog version",
    description="Create a NEW immutable version of the blog. This is the only way to edit content.",
)
async def create_version(
    blog_id: UUID,
    data: VersionCreate,
    db: DBConnection = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> VersionResponse:
    """Create a new blog version.

    Args:
        blog_id: Blog UUID
        data: Version creation data
        db: Database connection
        current_user: Authenticated user

    Returns:
        Created version data

    Raises:
        HTTPException: If creation fails or validation errors
    """
    # TODO: Implement version creation logic
    # 1. Verify blog exists
    # 2. Validate parent_version_id (if provided)
    # 3. Calculate next version_number
    # 4. Insert into blog_versions table
    # 5. If source_rewrite_cycle_id provided, link to rewrite cycle
    # 6. Return created version
    raise NotImplementedError("Version creation not yet implemented")
