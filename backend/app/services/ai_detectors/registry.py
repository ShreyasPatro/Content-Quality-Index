"""AI detector registry system.

This module provides a registry for organizing AI detector classes.
The registry is responsible ONLY for organization and metadata lookup,
NOT for detector execution or configuration management.

What this registry DOES:
- Register detector classes (not instances)
- Return active detector instances based on injected configuration
- Preserve deterministic execution order
- Provide detector metadata lookup (name, version)

What this registry does NOT do:
- Execute detectors (no detect() calls)
- Read environment variables or settings
- Access databases
- Make HTTP calls
- Manage Celery tasks
- Maintain global mutable state

Safe to import at startup.
"""

from typing import Dict, List, Optional, Type

from app.services.ai_detectors.base import AIDetector


# ============================================================================
# DETECTOR REGISTRY
# ============================================================================


class DetectorRegistry:
    """Registry for AI detector classes.

    This registry organizes detector classes and provides methods to
    instantiate active detectors based on injected configuration.

    The registry is deterministic: same configuration and registered
    detectors always produce the same output order.

    Example:
        >>> registry = DetectorRegistry()
        >>> registry.register("internal_rubric", InternalRubricDetector)
        >>> registry.register("external_vendor", ExternalDetector)
        >>>
        >>> # Get active detectors based on config
        >>> config = {"enabled_detectors": ["internal_rubric"]}
        >>> detectors = registry.get_active_detectors(config)
        >>> print([d.name for d in detectors])
        ['InternalRubric']
    """

    def __init__(self) -> None:
        """Initialize empty detector registry.

        The registry starts empty. Detector classes must be registered
        explicitly using register().
        """
        # Map of detector_id -> detector class
        # Using dict to preserve insertion order (Python 3.7+)
        self._detectors: Dict[str, Type[AIDetector]] = {}

    def register(self, detector_id: str, detector_class: Type[AIDetector]) -> None:
        """Register a detector class.

        Args:
            detector_id: Unique identifier for this detector (e.g., "internal_rubric")
            detector_class: Detector class (NOT instance) implementing AIDetector

        Raises:
            ValueError: If detector_id is already registered
            TypeError: If detector_class does not implement AIDetector

        Example:
            >>> registry.register("internal_rubric", InternalRubricDetector)
        """
        if detector_id in self._detectors:
            raise ValueError(
                f"Detector '{detector_id}' is already registered. "
                f"Use unregister() first if you want to replace it."
            )

        if not issubclass(detector_class, AIDetector):
            raise TypeError(
                f"Detector class must implement AIDetector interface, "
                f"got {detector_class}"
            )

        self._detectors[detector_id] = detector_class

    def unregister(self, detector_id: str) -> None:
        """Unregister a detector class.

        Args:
            detector_id: Identifier of detector to unregister

        Raises:
            KeyError: If detector_id is not registered

        Example:
            >>> registry.unregister("internal_rubric")
        """
        if detector_id not in self._detectors:
            raise KeyError(f"Detector '{detector_id}' is not registered")

        del self._detectors[detector_id]

    def is_registered(self, detector_id: str) -> bool:
        """Check if a detector is registered.

        Args:
            detector_id: Identifier to check

        Returns:
            bool: True if detector is registered, False otherwise

        Example:
            >>> registry.is_registered("internal_rubric")
            True
        """
        return detector_id in self._detectors

    def list_registered(self) -> List[str]:
        """List all registered detector IDs.

        Returns:
            List[str]: List of detector IDs in registration order

        Example:
            >>> registry.list_registered()
            ['internal_rubric', 'external_vendor']
        """
        return list(self._detectors.keys())

    def get_detector_class(self, detector_id: str) -> Type[AIDetector]:
        """Get a registered detector class.

        Args:
            detector_id: Identifier of detector to retrieve

        Returns:
            Type[AIDetector]: Detector class (NOT instance)

        Raises:
            KeyError: If detector_id is not registered

        Example:
            >>> detector_class = registry.get_detector_class("internal_rubric")
            >>> detector = detector_class()  # Instantiate manually
        """
        if detector_id not in self._detectors:
            raise KeyError(
                f"Detector '{detector_id}' is not registered. "
                f"Available detectors: {self.list_registered()}"
            )

        return self._detectors[detector_id]

    def get_active_detectors(
        self, config: Optional[Dict[str, List[str]]] = None
    ) -> List[AIDetector]:
        """Get active detector instances based on configuration.

        This method instantiates detectors based on the provided configuration.
        Configuration is INJECTED, not read from environment or settings.

        Args:
            config: Configuration dict with "enabled_detectors" key.
                   If None or empty, returns all registered detectors.
                   Example: {"enabled_detectors": ["internal_rubric", "external_vendor"]}

        Returns:
            List[AIDetector]: List of detector instances in deterministic order
                             (order matches enabled_detectors list or registration order)

        Raises:
            KeyError: If an enabled detector is not registered
            TypeError: If config format is invalid

        Example:
            >>> config = {"enabled_detectors": ["internal_rubric"]}
            >>> detectors = registry.get_active_detectors(config)
            >>> for detector in detectors:
            ...     result = detector.detect(text)
        """
        # If no config provided, return all detectors in registration order
        if config is None or not config:
            return [cls() for cls in self._detectors.values()]

        # Validate config format
        if not isinstance(config, dict):
            raise TypeError(
                f"Config must be a dict, got {type(config)}. "
                f"Expected format: {{'enabled_detectors': ['detector1', 'detector2']}}"
            )

        # Get enabled detector IDs from config
        enabled_ids = config.get("enabled_detectors", [])

        if not isinstance(enabled_ids, list):
            raise TypeError(
                f"enabled_detectors must be a list, got {type(enabled_ids)}"
            )

        # If no detectors enabled, return empty list
        if not enabled_ids:
            return []

        # Instantiate enabled detectors in config order (deterministic)
        detectors = []
        for detector_id in enabled_ids:
            if detector_id not in self._detectors:
                raise KeyError(
                    f"Detector '{detector_id}' is enabled in config but not registered. "
                    f"Available detectors: {self.list_registered()}"
                )

            detector_class = self._detectors[detector_id]
            detectors.append(detector_class())

        return detectors

    def get_metadata(self, detector_id: str) -> Dict[str, str]:
        """Get metadata for a registered detector.

        This instantiates the detector to access its name and version properties.

        Args:
            detector_id: Identifier of detector

        Returns:
            dict: Metadata with "name" and "version" keys

        Raises:
            KeyError: If detector_id is not registered

        Example:
            >>> metadata = registry.get_metadata("internal_rubric")
            >>> print(metadata)
            {'name': 'InternalRubric', 'version': '1.0.0'}
        """
        detector_class = self.get_detector_class(detector_id)
        detector = detector_class()

        return {
            "name": detector.name,
            "version": detector.version,
        }

    def get_all_metadata(self) -> Dict[str, Dict[str, str]]:
        """Get metadata for all registered detectors.

        Returns:
            dict: Map of detector_id -> metadata dict

        Example:
            >>> all_metadata = registry.get_all_metadata()
            >>> print(all_metadata)
            {
                'internal_rubric': {'name': 'InternalRubric', 'version': '1.0.0'},
                'external_vendor': {'name': 'ExternalVendor', 'version': '2.0'}
            }
        """
        return {
            detector_id: self.get_metadata(detector_id)
            for detector_id in self._detectors.keys()
        }


# ============================================================================
# GLOBAL REGISTRY INSTANCE (OPTIONAL)
# ============================================================================

# Global registry instance for convenience
# This is NOT mutable state - it's a singleton container
# Detectors must be registered explicitly at application startup
_global_registry: Optional[DetectorRegistry] = None


def get_global_registry() -> DetectorRegistry:
    """Get the global detector registry instance.

    This creates a singleton registry on first call.
    The registry itself is immutable, but detectors can be registered.

    Returns:
        DetectorRegistry: Global registry instance

    Example:
        >>> registry = get_global_registry()
        >>> registry.register("internal_rubric", InternalRubricDetector)
    """
    global _global_registry

    if _global_registry is None:
        _global_registry = DetectorRegistry()

    return _global_registry


def reset_global_registry() -> None:
    """Reset the global registry (for testing only).

    This clears the global registry singleton.
    Should ONLY be used in tests.

    Example:
        >>> # In test teardown
        >>> reset_global_registry()
    """
    global _global_registry
    _global_registry = None


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "DetectorRegistry",
    "get_global_registry",
    "reset_global_registry",
]
