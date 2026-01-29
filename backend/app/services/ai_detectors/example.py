"""Example implementations and usage of the AI detector interface."""

from app.services.ai_detectors import (
    AIDetector,
    DetectorError,
    DetectorInvalidResponse,
    DetectorResult,
    DetectorTimeout,
    DetectorUnavailable,
)


# ============================================================================
# EXAMPLE 1: MOCK DETECTOR (FOR TESTING)
# ============================================================================


class MockDetector(AIDetector):
    """Mock detector for testing purposes.

    Always returns a fixed score. Useful for testing the evaluation pipeline
    without making external API calls.
    """

    def __init__(self, fixed_score: float = 50.0):
        """Initialize mock detector.

        Args:
            fixed_score: Score to always return (0-100)
        """
        self._fixed_score = fixed_score

    @property
    def name(self) -> str:
        return "MockDetector"

    @property
    def version(self) -> str:
        return "1.0.0"

    def detect(self, text: str) -> DetectorResult:
        """Return fixed score for any text.

        Args:
            text: Input text (ignored)

        Returns:
            DetectorResult with fixed score
        """
        return DetectorResult(
            score=self._fixed_score,
            confidence=100.0,
            raw_metadata={
                "detector_type": "mock",
                "text_length": len(text),
            },
        )


# ============================================================================
# EXAMPLE 2: SIMULATED EXTERNAL DETECTOR
# ============================================================================


class SimulatedExternalDetector(AIDetector):
    """Simulated external detector that demonstrates error handling.

    This detector simulates various failure modes:
    - Timeout (if text is very long)
    - Unavailable (if text contains "offline")
    - Invalid response (if text contains "corrupt")
    """

    @property
    def name(self) -> str:
        return "SimulatedExternal"

    @property
    def version(self) -> str:
        return "2.5.1"

    def detect(self, text: str) -> DetectorResult:
        """Simulate external detector with various failure modes.

        Args:
            text: Input text

        Returns:
            DetectorResult with simulated score

        Raises:
            DetectorTimeout: If text is very long (> 10000 chars)
            DetectorUnavailable: If text contains "offline"
            DetectorInvalidResponse: If text contains "corrupt"
        """
        # Simulate timeout for very long text
        if len(text) > 10000:
            raise DetectorTimeout(
                f"Detector timed out processing {len(text)} characters"
            )

        # Simulate service unavailable
        if "offline" in text.lower():
            raise DetectorUnavailable("Detector service is currently offline")

        # Simulate invalid response
        if "corrupt" in text.lower():
            raise DetectorInvalidResponse("Detector returned malformed JSON")

        # Normal operation: simple heuristic based on text length
        # (This is just for demonstration - real detectors use ML models)
        score = min(100.0, len(text) / 10)

        return DetectorResult(
            score=score,
            confidence=75.0,
            raw_metadata={
                "api_version": "2.5.1",
                "processing_time_ms": 150,
                "model": "simulated-v2",
            },
        )


# ============================================================================
# EXAMPLE 3: USAGE PATTERNS
# ============================================================================


def example_basic_usage():
    """Demonstrate basic detector usage."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 80)

    detector = MockDetector(fixed_score=85.5)

    text = "This is sample text to analyze."
    result = detector.detect(text)

    print(f"\nDetector: {detector.name} v{detector.version}")
    print(f"Score: {result.score:.1f}/100")
    print(f"Confidence: {result.confidence:.1f}%")
    print(f"Metadata: {result.raw_metadata}")
    print(f"\nAs dict: {result.to_dict()}")


def example_error_handling():
    """Demonstrate error handling."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Error Handling")
    print("=" * 80)

    detector = SimulatedExternalDetector()

    test_cases = [
        ("Normal text", "This is normal text."),
        ("Timeout trigger", "x" * 15000),
        ("Unavailable trigger", "The service is offline."),
        ("Invalid response trigger", "This response is corrupt."),
    ]

    for description, text in test_cases:
        print(f"\n{description}:")
        try:
            result = detector.detect(text)
            print(f"  ✓ Success: score={result.score:.1f}")
        except DetectorTimeout as e:
            print(f"  ⏱ Timeout: {e}")
        except DetectorUnavailable as e:
            print(f"  ⚠ Unavailable: {e}")
        except DetectorInvalidResponse as e:
            print(f"  ✗ Invalid: {e}")
        except DetectorError as e:
            print(f"  ✗ Error: {e}")


def example_validation():
    """Demonstrate result validation."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Result Validation")
    print("=" * 80)

    # Valid result
    print("\nValid result:")
    try:
        result = DetectorResult(
            score=85.5, confidence=92.0, raw_metadata={"model": "v1"}
        )
        print(f"  ✓ Created: score={result.score}")
    except ValueError as e:
        print(f"  ✗ Error: {e}")

    # Invalid score (too high)
    print("\nInvalid score (> 100):")
    try:
        result = DetectorResult(
            score=150.0, confidence=None, raw_metadata={}
        )
        print(f"  ✓ Created: score={result.score}")
    except ValueError as e:
        print(f"  ✗ Error: {e}")

    # Invalid confidence (negative)
    print("\nInvalid confidence (< 0):")
    try:
        result = DetectorResult(
            score=50.0, confidence=-10.0, raw_metadata={}
        )
        print(f"  ✓ Created: confidence={result.confidence}")
    except ValueError as e:
        print(f"  ✗ Error: {e}")


def example_integration_pattern():
    """Demonstrate integration with evaluation pipeline."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Integration Pattern")
    print("=" * 80)

    detectors = [
        MockDetector(fixed_score=85.0),
        SimulatedExternalDetector(),
    ]

    text = "Sample text for evaluation."

    print(f"\nEvaluating text: '{text}'\n")

    results = []
    for detector in detectors:
        print(f"Running {detector.name} v{detector.version}...")
        try:
            result = detector.detect(text)
            results.append(
                {
                    "provider": detector.name,
                    "score": result.score,
                    "confidence": result.confidence,
                    "metadata": result.raw_metadata,
                }
            )
            print(f"  ✓ Score: {result.score:.1f}")
        except DetectorError as e:
            print(f"  ✗ Failed: {e}")
            # Continue with other detectors
            continue

    print(f"\nCollected {len(results)} results:")
    for r in results:
        print(f"  - {r['provider']}: {r['score']:.1f}")


# ============================================================================
# RUN EXAMPLES
# ============================================================================


if __name__ == "__main__":
    example_basic_usage()
    example_error_handling()
    example_validation()
    example_integration_pattern()

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)
