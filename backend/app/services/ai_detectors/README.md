# AI Detector Interface Documentation

## Overview

The AI detector interface provides a pluggable contract for integrating external AI detection services (e.g., GPTZero, Originality.ai) into the evaluation pipeline.

**Location**: `app/services/ai_detectors/base.py`

## Design Principles

1. **Pure Interface**: No vendor-specific code, HTTP calls, or side effects
2. **Advisory Signals**: Detectors are not authoritative, may fail gracefully
3. **Type Safety**: Strong typing with validation and invariants
4. **JSON Serializable**: All results can be stored in database

## Components

### DetectorResult

Canonical output format for all detectors.

```python
@dataclass
class DetectorResult:
    score: float                    # 0-100 (higher = more AI-like)
    confidence: Optional[float]     # 0-100 (higher = more confident)
    raw_metadata: Dict[str, Any]    # Detector-specific metadata
```

**Invariants** (enforced in `__post_init__`):
- `score` must be between 0 and 100
- `confidence` (if present) must be between 0 and 100
- Raises `ValueError` if violated

**Example**:
```python
result = DetectorResult(
    score=85.5,
    confidence=92.0,
    raw_metadata={
        "model_version": "3.0",
        "timestamp": "2026-01-29T11:50:22Z"
    }
)
```

### Typed Exceptions

```python
DetectorError              # Base exception
├── DetectorTimeout        # Request exceeded time limit
├── DetectorUnavailable    # Service is down/unreachable
└── DetectorInvalidResponse # Malformed response
```

**Usage**:
```python
try:
    result = detector.detect(text)
except DetectorTimeout:
    # Log and continue with other detectors
    pass
except DetectorUnavailable:
    # Mark detector as down, retry later
    pass
except DetectorInvalidResponse:
    # Log error, may indicate API version mismatch
    pass
```

### AIDetector Interface

Abstract base class defining the detector contract.

```python
class AIDetector(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable detector name"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Detector model or API version"""
        pass

    @abstractmethod
    def detect(self, text: str) -> DetectorResult:
        """Detect AI-generated content in text"""
        pass
```

## Implementation Example

```python
from app.services.ai_detectors import AIDetector, DetectorResult

class GPTZeroDetector(AIDetector):
    @property
    def name(self) -> str:
        return "GPTZero"

    @property
    def version(self) -> str:
        return "2.0"

    def detect(self, text: str) -> DetectorResult:
        # Call GPTZero API
        response = self._call_gptzero_api(text)
        
        return DetectorResult(
            score=response["ai_probability"] * 100,
            confidence=response["confidence"] * 100,
            raw_metadata={
                "model_version": response["model"],
                "processing_time_ms": response["time"]
            }
        )
```

## Integration with Evaluation Pipeline

```python
from app.services.ai_detectors import AIDetector, DetectorError
from app.models import ai_detector_scores

async def run_detector(
    detector: AIDetector,
    run_id: UUID,
    text: str
) -> None:
    """Run a single detector and store results."""
    try:
        result = detector.detect(text)
        
        # Store in database
        await conn.execute(
            ai_detector_scores.insert().values(
                run_id=run_id,
                provider=detector.name,
                score=result.score,
                details={
                    "model_version": detector.version,
                    "confidence": result.confidence,
                    "raw_metadata": result.raw_metadata
                }
            )
        )
    except DetectorError as e:
        # Log error and continue with other detectors
        logger.warning(f"{detector.name} failed: {e}")
```

## Validation

```python
from app.services.ai_detectors import validate_detector_result

# Automatic validation in __post_init__
result = DetectorResult(score=150.0, confidence=None, raw_metadata={})
# Raises: ValueError: DetectorResult.score must be between 0 and 100, got 150.0

# Manual validation
validate_detector_result(result)  # Additional type checks
```

## Safety Guarantees

✅ **No Side Effects**: Pure type definitions only  
✅ **No HTTP Calls**: Interface only, implementations handle I/O  
✅ **No Environment Variables**: No configuration in base module  
✅ **No Database Access**: Results are passed to caller for storage  
✅ **No Logging**: Implementations handle logging  
✅ **Safe to Import**: Can be imported in any environment  

## File Structure

```
app/services/ai_detectors/
├── __init__.py       # Package exports
├── base.py           # Interface and types (THIS FILE)
├── example.py        # Usage examples
├── gptzero.py        # Future: GPTZero implementation
└── originality.py    # Future: Originality.ai implementation
```

## API Reference

### Exports

```python
from app.services.ai_detectors import (
    # Interface
    AIDetector,
    
    # Result
    DetectorResult,
    
    # Exceptions
    DetectorError,
    DetectorTimeout,
    DetectorUnavailable,
    DetectorInvalidResponse,
    
    # Types
    DetectorMetadata,
    
    # Utilities
    validate_detector_result,
)
```

### DetectorResult Methods

- `to_dict() -> Dict[str, Any]`: Convert to JSON-serializable dict

### Utility Functions

- `validate_detector_result(result: DetectorResult) -> None`: Validate result

## Testing

```python
from app.services.ai_detectors import DetectorResult

# Test score validation
def test_score_validation():
    # Valid
    result = DetectorResult(score=50.0, confidence=None, raw_metadata={})
    assert result.score == 50.0
    
    # Invalid (too high)
    with pytest.raises(ValueError):
        DetectorResult(score=150.0, confidence=None, raw_metadata={})
    
    # Invalid (negative)
    with pytest.raises(ValueError):
        DetectorResult(score=-10.0, confidence=None, raw_metadata={})

# Test confidence validation
def test_confidence_validation():
    # Valid (None)
    result = DetectorResult(score=50.0, confidence=None, raw_metadata={})
    assert result.confidence is None
    
    # Valid (in range)
    result = DetectorResult(score=50.0, confidence=75.0, raw_metadata={})
    assert result.confidence == 75.0
    
    # Invalid
    with pytest.raises(ValueError):
        DetectorResult(score=50.0, confidence=150.0, raw_metadata={})
```

## Future Implementations

### GPTZero Detector
- API endpoint: `https://api.gptzero.me/v2/predict/text`
- Authentication: API key in headers
- Rate limits: 100 requests/minute

### Originality.ai Detector
- API endpoint: `https://api.originality.ai/api/v1/scan/ai`
- Authentication: API key in headers
- Rate limits: 50 requests/minute

### Internal Rubric Detector
- Already implemented: `app/ai_detection/rubric/scorer.py`
- Wraps `score_ai_likeness()` in `AIDetector` interface
- No external API calls, fully deterministic

## Changelog

### v1.0.0 (2026-01-29)

**Initial Release**:
- ✅ `DetectorResult` dataclass with validation
- ✅ Typed exception hierarchy
- ✅ `AIDetector` abstract base class
- ✅ `validate_detector_result()` utility
- ✅ Comprehensive documentation and examples
- ✅ Zero side effects, safe to import anywhere
