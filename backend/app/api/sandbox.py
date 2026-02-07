"""Sandbox API endpoints."""

from fastapi import APIRouter, HTTPException, status
from app.schemas.sandbox import SandboxAnalyzeRequest, SandboxAnalyzeResponse
from app.aeo.signals import extract_aeo_signals
from app.aeo.scorer import score_aeo
from dataclasses import asdict

router = APIRouter()

@router.post(
    "/aeo",
    response_model=SandboxAnalyzeResponse,
    summary="Analyze AEO score (Sandbox)",
    description="Run AEO scoring on raw text without saving to database. Purely for testing/simulation."
)
async def analyze_aeo(request: SandboxAnalyzeRequest) -> SandboxAnalyzeResponse:
    """Run AEO analysis on provided content."""
    try:
        # 1. Extract pure signals
        signals = extract_aeo_signals(request.content)
        
        # 2. Run deterministic scorer
        result = score_aeo(signals)
        
        # 3. Return results directly
        return SandboxAnalyzeResponse(aeo=asdict(result))
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

# --- AI Sandbox Endpoint ---

from app.schemas.sandbox import SandboxAIRequest, SandboxAIResponse
from app.ai_detection.rubric import score_ai_likeness

@router.post(
    "/ai",
    response_model=SandboxAIResponse,
    summary="Analyze AI Likeness (Sandbox)",
    description="Run Internal AI Likeness Rubric on raw text without saving to database."
)
async def analyze_ai(request: SandboxAIRequest) -> SandboxAIResponse:
    """Run AI Likeness analysis on provided content."""
    try:
        # Run pure function
        result = score_ai_likeness(request.content)
        
        # Result is already a dict, Pydantic will validate it against SandboxAIResponse
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Analysis failed: {str(e)}"
        )
