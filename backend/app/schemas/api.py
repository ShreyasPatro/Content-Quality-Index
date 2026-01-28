"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Blog Schemas
# ============================================================================


class BlogCreate(BaseModel):
    """Request schema for creating a blog."""

    title_slug: str = Field(..., pattern=r"^[a-z0-9-]+$", min_length=1, max_length=200)
    project_id: UUID | None = None


class BlogResponse(BaseModel):
    """Response schema for blog data."""

    id: UUID
    title_slug: str
    created_at: datetime


# ============================================================================
# Version Schemas
# ============================================================================


class VersionCreate(BaseModel):
    """Request schema for creating a blog version."""

    parent_version_id: UUID | None = Field(None, description="NULL for first version only")
    content: dict[str, Any] = Field(..., description="Full JSON body")
    change_reason: str = Field(..., min_length=5)
    source_rewrite_cycle_id: UUID | None = Field(
        None,
        description="If accepting AI-generated rewrite suggestion, provide rewrite_cycle.id",
    )


class VersionResponse(BaseModel):
    """Response schema for version data."""

    id: UUID
    blog_id: UUID
    version_number: int
    content_hash: str
    created_at: datetime
    created_by: UUID


# ============================================================================
# Evaluation Schemas
# ============================================================================


class EvaluationRequest(BaseModel):
    """Request schema for triggering evaluation."""

    include_detectors: bool = True
    include_aeo: bool = True


class JobResponse(BaseModel):
    """Response schema for async job."""

    job_id: UUID
    status: str = "queued"
    eta_seconds: int | None = None


# ============================================================================
# Rewrite Schemas
# ============================================================================


class RewriteRequest(BaseModel):
    """Request schema for AI rewrite."""

    prompt_template_id: UUID | None = None
    instructions: str
    target_sections: list[str] | None = None


# ============================================================================
# Review Schemas
# ============================================================================


class ReviewActionRequest(BaseModel):
    """Request schema for human review action."""

    action: str = Field(..., pattern=r"^(COMMENT|REQUEST_CHANGES|REJECT|APPROVE_INTENT)$")
    comments: str


class ReviewActionResponse(BaseModel):
    """Response schema for review action."""

    id: UUID
    action: str
    performed_at: datetime


# ============================================================================
# Approval Schemas
# ============================================================================


class ApprovalRequest(BaseModel):
    """Request schema for blog approval."""

    approved_version_id: UUID
    notes: str | None = None


class ApprovalResponse(BaseModel):
    """Response schema for approval state."""

    id: UUID
    blog_id: UUID
    approved_version_id: UUID
    approver_id: UUID
    approved_at: datetime
