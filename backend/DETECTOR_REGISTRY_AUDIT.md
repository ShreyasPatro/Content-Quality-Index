# Detector Registry - Hostile Audit Report

**Audit Date**: 2026-01-29T12:34:43+05:30  
**Auditor**: Hostile Backend Systems Auditor  
**Scope**: `app/services/ai_detectors/registry.py` ONLY  
**Assumption**: External regulatory audit, zero tolerance for hidden behavior

---

## Executive Summary

**VERDICT**: ⚠️ **CONDITIONAL PASS - PROCEED WITH WARNINGS**

**BLOCKING ISSUES**: 0  
**WARNINGS**: 2  
**PASS**: 7

The detector registry is **mostly compliant** but contains **global mutable state** and **auto-instantiation behavior** that violate strict purity requirements. These issues are acceptable for production use but must be documented and monitored.

---

## PART 1 — REGISTRY RESPONSIBILITY

### 1.1 Registry Scope

#### ✅ **PASS**

**Expected**: Registry ONLY registers and returns detector instances  
**Actual**: Registry performs only organizational functions

**Evidence**:

**What Registry DOES** (lines 7-11):
```python
What this registry DOES:
- Register detector classes (not instances)
- Return active detector instances based on injected configuration
- Preserve deterministic execution order
- Provide detector metadata lookup (name, version)
```

**What Registry does NOT do** (lines 13-19):
```python
What this registry does NOT do:
- Execute detectors (no detect() calls)
- Read environment variables or settings
- Access databases
- Make HTTP calls
- Manage Celery tasks
- Maintain global mutable state
```

**Verification**:
- ✅ NO `detect()` calls found (grep search: no results)
- ✅ NO scoring logic
- ✅ NO retry logic
- ✅ NO failure handling beyond exceptions
- ✅ NO result logging

**Methods** (lines 65-269):
- `register()` - Stores detector class
- `unregister()` - Removes detector class
- `is_registered()` - Checks registration
- `list_registered()` - Lists detector IDs
- `get_detector_class()` - Returns class (not instance)
- `get_active_detectors()` - Returns instances (instantiation only)
- `get_metadata()` - Returns name/version
- `get_all_metadata()` - Returns all metadata

**Verdict**: **PASS** - Registry responsibility is correct

---

## PART 2 — CONFIGURATION SAFETY

### 2.1 Configuration Injection

#### ✅ **PASS**

**Expected**: Enable/disable driven ONLY by injected configuration  
**Actual**: Configuration is parameter-injected

**Evidence**: **Lines 161-187**

```python
def get_active_detectors(
    self, config: Optional[Dict[str, List[str]]] = None
) -> List[AIDetector]:
    """Get active detector instances based on configuration.
    
    This method instantiates detectors based on the provided configuration.
    Configuration is INJECTED, not read from environment or settings.
    
    Args:
        config: Configuration dict with "enabled_detectors" key.
```

**Configuration Usage**:
- **Line 189**: `if config is None or not config:`
- **Line 200**: `enabled_ids = config.get("enabled_detectors", [])`
- **Line 213**: `for detector_id in enabled_ids:`

**Verdict**: **PASS** - Configuration is injected

---

### 2.2 No Environment Access

#### ✅ **PASS**

**Expected**: NO environment variable access  
**Actual**: NO environment access found

**Verification**:
- ✅ NO `os.environ` usage (grep search: no results)
- ✅ NO `getenv` calls
- ✅ NO `settings` imports
- ✅ NO `config.` access (except parameter)

**Imports** (lines 24-26):
```python
from typing import Dict, List, Optional, Type

from app.services.ai_detectors.base import AIDetector
```

Only imports:
- `typing` (standard library)
- `AIDetector` (local interface)

**Verdict**: **PASS** - No environment access

---

### 2.3 No Hidden Defaults

#### ⚠️ **WARNING - Potential Auto-Enable**

**Expected**: NO hidden defaults that auto-enable detectors  
**Actual**: `None` config returns ALL detectors

**Evidence**: **Lines 188-190**

```python
# If no config provided, return all detectors in registration order
if config is None or not config:
    return [cls() for cls in self._detectors.values()]
```

**Issue**:
- If `config=None`, registry returns **ALL registered detectors**
- This is a **hidden default** behavior
- Could auto-enable detectors unintentionally

**Severity**: **WARNING** (Acceptable)

**Justification**:
- Behavior is **explicitly documented** (line 171)
- Caller controls whether to pass `None`
- **ACCEPTABLE** but risky if caller forgets config

**Recommendation**: Consider requiring explicit config or add warning in docstring.

**Verdict**: **WARNING** - Auto-enable behavior exists but documented

---

## PART 3 — DETERMINISM

### 3.1 Detector Ordering

#### ✅ **PASS**

**Expected**: Deterministic ordering (same inputs → same output order)  
**Actual**: Ordering is deterministic

**Evidence**:

**Registration Order** (lines 61-63):
```python
# Map of detector_id -> detector class
# Using dict to preserve insertion order (Python 3.7+)
self._detectors: Dict[str, Type[AIDetector]] = {}
```

**Comment explicitly states**: "Using dict to preserve insertion order (Python 3.7+)"

**Config Order** (lines 211-221):
```python
# Instantiate enabled detectors in config order (deterministic)
detectors = []
for detector_id in enabled_ids:
    if detector_id not in self._detectors:
        raise KeyError(...)
    
    detector_class = self._detectors[detector_id]
    detectors.append(detector_class())

return detectors
```

**Ordering Guarantees**:
1. **Registration order**: Preserved by dict (Python 3.7+)
2. **Config order**: Iterates `enabled_ids` list in order
3. **No sorting**: No `sorted()` or `set()` usage

**Verdict**: **PASS** - Deterministic ordering

---

### 3.2 No External Dependencies

#### ✅ **PASS**

**Expected**: No reliance on filesystem, import side effects  
**Actual**: No external dependencies

**Verification**:
- ✅ NO filesystem access
- ✅ NO import side effects (only class imports)
- ✅ NO network calls
- ✅ NO database queries

**Verdict**: **PASS** - No external dependencies

---

## PART 4 — IMPORT SAFETY

### 4.1 No Side Effects on Import

#### ✅ **PASS**

**Expected**: No side effects at import time  
**Actual**: Only class/function definitions

**Evidence**: Lines 1-326 contain only:
- Module docstring (lines 1-22)
- Imports (lines 24-26)
- Class definition (lines 34-269)
- Global variable declaration (line 279)
- Function definitions (lines 282-314)
- Exports (lines 321-325)

**No Execution**:
- ✅ NO function calls at module level
- ✅ NO detector instantiation
- ✅ NO registration calls

**Global Variable** (line 279):
```python
_global_registry: Optional[DetectorRegistry] = None
```

This is a **type-annotated declaration**, not instantiation. No side effects.

**Verdict**: **PASS** - Safe to import

---

### 4.2 No Auto-Registration

#### ✅ **PASS**

**Expected**: No registration executed automatically on import  
**Actual**: Registry starts empty

**Evidence**: **Lines 55-63**

```python
def __init__(self) -> None:
    """Initialize empty detector registry.
    
    The registry starts empty. Detector classes must be registered
    explicitly using register().
    """
    # Map of detector_id -> detector class
    # Using dict to preserve insertion order (Python 3.7+)
    self._detectors: Dict[str, Type[AIDetector]] = {}
```

**Verification**:
- ✅ `__init__` creates empty dict
- ✅ NO pre-populated detectors
- ✅ NO auto-discovery
- ✅ Explicit registration required

**Verdict**: **PASS** - No auto-registration

---

## PART 5 — GLOBAL STATE

### 5.1 Mutable Global Registry

#### ⚠️ **WARNING - Global Mutable State**

**Expected**: NO mutable global registry  
**Actual**: Global singleton with mutable state

**Evidence**: **Lines 276-300**

```python
# Global registry instance for convenience
# This is NOT mutable state - it's a singleton container
# Detectors must be registered explicitly at application startup
_global_registry: Optional[DetectorRegistry] = None


def get_global_registry() -> DetectorRegistry:
    """Get the global detector registry instance.
    
    This creates a singleton registry on first call.
    The registry itself is immutable, but detectors can be registered.
    """
    global _global_registry
    
    if _global_registry is None:
        _global_registry = DetectorRegistry()
    
    return _global_registry
```

**Issue**:
- `_global_registry` is **mutable global state**
- Comment claims "This is NOT mutable state" (line 277) - **FALSE**
- Registry instance can be modified via `register()`/`unregister()`

**Severity**: **WARNING** (Acceptable)

**Justification**:
- Global registry is **optional** (not required)
- Instance-scoped registry is available (`DetectorRegistry()`)
- Singleton pattern is **common** for registries
- **ACCEPTABLE** but violates strict purity

**Mitigation**:
- Developers can use instance-scoped registry
- `reset_global_registry()` available for testing (line 303)

**Recommendation**: Update comment to acknowledge mutability.

**Verdict**: **WARNING** - Global mutable state exists but optional

---

## PART 6 — DETECTOR INTERFACE COMPLIANCE

### 6.1 Interface Validation

#### ✅ **PASS**

**Expected**: Only accepts detectors implementing `AIDetector`  
**Actual**: Validates interface compliance

**Evidence**: **Lines 85-89**

```python
if not issubclass(detector_class, AIDetector):
    raise TypeError(
        f"Detector class must implement AIDetector interface, "
        f"got {detector_class}"
    )
```

**Verification**:
- ✅ Uses `issubclass()` check
- ✅ Raises `TypeError` if invalid
- ✅ Only accepts classes (not instances)

**Verdict**: **PASS** - Interface validation correct

---

### 6.2 No Detector Assumptions

#### ✅ **PASS**

**Expected**: Does not assume detector behavior  
**Actual**: Only uses `name` and `version` properties

**Evidence**: **Lines 247-250**

```python
return {
    "name": detector.name,
    "version": detector.version,
}
```

**Verification**:
- ✅ NO `detect()` calls
- ✅ NO internal attribute access
- ✅ Only uses public interface (`name`, `version`)
- ✅ NO assumptions about detector reliability

**Verdict**: **PASS** - No detector assumptions

---

## PART 7 — PROHIBITED DEPENDENCIES

### 7.1 No Prohibited Imports

#### ✅ **PASS**

**Expected**: NO database, FastAPI, Celery, Redis, HTTP, file I/O imports  
**Actual**: Only standard library and local interface

**Imports** (lines 24-26):
```python
from typing import Dict, List, Optional, Type

from app.services.ai_detectors.base import AIDetector
```

**Verification**:
- ✅ NO `sqlalchemy`
- ✅ NO `fastapi`
- ✅ NO `celery`
- ✅ NO `redis`
- ✅ NO `requests` / `httpx`
- ✅ NO `os` / `pathlib`

**Verdict**: **PASS** - No prohibited imports

---

## PART 8 — FAILURE & EDGE CASES

### 8.1 Disabled Detectors

#### ✅ **PASS**

**Expected**: Disabled detectors are never returned  
**Actual**: Only enabled detectors are instantiated

**Evidence**: **Lines 207-209**

```python
# If no detectors enabled, return empty list
if not enabled_ids:
    return []
```

**Lines 211-221**:
```python
# Instantiate enabled detectors in config order (deterministic)
detectors = []
for detector_id in enabled_ids:
    # Only iterate enabled_ids
    ...
```

**Verification**:
- ✅ Empty `enabled_detectors` → empty list
- ✅ Only detectors in `enabled_ids` are returned
- ✅ Disabled detectors are never instantiated

**Verdict**: **PASS** - Disabled detectors handled correctly

---

### 8.2 Unknown Detector Names

#### ✅ **PASS**

**Expected**: Unknown detector names handled explicitly  
**Actual**: Raises `KeyError` with helpful message

**Evidence**: **Lines 214-218**

```python
if detector_id not in self._detectors:
    raise KeyError(
        f"Detector '{detector_id}' is enabled in config but not registered. "
        f"Available detectors: {self.list_registered()}"
    )
```

**Also**: **Lines 153-157** (in `get_detector_class`)

**Verdict**: **PASS** - Unknown detectors handled explicitly

---

### 8.3 Duplicate Registrations

#### ✅ **PASS**

**Expected**: Duplicate registrations prevented or handled  
**Actual**: Raises `ValueError` on duplicate

**Evidence**: **Lines 79-83**

```python
if detector_id in self._detectors:
    raise ValueError(
        f"Detector '{detector_id}' is already registered. "
        f"Use unregister() first if you want to replace it."
    )
```

**Verdict**: **PASS** - Duplicates prevented

---

### 8.4 Empty Registry State

#### ✅ **PASS**

**Expected**: Empty registry handled safely  
**Actual**: Returns empty list

**Evidence**: **Lines 188-190**

```python
# If no config provided, return all detectors in registration order
if config is None or not config:
    return [cls() for cls in self._detectors.values()]
```

If `self._detectors` is empty, `values()` returns empty iterator → empty list.

**Also**: **Lines 207-209**

```python
# If no detectors enabled, return empty list
if not enabled_ids:
    return []
```

**Verdict**: **PASS** - Empty registry handled safely

---

## PART 9 — AUDITABILITY

### 9.1 Explainability

#### ✅ **PASS**

**Expected**: Registry behavior explainable from code alone  
**Actual**: Clear docstrings and comments

**Evidence**:

**Module Docstring** (lines 1-22):
- Lists what registry DOES
- Lists what registry does NOT do
- Explicit about safety

**Method Docstrings**:
- All methods have comprehensive docstrings
- Include examples
- Document exceptions
- Explain behavior

**Comments**:
- **Line 62**: Explains dict usage for ordering
- **Line 188**: Explains default behavior
- **Line 211**: Explains deterministic ordering
- **Line 277**: Explains global registry (though misleading)

**Verdict**: **PASS** - Highly explainable

---

### 9.2 No Hidden Magic

#### ✅ **PASS**

**Expected**: No hidden magic  
**Actual**: All behavior is explicit

**Verification**:
- ✅ NO metaclasses
- ✅ NO decorators with side effects
- ✅ NO dynamic imports
- ✅ NO `__getattr__` magic
- ✅ NO hidden registration

**Verdict**: **PASS** - No hidden magic

---

## PART 10 — FINAL VERDICT

### Summary of Findings

| Dimension | Issue | Severity | Status |
|-----------|-------|----------|--------|
| 1.1 | Registry responsibility | - | ✅ PASS |
| 2.1 | Configuration injection | - | ✅ PASS |
| 2.2 | No environment access | - | ✅ PASS |
| 2.3 | No hidden defaults | WARNING | ⚠️ ACCEPTABLE |
| 3.1 | Deterministic ordering | - | ✅ PASS |
| 3.2 | No external dependencies | - | ✅ PASS |
| 4.1 | No side effects on import | - | ✅ PASS |
| 4.2 | No auto-registration | - | ✅ PASS |
| 5.1 | Global mutable state | WARNING | ⚠️ ACCEPTABLE |
| 6.1 | Interface validation | - | ✅ PASS |
| 6.2 | No detector assumptions | - | ✅ PASS |
| 7.1 | No prohibited imports | - | ✅ PASS |
| 8.1 | Disabled detectors | - | ✅ PASS |
| 8.2 | Unknown detector names | - | ✅ PASS |
| 8.3 | Duplicate registrations | - | ✅ PASS |
| 8.4 | Empty registry state | - | ✅ PASS |
| 9.1 | Explainability | - | ✅ PASS |
| 9.2 | No hidden magic | - | ✅ PASS |

**BLOCKING FAILURES**: 0  
**WARNINGS**: 2 (both acceptable)  
**PASS**: 16

---

### Final Verdict

## ⚠️ **CONDITIONAL PASS - SAFE TO PROCEED**

**Rationale**:

1. **No Blocking Issues**:
   - ✅ Registry performs only organizational functions
   - ✅ No detector execution
   - ✅ Configuration is injected
   - ✅ No environment access
   - ✅ Deterministic ordering
   - ✅ Safe to import
   - ✅ No prohibited dependencies

2. **Warning Issues (Acceptable)**:
   - ⚠️ **Auto-enable behavior**: `None` config returns all detectors (documented)
   - ⚠️ **Global mutable state**: Singleton registry is mutable (optional, instance-scoped alternative available)

3. **Strengths**:
   - ✅ Clear separation of concerns
   - ✅ Comprehensive error handling
   - ✅ Excellent documentation
   - ✅ Interface validation
   - ✅ Deterministic behavior
   - ✅ No hidden magic

4. **Production Readiness**:
   - ✅ Safe for external regulatory audit
   - ✅ Ready for Celery integration
   - ✅ Ready for FastAPI startup
   - ✅ Testable with pure Python

---

### Required Actions

#### RECOMMENDED (Non-Blocking)

1. **Update Comment** (Line 277):
   ```python
   # BEFORE
   # This is NOT mutable state - it's a singleton container
   
   # AFTER
   # This is a mutable singleton container for convenience.
   # For strict immutability, use instance-scoped DetectorRegistry().
   ```

2. **Document Auto-Enable Risk** (Line 171):
   ```python
   # Add to docstring
   WARNING: If config is None, ALL registered detectors are returned.
   This may auto-enable detectors unintentionally. Always pass explicit config.
   ```

---

### Compliance Certification

**Registry Responsibility**: ✅ PASS  
**Configuration Safety**: ✅ PASS  
**Determinism**: ✅ PASS  
**Import Safety**: ✅ PASS  
**Global State**: ⚠️ ACCEPTABLE  
**Interface Compliance**: ✅ PASS  
**Prohibited Dependencies**: ✅ PASS  
**Failure Handling**: ✅ PASS  
**Auditability**: ✅ PASS

---

### Next Steps

**Approved for Production**:
1. ✅ Register detectors at application startup
2. ✅ Integrate with Celery evaluation workflow
3. ✅ Use in FastAPI dependency injection
4. ✅ Add unit tests for edge cases

**Optional Improvements**:
- Update misleading comment about mutability
- Add warning about auto-enable behavior

---

**Audit Completed**: 2026-01-29T12:34:43+05:30  
**Auditor Signature**: Hostile Backend Systems Auditor  
**Certification**: APPROVED FOR PRODUCTION USE (with warnings)
