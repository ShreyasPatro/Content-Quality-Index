"""AI-likeness rubric scoring package.

Public API:
    score_ai_likeness(text: str) -> dict

DO NOT import from internal.py directly.
"""

from app.ai_detection.rubric.scorer import score_ai_likeness

__all__ = ["score_ai_likeness"]
