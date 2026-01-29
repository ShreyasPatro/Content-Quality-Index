"""Public API for AI-likeness rubric scoring.

This module exposes the ONLY public function for rubric scoring.
All internal implementation is in internal.py.

Public API:
    score_ai_likeness(text: str) -> dict
"""

from datetime import datetime, timezone

from app.ai_detection.rubric.internal import RUBRIC_VERSION, score_text_internal

__all__ = ["score_ai_likeness"]


def score_ai_likeness(text: str) -> dict:
    """Score text for AI-likeness using deterministic rubric.

    This is the ONLY public function in the rubric scoring API.
    Returns a database-compatible dict that can be stored directly
    in ai_detector_scores.details JSONB column.

    Args:
        text: Input text to analyze (minimum 5 words)

    Returns:
        dict: Database-compatible result with structure:
            {
                "model_version": "rubric_v1.0.0",
                "timestamp": "2026-01-29T11:34:56.123456+00:00",
                "score": 45.5,
                "raw_response": {
                    "rubric_version": "1.0.0",
                    "total_score": 45.5,
                    "subscores": {
                        "predictability_entropy": {...},
                        "sentence_uniformity": {...},
                        "generic_language": {...},
                        "structural_templates": {...},
                        "lack_of_friction": {...},
                        "over_polish": {...}
                    },
                    "metadata": {
                        "text_length": 1234,
                        "word_count": 234
                    }
                }
            }

    Raises:
        ValueError: If text is empty, too short (< 5 words), or scoring error

    Determinism Guarantee:
        - Same input text → Same output (always)
        - No randomness, no external dependencies
        - Only timestamp varies between calls
    """
    # Call internal scoring engine
    result = score_text_internal(text)

    # Build database-compatible output
    return {
        # Required by ai_detector_scores.details schema
        "model_version": f"rubric_v{RUBRIC_VERSION}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "score": result.total_score,  # Top-level for convenience
        # Full rubric output
        "raw_response": {
            "rubric_version": result.rubric_version,
            "total_score": result.total_score,
            "subscores": {
                "predictability_entropy": {
                    "score": result.predictability_entropy["score"],
                    "max_score": result.predictability_entropy["max_score"],
                    "percentage": result.predictability_entropy["percentage"],
                    "explanation": result.predictability_entropy["explanation"],
                    "evidence": result.predictability_entropy["evidence"],
                },
                "sentence_uniformity": {
                    "score": result.sentence_uniformity["score"],
                    "max_score": result.sentence_uniformity["max_score"],
                    "percentage": result.sentence_uniformity["percentage"],
                    "explanation": result.sentence_uniformity["explanation"],
                    "evidence": result.sentence_uniformity["evidence"],
                },
                "generic_language": {
                    "score": result.generic_language["score"],
                    "max_score": result.generic_language["max_score"],
                    "percentage": result.generic_language["percentage"],
                    "explanation": result.generic_language["explanation"],
                    "evidence": result.generic_language["evidence"],
                },
                "structural_templates": {
                    "score": result.structural_templates["score"],
                    "max_score": result.structural_templates["max_score"],
                    "percentage": result.structural_templates["percentage"],
                    "explanation": result.structural_templates["explanation"],
                    "evidence": result.structural_templates["evidence"],
                },
                "lack_of_friction": {
                    "score": result.lack_of_friction["score"],
                    "max_score": result.lack_of_friction["max_score"],
                    "percentage": result.lack_of_friction["percentage"],
                    "explanation": result.lack_of_friction["explanation"],
                    "evidence": result.lack_of_friction["evidence"],
                },
                "over_polish": {
                    "score": result.over_polish["score"],
                    "max_score": result.over_polish["max_score"],
                    "percentage": result.over_polish["percentage"],
                    "explanation": result.over_polish["explanation"],
                    "evidence": result.over_polish["evidence"],
                },
            },
            "metadata": {
                "text_length": result.text_length,
                "word_count": result.word_count,
            },
        },
    }
