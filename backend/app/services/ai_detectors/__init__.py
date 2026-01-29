"""AI detectors service package."""

from app.services.ai_detectors.base import (
    AIDetector,
    DetectorError,
    DetectorInvalidResponse,
    DetectorMetadata,
    DetectorResult,
    DetectorTimeout,
    DetectorUnavailable,
    validate_detector_result,
)

__all__ = [
    # Interface
    "AIDetector",
    # Result
    "DetectorResult",
    # Exceptions
    "DetectorError",
    "DetectorTimeout",
    "DetectorUnavailable",
    "DetectorInvalidResponse",
    # Types
    "DetectorMetadata",
    # Utilities
    "validate_detector_result",
]
