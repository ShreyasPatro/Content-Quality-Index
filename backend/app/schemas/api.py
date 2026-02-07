"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Blog Schemas
# ============================================================================


class BlogCreate(BaseModel):
    """Request schema for creating a blog.
    
    REGULATORY: Blog name is human-provided, immutable after creation.
    """

    name: str = Field(..., min_length=3, max_length=100, description="Human-provided blog name")


class BlogResponse(BaseModel):
    """Response schema for blog data."""

    id: UUID
    name: str
    created_at: datetime


# ============================================================================
# Version Schemas
# ============================================================================


class VersionCreate(BaseModel):
    """Request schema for creating a blog version.
    
    REGULATORY: Content is paste-only, source is enforced as 'human_paste'.
    """

    content: str = Field(..., min_length=100, description="Pasted blog content")
    source: str = Field(..., pattern=r"^human_paste$", description="Must be 'human_paste'")


class VersionResponse(BaseModel):
    """Response schema for version data."""

    id: UUID
    blog_id: UUID
    version_number: int
    source: str
    created_at: datetime


# ============================================================================
# Evaluation Schemas
# ============================================================================


class EvaluationTriggerRequest(BaseModel):
    """Request schema for triggering evaluation pipeline.
    
    REGULATORY: Evaluation is human-initiated, not automatic.
    """

    blog_id: UUID
    version_id: UUID


class EvaluationRequest(BaseModel):
    """Request schema for triggering evaluation."""

    include_detectors: bool = True
    include_aeo: bool = True


class EvaluationTriggerRequest(BaseModel):
    """Request schema for blog ingestion evaluation trigger.
    
    REGULATORY: Human-initiated evaluation only.
    """

    blog_id: UUID
    version_id: UUID


class EvaluationStatusResponse(BaseModel):
    """Response schema for evaluation status polling.
    
    REGULATORY: Read-only status check, no mutations.
    """

    run_id: UUID
    status: str  # queued, processing, completed, failed
    ai_likeness_score: float | None = None
    aeo_score: float | None = None
    completed_at: datetime | None = None


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
