"""AI detector interface and type definitions.

This module defines the contract for pluggable AI detectors.
It contains ONLY type definitions, exceptions, and abstract interfaces.

NO vendor-specific code, HTTP calls, or side effects are allowed.
Safe to import in any environment.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


# ============================================================================
# DETECTOR EXCEPTIONS
# ============================================================================


class DetectorError(Exception):
    """Base exception for all detector errors.

    All detector implementations should raise subclasses of this exception
    to allow uniform error handling in the evaluation pipeline.
    """

    pass


class DetectorTimeout(DetectorError):
    """Detector request exceeded time limit.

    Raised when a detector takes too long to respond.
    The evaluation pipeline should handle this gracefully and continue
    with other detectors.
    """

    pass


class DetectorUnavailable(DetectorError):
    """Detector service is unavailable.

    Raised when a detector cannot be reached (network error, service down, etc.).
    This is a transient error - the detector may be available later.
    """

    pass


class DetectorInvalidResponse(DetectorError):
    """Detector returned an invalid or malformed response.

    Raised when a detector returns data that cannot be parsed or validated.
    This may indicate an API version mismatch or detector bug.
    """

    pass


# ============================================================================
# DETECTOR RESULT
# ============================================================================


@dataclass
class DetectorResult:
    """Result from an AI detector.

    This is the canonical output format for all detectors.
    All fields must be JSON-serializable for storage in database.

    Attributes:
        score: AI-likeness score (0-100, higher = more AI-like)
        confidence: Optional confidence level (0-100, higher = more confident)
        raw_metadata: Detector-specific metadata (model version, timestamps, etc.)

    Invariants:
        - score must be between 0 and 100 (inclusive)
        - confidence (if present) must be between 0 and 100 (inclusive)
        - raw_metadata must be JSON-serializable

    Example:
        >>> result = DetectorResult(
        ...     score=85.5,
        ...     confidence=92.0,
        ...     raw_metadata={
        ...         "model_version": "3.0",
        ...         "timestamp": "2026-01-29T11:50:22Z",
        ...         "detected_patterns": ["generic_language", "uniform_sentences"]
        ...     }
        ... )
    """

    score: float
    confidence: Optional[float]
    raw_metadata: Dict[str, Any]

    def __post_init__(self) -> None:
        """Validate invariants after initialization.

        Raises:
            ValueError: If score or confidence are out of valid range
        """
        # Validate score
        if not (0.0 <= self.score <= 100.0):
            raise ValueError(
                f"DetectorResult.score must be between 0 and 100, got {self.score}"
            )

        # Validate confidence (if present)
        if self.confidence is not None:
            if not (0.0 <= self.confidence <= 100.0):
                raise ValueError(
                    f"DetectorResult.confidence must be between 0 and 100, got {self.confidence}"
                )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary.

        Returns:
            dict: Dictionary representation suitable for database storage
        """
        return {
            "score": self.score,
            "confidence": self.confidence,
            "raw_metadata": self.raw_metadata,
        }


# ============================================================================
# DETECTOR INTERFACE
# ============================================================================


class AIDetector(ABC):
    """Abstract base class for AI content detectors.

    All detector implementations must inherit from this class and implement
    the required abstract methods.

    Detectors are advisory signals, not authoritative. They may be:
    - Unavailable (service down)
    - Slow (timeout)
    - Unreliable (inconsistent results)

    The evaluation pipeline must handle detector failures gracefully.

    Example Implementation:
        >>> class ExternalDetector(AIDetector):
        ...     @property
        ...     def name(self) -> str:
        ...         return "ExternalVendor"
        ...
        ...     @property
        ...     def version(self) -> str:
        ...         return "2.0"
        ...
        ...     def detect(self, text: str) -> DetectorResult:
        ...         # Call external detector API
        ...         response = self._call_api(text)
        ...         return DetectorResult(
        ...             score=response["ai_probability"] * 100,
        ...             confidence=response["confidence"] * 100,
        ...             raw_metadata={"model": response["model_version"]}
        ...         )
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable detector name.

        Returns:
            str: Detector name (e.g., "ExternalVendor", "ThirdPartyDetector", "InternalRubric")

        Example:
            >>> detector.name
            'ExternalVendor'
        """
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Detector model or API version.

        This should be the version of the underlying model or API,
        not the version of the integration code.

        Used for drift tracking and debugging.

        Returns:
            str: Version string (e.g., "2.0", "v3.1.4", "gpt-4-turbo")

        Example:
            >>> detector.version
            '2.0'
        """
        pass

    @abstractmethod
    def detect(self, text: str) -> DetectorResult:
        """Detect AI-generated content in text.

        This is a pure function with no side effects beyond the detector API call.
        Implementations should:
        - Call external detector API (if applicable)
        - Parse and validate response
        - Return DetectorResult with score and metadata

        Args:
            text: Input text to analyze

        Returns:
            DetectorResult: Detection result with score and metadata

        Raises:
            DetectorTimeout: If detector takes too long to respond
            DetectorUnavailable: If detector service is unreachable
            DetectorInvalidResponse: If detector returns invalid data
            DetectorError: For any other detector-specific errors

        Example:
            >>> result = detector.detect("This is sample text...")
            >>> print(f"AI-likeness: {result.score:.1f}%")
            AI-likeness: 85.5%
        """
        pass


# ============================================================================
# TYPE ALIASES
# ============================================================================

# Type alias for detector metadata dictionaries
DetectorMetadata = Dict[str, Any]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def validate_detector_result(result: DetectorResult) -> None:
    """Validate a detector result for correctness.

    This is a convenience function for testing and validation.
    The DetectorResult.__post_init__ already validates invariants,
    but this function can be used for additional checks.

    Args:
        result: DetectorResult to validate

    Raises:
        ValueError: If result violates invariants
        TypeError: If result has wrong types

    Example:
        >>> result = DetectorResult(score=85.5, confidence=92.0, raw_metadata={})
        >>> validate_detector_result(result)  # No error
        >>> bad_result = DetectorResult(score=150.0, confidence=None, raw_metadata={})
        Traceback (most recent call last):
            ...
        ValueError: DetectorResult.score must be between 0 and 100, got 150.0
    """
    # Type checks
    if not isinstance(result.score, (int, float)):
        raise TypeError(f"score must be numeric, got {type(result.score)}")

    if result.confidence is not None and not isinstance(
        result.confidence, (int, float)
    ):
        raise TypeError(
            f"confidence must be numeric or None, got {type(result.confidence)}"
        )

    if not isinstance(result.raw_metadata, dict):
        raise TypeError(
            f"raw_metadata must be dict, got {type(result.raw_metadata)}"
        )

    # Invariants are already checked in __post_init__
    # This function is primarily for type checking


# ============================================================================
# DOCUMENTATION
# ============================================================================

__all__ = [
    # Exceptions
    "DetectorError",
    "DetectorTimeout",
    "DetectorUnavailable",
    "DetectorInvalidResponse",
    # Data structures
    "DetectorResult",
    # Interfaces
    "AIDetector",
    # Type aliases
    "DetectorMetadata",
    # Utilities
    "validate_detector_result",
]
