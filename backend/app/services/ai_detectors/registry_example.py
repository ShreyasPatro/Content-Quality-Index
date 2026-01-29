"""Example usage of the detector registry system."""

from app.services.ai_detectors import AIDetector, DetectorResult
from app.services.ai_detectors.registry import DetectorRegistry, get_global_registry


# ============================================================================
# EXAMPLE DETECTOR IMPLEMENTATIONS
# ============================================================================


class InternalRubricDetector(AIDetector):
    """Example internal rubric detector."""

    @property
    def name(self) -> str:
        return "InternalRubric"

    @property
    def version(self) -> str:
        return "1.0.0"

    def detect(self, text: str) -> DetectorResult:
        """Detect using internal rubric."""
        # In real implementation, this would call the rubric scorer
        return DetectorResult(
            score=45.0,
            confidence=None,
            raw_metadata={"detector_type": "internal_rubric"},
        )


class ExternalVendorDetector(AIDetector):
    """Example external vendor detector."""

    @property
    def name(self) -> str:
        return "ExternalVendor"

    @property
    def version(self) -> str:
        return "2.0"

    def detect(self, text: str) -> DetectorResult:
        """Detect using external vendor API."""
        # In real implementation, this would call external API
        return DetectorResult(
            score=75.0,
            confidence=85.0,
            raw_metadata={"detector_type": "external_vendor"},
        )


class ThirdPartyDetector(AIDetector):
    """Example third-party detector."""

    @property
    def name(self) -> str:
        return "ThirdPartyDetector"

    @property
    def version(self) -> str:
        return "3.1.4"

    def detect(self, text: str) -> DetectorResult:
        """Detect using third-party service."""
        return DetectorResult(
            score=60.0,
            confidence=90.0,
            raw_metadata={"detector_type": "third_party"},
        )


# ============================================================================
# EXAMPLE 1: BASIC REGISTRY USAGE
# ============================================================================


def example_basic_usage():
    """Demonstrate basic registry usage."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Registry Usage")
    print("=" * 80)

    # Create registry
    registry = DetectorRegistry()

    # Register detectors
    registry.register("internal_rubric", InternalRubricDetector)
    registry.register("external_vendor", ExternalVendorDetector)
    registry.register("third_party", ThirdPartyDetector)

    # List registered detectors
    print(f"\nRegistered detectors: {registry.list_registered()}")

    # Check if detector is registered
    print(f"Is 'internal_rubric' registered? {registry.is_registered('internal_rubric')}")
    print(f"Is 'unknown' registered? {registry.is_registered('unknown')}")


# ============================================================================
# EXAMPLE 2: CONFIGURATION-BASED ACTIVATION
# ============================================================================


def example_configuration():
    """Demonstrate configuration-based detector activation."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Configuration-Based Activation")
    print("=" * 80)

    registry = DetectorRegistry()
    registry.register("internal_rubric", InternalRubricDetector)
    registry.register("external_vendor", ExternalVendorDetector)
    registry.register("third_party", ThirdPartyDetector)

    # Config 1: Enable only internal rubric
    config1 = {"enabled_detectors": ["internal_rubric"]}
    detectors1 = registry.get_active_detectors(config1)
    print(f"\nConfig 1 - Enabled: {config1['enabled_detectors']}")
    print(f"Active detectors: {[d.name for d in detectors1]}")

    # Config 2: Enable multiple detectors
    config2 = {"enabled_detectors": ["internal_rubric", "external_vendor"]}
    detectors2 = registry.get_active_detectors(config2)
    print(f"\nConfig 2 - Enabled: {config2['enabled_detectors']}")
    print(f"Active detectors: {[d.name for d in detectors2]}")

    # Config 3: Enable all detectors
    config3 = {
        "enabled_detectors": ["internal_rubric", "external_vendor", "third_party"]
    }
    detectors3 = registry.get_active_detectors(config3)
    print(f"\nConfig 3 - Enabled: {config3['enabled_detectors']}")
    print(f"Active detectors: {[d.name for d in detectors3]}")

    # Config 4: No config (returns all)
    detectors4 = registry.get_active_detectors(None)
    print(f"\nConfig 4 - No config (returns all)")
    print(f"Active detectors: {[d.name for d in detectors4]}")


# ============================================================================
# EXAMPLE 3: METADATA LOOKUP
# ============================================================================


def example_metadata():
    """Demonstrate metadata lookup."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Metadata Lookup")
    print("=" * 80)

    registry = DetectorRegistry()
    registry.register("internal_rubric", InternalRubricDetector)
    registry.register("external_vendor", ExternalVendorDetector)

    # Get metadata for single detector
    metadata = registry.get_metadata("internal_rubric")
    print(f"\nMetadata for 'internal_rubric': {metadata}")

    # Get metadata for all detectors
    all_metadata = registry.get_all_metadata()
    print(f"\nAll metadata:")
    for detector_id, meta in all_metadata.items():
        print(f"  {detector_id}: {meta}")


# ============================================================================
# EXAMPLE 4: DETERMINISTIC ORDERING
# ============================================================================


def example_deterministic_ordering():
    """Demonstrate deterministic ordering."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Deterministic Ordering")
    print("=" * 80)

    registry = DetectorRegistry()
    registry.register("detector_a", InternalRubricDetector)
    registry.register("detector_b", ExternalVendorDetector)
    registry.register("detector_c", ThirdPartyDetector)

    # Order matches config order (deterministic)
    config = {"enabled_detectors": ["detector_c", "detector_a", "detector_b"]}
    detectors = registry.get_active_detectors(config)

    print(f"\nConfig order: {config['enabled_detectors']}")
    print(f"Detector order: {[d.name for d in detectors]}")
    print("✓ Order matches config (deterministic)")


# ============================================================================
# EXAMPLE 5: GLOBAL REGISTRY
# ============================================================================


def example_global_registry():
    """Demonstrate global registry usage."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Global Registry")
    print("=" * 80)

    # Get global registry (singleton)
    registry = get_global_registry()

    # Register detectors globally
    registry.register("internal_rubric", InternalRubricDetector)
    registry.register("external_vendor", ExternalVendorDetector)

    # Access from anywhere in application
    registry2 = get_global_registry()
    print(f"\nSame registry instance? {registry is registry2}")
    print(f"Registered detectors: {registry2.list_registered()}")


# ============================================================================
# EXAMPLE 6: ERROR HANDLING
# ============================================================================


def example_error_handling():
    """Demonstrate error handling."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Error Handling")
    print("=" * 80)

    registry = DetectorRegistry()
    registry.register("internal_rubric", InternalRubricDetector)

    # Try to register duplicate
    print("\nTrying to register duplicate detector...")
    try:
        registry.register("internal_rubric", ExternalVendorDetector)
    except ValueError as e:
        print(f"✓ Caught error: {e}")

    # Try to get unregistered detector
    print("\nTrying to get unregistered detector...")
    try:
        registry.get_detector_class("unknown")
    except KeyError as e:
        print(f"✓ Caught error: {e}")

    # Try to enable unregistered detector
    print("\nTrying to enable unregistered detector...")
    try:
        config = {"enabled_detectors": ["unknown"]}
        registry.get_active_detectors(config)
    except KeyError as e:
        print(f"✓ Caught error: {e}")


# ============================================================================
# EXAMPLE 7: INTEGRATION PATTERN
# ============================================================================


def example_integration():
    """Demonstrate integration with evaluation pipeline."""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Integration Pattern")
    print("=" * 80)

    # Setup registry at application startup
    registry = DetectorRegistry()
    registry.register("internal_rubric", InternalRubricDetector)
    registry.register("external_vendor", ExternalVendorDetector)

    # In evaluation workflow, get active detectors from config
    config = {"enabled_detectors": ["internal_rubric", "external_vendor"]}
    detectors = registry.get_active_detectors(config)

    # Run detectors
    text = "Sample text to analyze..."
    print(f"\nAnalyzing text: '{text}'")

    results = []
    for detector in detectors:
        print(f"\nRunning {detector.name} v{detector.version}...")
        result = detector.detect(text)
        results.append(
            {
                "detector": detector.name,
                "version": detector.version,
                "score": result.score,
                "confidence": result.confidence,
            }
        )

    print(f"\nResults:")
    for r in results:
        print(f"  {r['detector']} v{r['version']}: score={r['score']}")


# ============================================================================
# RUN EXAMPLES
# ============================================================================


if __name__ == "__main__":
    example_basic_usage()
    example_configuration()
    example_metadata()
    example_deterministic_ordering()
    example_global_registry()
    example_error_handling()
    example_integration()

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)
