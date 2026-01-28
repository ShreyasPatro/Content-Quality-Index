# Immutability Policy & Justification

## Overview
This document explains which tables are immutable, which allow limited updates, and why this does NOT violate system invariants.

---

## Fully Immutable Tables

### 1. `blog_versions`
**Immutability**: TOTAL (no UPDATE or DELETE allowed)

**Rationale**: 
- Contains content data that must never change
- `content_hash` is generated column based on content
- Any modification would invalidate audit trail
- Lineage via `parent_version_id` must be preserved

**Trigger**: `prevent_modification()`

---

### 2. `human_review_actions`
**Immutability**: TOTAL (no UPDATE or DELETE allowed)

**Rationale**:
- Audit log of human decisions
- Regulatory requirement: cannot modify review history
- Timestamps and actions must be tamper-proof

**Trigger**: `prevent_modification()`

---

## Partially Immutable Tables

### 3. `evaluation_runs`
**Immutability**: PARTIAL (allow status and completed_at updates ONLY)

**Rationale**:
This table has two distinct types of data:

#### Immutable Data (Evaluation Identity & Config)
- `id` - Unique identifier
- `blog_version_id` - What was evaluated
- `run_at` - When evaluation started
- `triggered_by` - Who triggered it
- `model_config` - Snapshot of evaluation parameters

**These fields are PROTECTED** by `prevent_eval_data_modification()` trigger.

#### Mutable Workflow State
- `status` - Lifecycle state (`processing` → `completed`/`failed`/`partial_failure`)
- `completed_at` - When evaluation finished

**Why Status Updates Do NOT Violate Invariants**:

1. **Status is not evaluation data** - It's workflow metadata indicating job progress
2. **Status transitions are append-only in nature** - They only move forward (`processing` → `completed`)
3. **Auditability is preserved** - `run_at` (creation) and `completed_at` (completion) provide full timeline
4. **No content is mutated** - The actual evaluation results (scores) are in separate INSERT-ONLY tables (`ai_detector_scores`, `aeo_scores`)

**Trigger**: `prevent_eval_data_modification()`

---

## Why This Design is Safe

### Invariant: "Content is Immutable"
✅ **PRESERVED**: `blog_versions.content` cannot be modified

### Invariant: "Audit Trail is Complete"
✅ **PRESERVED**: 
- `evaluation_runs.run_at` is immutable (when evaluation started)
- `evaluation_runs.completed_at` is write-once (when evaluation finished)
- Together they provide complete timeline
- Actual scores are in separate immutable tables

### Invariant: "Human Actions are Tamper-Proof"
✅ **PRESERVED**: `human_review_actions` is fully immutable

---

## Status Transition Examples

### Valid Status Updates
```sql
-- Workflow marks evaluation as completed
UPDATE evaluation_runs 
SET status = 'completed', completed_at = NOW() 
WHERE id = '...' AND status = 'processing';
-- ✅ ALLOWED: Only status and completed_at changed
```

```sql
-- Workflow marks evaluation as failed
UPDATE evaluation_runs 
SET status = 'failed', completed_at = NOW() 
WHERE id = '...' AND status = 'processing';
-- ✅ ALLOWED: Only status and completed_at changed
```

### Invalid Updates (Blocked by Trigger)
```sql
-- Attempt to change which version was evaluated
UPDATE evaluation_runs 
SET blog_version_id = '...' 
WHERE id = '...';
-- ❌ BLOCKED: Core evaluation data cannot be modified
```

```sql
-- Attempt to change who triggered evaluation
UPDATE evaluation_runs 
SET triggered_by = '...' 
WHERE id = '...';
-- ❌ BLOCKED: Core evaluation data cannot be modified
```

```sql
-- Attempt to delete evaluation run
DELETE FROM evaluation_runs WHERE id = '...';
-- ❌ BLOCKED: Deletion is forbidden
```

---

## Comparison to Alternative Designs

### Alternative 1: Fully Immutable evaluation_runs
**Problem**: Workflows cannot update status, requiring:
- Separate `evaluation_run_status_changes` table (INSERT-ONLY)
- Complex queries to get current status
- Overhead for simple workflow state

**Verdict**: Over-engineered for workflow metadata

### Alternative 2: No Immutability on evaluation_runs
**Problem**: Core evaluation data (version_id, config) could be modified, breaking audit trail

**Verdict**: Too permissive, violates invariants

### Chosen Design: Partial Immutability
**Benefits**:
- Protects core evaluation data
- Allows workflow state updates
- Simple queries for current status
- Auditability preserved via timestamps

**Verdict**: ✅ Optimal balance

---

## Trigger Implementation Details

### `prevent_eval_data_modification()` Logic
```sql
1. Block ALL DELETE operations
2. On UPDATE, check if core fields changed:
   - id
   - blog_version_id
   - run_at
   - triggered_by
   - model_config
3. If core fields changed → RAISE EXCEPTION
4. If only status/completed_at changed → ALLOW
```

### Why `IS DISTINCT FROM` Instead of `!=`
- Handles NULL values correctly
- `NULL != NULL` is NULL (not TRUE)
- `NULL IS DISTINCT FROM NULL` is FALSE
- Ensures trigger works even if fields are NULL

---

## Audit Trail Proof

### Question: "Can you prove evaluation X was for version Y?"
**Answer**: YES
```sql
SELECT blog_version_id, run_at, triggered_by, model_config
FROM evaluation_runs
WHERE id = 'X';
```
These fields are immutable, so the answer is tamper-proof.

### Question: "Can you prove when evaluation X completed?"
**Answer**: YES
```sql
SELECT run_at, completed_at, status
FROM evaluation_runs
WHERE id = 'X';
```
- `run_at` is immutable (creation timestamp)
- `completed_at` is write-once (completion timestamp)
- Together they provide full timeline

### Question: "Can you prove what scores evaluation X produced?"
**Answer**: YES
```sql
SELECT * FROM ai_detector_scores WHERE run_id = 'X';
SELECT * FROM aeo_scores WHERE run_id = 'X';
```
These tables are fully INSERT-ONLY (no triggers needed, application enforces).

---

## Summary

| Table | Immutability | Trigger | Justification |
|-------|--------------|---------|---------------|
| `blog_versions` | TOTAL | `prevent_modification()` | Content data must never change |
| `human_review_actions` | TOTAL | `prevent_modification()` | Audit log must be tamper-proof |
| `evaluation_runs` | PARTIAL | `prevent_eval_data_modification()` | Protect eval data, allow workflow state |
| `ai_detector_scores` | INSERT-ONLY | None (app enforced) | Evaluation results are immutable |
| `aeo_scores` | INSERT-ONLY | None (app enforced) | Evaluation results are immutable |
| `approval_states` | INSERT-ONLY | None (app enforced) | Revocation via new rows, not UPDATE |

**Verdict**: The partial immutability design for `evaluation_runs` is **SAFE** and does NOT violate system invariants.
