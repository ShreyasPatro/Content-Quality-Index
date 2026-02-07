"""Sandbox API schemas."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field

class SandboxAnalyzeRequest(BaseModel):
    """Request model for clean text analysis."""
    content: str = Field(..., min_length=10, description="Markdown content to analyze")

class PillarScoreSchema(BaseModel):
    """Schema for individual pillar scores."""
    score: float
    max_score: float
    reason: List[str]

class AEOScoreResultSchema(BaseModel):
    """Schema for AEO score results."""
    total_score: float
    rubric_version: str
    pillars: Dict[str, PillarScoreSchema]
    details: Dict[str, Any]

class SandboxAnalyzeResponse(BaseModel):
    """Response model for sandbox analysis."""
    aeo: AEOScoreResultSchema

# --- AI Sandbox Schemas ---

class SandboxAIRequest(BaseModel):
    content: str = Field(..., min_length=10, description="Content to check for AI likeness")

class SubScoreItem(BaseModel):
    score: float
    max_score: float
    percentage: float
    explanation: str
    evidence: List[str]

class RubricRawResponse(BaseModel):
    rubric_version: str
    total_score: float
    subscores: Dict[str, SubScoreItem]
    metadata: Dict[str, Any]

class SandboxAIResponse(BaseModel):
    """Response model for AI sandbox analysis."""
    score: float
    model_version: str
    timestamp: str
    raw_response: RubricRawResponse
