# AI Detection Tables - Implementation Summary

## Overview

This document summarizes the SQLAlchemy Core table definitions for AI detection-related tables.

## Delivered Files

### 1. `app/models/ai_detection.py` (NEW)
Consolidated module for AI detection tables with comprehensive documentation.

**Exports**:
- `ai_detector_scores` - Third-party AI detector scores
- `aeo_scores` - Answer Engine Optimization scores  
- `evaluation_runs` - Evaluation orchestration metadata

**Features**:
- Detailed table documentation with column descriptions
- Constraint explanations
- Immutability policy notes
- Usage examples for common operations

### 2. `app/models/scores.py` (EXISTING)
Contains actual table definitions for scoring tables.

**Tables**:
- `ai_detector_scores` - Stores AI detection scores from providers
- `aeo_scores` - Stores AEO quality scores

### 3. `app/models/evaluations.py` (EXISTING)
Contains evaluation orchestration table.

**Tables**:
- `evaluation_runs` - Tracks evaluation pipeline execution

### 4. `app/models/__init__.py` (UPDATED)
Updated to export AI detection tables from the new consolidated module.

## Table Definitions

### ai_detector_scores

**Purpose**: Store immutable AI detection scores from third-party providers.

**Schema**:
```python
Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
Column("run_id", UUID, ForeignKey("evaluation_runs.id"), nullable=False)
Column("provider", String(50), nullable=False)  # e.g., "originality_ai", "gptzero"
Column("score", Numeric(5, 2), nullable=False)  # 0-100
Column("details", JSONB, nullable=True)  # model_version, raw_response, timestamp
```

**Constraints**:
- `UNIQUE(run_id, provider)` - One score per provider per evaluation
- `CHECK(score >= 0 AND score <= 100)` - Valid score range

**Indexes**:
- `idx_detector_scores_run` - Fast lookup by evaluation run

**Immutability**: INSERT-ONLY (enforced by database trigger)

---

### aeo_scores

**Purpose**: Store immutable AEO quality scores for query intents.

**Schema**:
```python
Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
Column("run_id", UUID, ForeignKey("evaluation_runs.id"), nullable=False)
Column("query_intent", Text, nullable=False)  # Target query/question
Column("score", Numeric(5, 2), nullable=False)  # 0-100
Column("rationale", Text, nullable=True)  # LLM explanation
```

**Constraints**:
- `UNIQUE(run_id, query_intent)` - One score per query per evaluation
- `CHECK(score >= 0 AND score <= 100)` - Valid score range

**Indexes**:
- `idx_aeo_scores_run` - Fast lookup by evaluation run

**Immutability**: INSERT-ONLY (enforced by database trigger)

---

### evaluation_runs

**Purpose**: Orchestrate evaluation pipeline execution.

**Schema**:
```python
Column("id", UUID, primary_key=True, server_default=text("uuid_generate_v4()"))
Column("blog_version_id", UUID, ForeignKey("blog_versions.id"), nullable=False)
Column("run_at", TIMESTAMPTZ, nullable=False, server_default=text("NOW()"))
Column("triggered_by", UUID, ForeignKey("users.id"), nullable=True)
Column("model_config", JSONB, nullable=True)  # Snapshot for replayability
Column("completed_at", TIMESTAMPTZ, nullable=True)
Column("status", String(20), nullable=False, server_default=text("'processing'"))
```

**Status Values**:
- `processing` - Evaluation in progress
- `completed` - All detectors succeeded
- `partial_failure` - Some detectors failed
- `failed` - All detectors failed

**Constraints**:
- `CHECK(status IN ('processing', 'completed', 'partial_failure', 'failed'))`

**Indexes**:
- `idx_eval_runs_version` - Fast lookup by blog version
- `idx_eval_runs_status` - Partial index for incomplete runs

**Partial Immutability**:
- Core data (blog_version_id, run_at, model_config) is immutable
- Workflow metadata (status, completed_at) is updatable

## Usage Examples

### Insert AI Detector Score

```python
from app.models.ai_detection import ai_detector_scores

await conn.execute(
    ai_detector_scores.insert().values(
        run_id=run_id,
        provider="originality_ai",
        score=85.5,
        details={
            "model_version": "3.0",
            "raw_response": {...},
            "timestamp": "2026-01-29T11:16:52Z",
            "confidence": "high"
        }
    )
)
```

### Query Scores for Evaluation Run

```python
from sqlalchemy import select
from app.models.ai_detection import ai_detector_scores, aeo_scores

# Get all AI detector scores
stmt = select(ai_detector_scores).where(
    ai_detector_scores.c.run_id == run_id
)
detector_scores = await conn.execute(stmt)

# Get all AEO scores
stmt = select(aeo_scores).where(
    aeo_scores.c.run_id == run_id
)
aeo_results = await conn.execute(stmt)
```

### Check Evaluation Status

```python
from sqlalchemy import select
from app.models.ai_detection import evaluation_runs

stmt = select(evaluation_runs).where(
    evaluation_runs.c.id == run_id
)
result = await conn.execute(stmt)
run = result.fetchone()

if run.status == "completed":
    # All detectors succeeded
    pass
elif run.status == "partial_failure":
    # Some detectors failed
    pass
```

## Verification

All table definitions match `01_architecture/schema.sql`:

- ✅ Column types match
- ✅ Foreign keys match
- ✅ Constraints match
- ✅ Indexes match
- ✅ Default values match

## Integration Points

### Stage 5 (AI Detection Pipeline)

Detector tasks will:
1. Receive `run_id` from evaluation workflow
2. Call external detector APIs
3. Insert results into `ai_detector_scores`
4. Store model version in `details.model_version` for drift tracking

### Workflow Integration

```python
# In app/workflows/evaluation.py
from app.models.ai_detection import ai_detector_scores

# After detector completes
await conn.execute(
    ai_detector_scores.insert().values(
        run_id=run_id,
        provider=provider_name,
        score=result.score,
        details={
            "model_version": result.model_version,
            "raw_response": result.raw_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
)
```

## Notes

- **No ORM classes**: Pure SQLAlchemy Core as required
- **No queries**: Table definitions only, no business logic
- **No inserts/updates**: No mutation logic in table definitions
- **Shared metadata**: All tables use `app.models.base.metadata`
- **INSERT-ONLY**: Database triggers enforce immutability (not in Python code)
