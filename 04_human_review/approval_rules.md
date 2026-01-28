# Compliance & Audit Hardening Policies

## Overview
This document defines the compliance policies and audit controls that ensure human dominance is provable and abuse-resistant. These policies address regulatory defensibility and platform compliance requirements.

---

## 1. Human Verification (`is_human`)

### Source of Truth
**Rule**: `is_human` is stored in the `users` table, NOT in JWT claims.

**Rationale**: JWT claims are self-asserted and can be spoofed. Database storage with admin-only modification ensures integrity.

### Verification Flow
```python
# CORRECT: Database lookup
def verify_human_approval(user_id: UUID) -> bool:
    user = db.query(users).filter(id == user_id).first()
    if not user:
        raise UserNotFound(user_id)
    return user.is_human

# INCORRECT: Trust JWT claim
def verify_human_approval_WRONG(request):
    return request.user.claims.get("is_human", False)  # SPOOFABLE
```

### Setting `is_human`
**Rule**: Only users with `role='admin'` can set `is_human=true`.

**Implementation**:
```sql
-- Admin-only UPDATE permission
REVOKE UPDATE ON users FROM app_user;
GRANT UPDATE (is_human) ON users TO admin_user;

-- Application-level check
def set_user_human_status(admin_id: UUID, target_user_id: UUID, is_human: bool):
    admin = db.query(users).filter(id == admin_id).first()
    if admin.role != 'admin':
        raise Forbidden("Only admins can modify is_human")
    
    db.update(users).where(id == target_user_id).values(is_human=is_human)
```

### Service Account Protection
**Rule**: Service accounts (role='system') CANNOT be marked `is_human=true`.

**Enforcement**: Database CHECK constraint (already in schema):
```sql
CONSTRAINT chk_system_not_human CHECK (
    role != 'system' OR is_human = false
)
```

### API Enforcement
**Rule**: All human-only endpoints MUST query `users.is_human` before proceeding.

**Implementation**:
```python
# In FastAPI dependency
async def require_human(user_id: UUID = Depends(get_current_user)):
    is_human = await db.fetch_val(
        "SELECT is_human FROM users WHERE id = $1", user_id
    )
    if not is_human:
        raise HTTPException(
            status_code=403,
            detail="This action requires a human user"
        )
    return user_id

# Usage
@app.post("/blogs/{blog_id}/approve")
async def approve_blog(
    blog_id: UUID,
    data: ApprovalRequest,
    user_id: UUID = Depends(require_human)  # Enforces human-only
):
    ...
```

---

## 2. Failed Approval Auditing

### Logging Rule
**Rule**: ALL approval attempts (success AND failure) MUST be logged to `approval_attempts` table.

### What to Log
```python
@dataclass
class ApprovalAttempt:
    blog_id: UUID
    attempted_by: UUID
    is_human: bool  # Snapshot at attempt time
    result: Literal["success", "forbidden", "invalid_state", "invalid_version"]
    attempted_at: datetime
    failure_reason: str | None
```

### Implementation
```python
async def approve_blog(blog_id: UUID, version_id: UUID, user_id: UUID):
    # Step 1: Verify human status
    user = await db.fetch_one("SELECT is_human FROM users WHERE id = $1", user_id)
    
    # Step 2: Log attempt (BEFORE enforcement)
    attempt_id = await db.insert_approval_attempt(
        blog_id=blog_id,
        attempted_by=user_id,
        is_human=user.is_human,
        result="pending"  # Will update
    )
    
    # Step 3: Enforce human-only
    if not user.is_human:
        await db.update_approval_attempt(
            attempt_id,
            result="forbidden",
            failure_reason="User is not marked as human"
        )
        raise HTTPException(403, "Human verification required")
    
    # Step 4: Validate version belongs to blog
    version = await db.fetch_one(
        "SELECT blog_id FROM blog_versions WHERE id = $1", version_id
    )
    if version.blog_id != blog_id:
        await db.update_approval_attempt(
            attempt_id,
            result="invalid_version",
            failure_reason=f"Version {version_id} does not belong to blog {blog_id}"
        )
        raise HTTPException(400, "Version mismatch")
    
    # Step 5: Proceed with approval
    await db.insert_approval_state(
        blog_id=blog_id,
        approved_version_id=version_id,
        approver_id=user_id
    )
    
    await db.update_approval_attempt(attempt_id, result="success")
```

### Abuse Detection Queries
```sql
-- Detect repeated failed attempts (possible bypass attempt)
SELECT attempted_by, COUNT(*) as failed_attempts
FROM approval_attempts
WHERE result != 'success'
  AND attempted_at > NOW() - INTERVAL '1 hour'
GROUP BY attempted_by
HAVING COUNT(*) > 10;

-- Detect service accounts attempting approval
SELECT *
FROM approval_attempts
WHERE is_human = false
  AND attempted_at > NOW() - INTERVAL '7 days';
```

---

## 3. Rubber-Stamp Detection

### Minimum Review Time Policy
**Rule**: If a blog version is approved within 30 seconds of creation, it is flagged as a "fast approval".

**Rationale**: 30 seconds is insufficient to read and review content. This indicates rubber-stamping or automation.

### Implementation
```python
async def approve_blog(blog_id: UUID, version_id: UUID, user_id: UUID):
    # ... (human verification as above)
    
    # Fetch version creation time
    version = await db.fetch_one(
        "SELECT created_at FROM blog_versions WHERE id = $1", version_id
    )
    
    time_since_creation = datetime.now(UTC) - version.created_at
    
    # Check for fast approval
    if time_since_creation.total_seconds() < 30:
        # Log warning in approval_states
        notes = f"WARNING: Fast approval detected ({time_since_creation.total_seconds():.1f}s). Possible rubber-stamp."
        
        await db.insert_approval_state(
            blog_id=blog_id,
            approved_version_id=version_id,
            approver_id=user_id,
            notes=notes  # NEW COLUMN: approval_states.notes
        )
        
        # Also log to separate fast_approvals table for monitoring
        await db.insert_fast_approval(
            approval_id=approval_id,
            reviewer_id=user_id,
            review_duration_seconds=time_since_creation.total_seconds()
        )
        
        # Optional: Send alert to manager
        await notification.send_alert(
            to=config.MANAGER_EMAIL,
            subject=f"Fast Approval Alert: {user_id}",
            body=f"User {user_id} approved blog {blog_id} in {time_since_creation.total_seconds():.1f}s"
        )
    else:
        # Normal approval
        await db.insert_approval_state(
            blog_id=blog_id,
            approved_version_id=version_id,
            approver_id=user_id
        )
```

### Schema Addition
```sql
-- Add notes column to approval_states
ALTER TABLE approval_states ADD COLUMN notes TEXT;

-- Optional: Dedicated fast approval tracking
CREATE TABLE fast_approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    approval_id UUID NOT NULL REFERENCES approval_states(id),
    reviewer_id UUID NOT NULL REFERENCES users(id),
    review_duration_seconds NUMERIC(10, 2) NOT NULL,
    flagged_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fast_approvals_reviewer ON fast_approvals(reviewer_id);
```

### Manager Review Requirement (Optional)
**Rule**: If a user has 3+ fast approvals in 24 hours, require manager co-signature for future approvals.

```python
async def approve_blog(blog_id: UUID, version_id: UUID, user_id: UUID):
    # Check fast approval history
    fast_approval_count = await db.fetch_val(
        """
        SELECT COUNT(*) FROM fast_approvals
        WHERE reviewer_id = $1
          AND flagged_at > NOW() - INTERVAL '24 hours'
        """,
        user_id
    )
    
    if fast_approval_count >= 3:
        raise HTTPException(
            status_code=403,
            detail="Manager co-signature required due to repeated fast approvals"
        )
```

---

## 4. Detector Drift Awareness

### Model Version Storage
**Rule**: ALL AI detector scores MUST include the detector's model version in the `details` JSONB column.

### Implementation
```python
async def run_ai_detector(run_id: UUID, provider: str):
    # Call detector API
    response = await detector_api.check(content, provider=provider)
    
    # Extract model version from response
    model_version = response.get("model_version") or response.get("version") or "unknown"
    
    # Store score with model version
    await db.insert_ai_detector_score(
        run_id=run_id,
        provider=provider,
        score=response.score,
        details={
            "model_version": model_version,  # REQUIRED
            "raw_response": response.raw,
            "timestamp": datetime.now(UTC).isoformat()
        }
    )
```

### Score Comparison Rule
**Rule**: When comparing scores across evaluation runs, ONLY compare scores from the same detector model version.

**Implementation**:
```python
def detect_score_regression(current_run_id: UUID, blog_id: UUID):
    current_scores = db.get_scores_by_run(current_run_id)
    previous_run = db.get_latest_completed_run_for_blog(blog_id, exclude_run=current_run_id)
    previous_scores = db.get_scores_by_run(previous_run.id)
    
    for metric in ["ai_detector_avg", "aeo_avg"]:
        # NEW CHECK: Verify model versions match
        current_model = current_scores.get(f"{metric}_model_version")
        previous_model = previous_scores.get(f"{metric}_model_version")
        
        if current_model != previous_model:
            logger.warning(
                f"Skipping {metric} comparison: model version mismatch "
                f"(current={current_model}, previous={previous_model})"
            )
            continue  # Skip this metric
        
        # Safe to compare
        delta = current_scores[metric] - previous_scores[metric]
        if delta < -10:
            regression_detected = True
```

### UI Warning
**Rule**: When displaying historical scores, show a warning if model versions differ.

**Example**:
```
AI Detector Score: 85 (Originality.ai v2.1)
Previous Score: 90 (Originality.ai v1.9)

⚠️ WARNING: Scores from different model versions are not directly comparable.
```

---

## 5. Storage Implications

### New Columns
- `approval_states.notes` (TEXT) - For fast approval warnings
- `ai_detector_scores.details` (JSONB) - Already exists, now REQUIRED to include `model_version`

### New Tables
- `fast_approvals` (Optional) - Dedicated tracking for rubber-stamp detection

### Indexes
```sql
-- Fast approval lookups
CREATE INDEX idx_fast_approvals_reviewer_time ON fast_approvals(reviewer_id, flagged_at);

-- Abuse detection
CREATE INDEX idx_approval_attempts_failed ON approval_attempts(attempted_by, attempted_at) 
WHERE result != 'success';
```

---

## 6. Compliance Checklist

When audited by regulators or platforms, you can prove:

- [x] **Human Dominance**: `is_human` is database-backed, admin-only, with CHECK constraints preventing service account spoofing
- [x] **Approval Accountability**: Every approval attempt logged, including failures
- [x] **Rubber-Stamp Prevention**: Fast approvals flagged and monitored
- [x] **Score Integrity**: Detector model versions tracked, invalid comparisons prevented
- [x] **Audit Trail**: All state changes are INSERT-ONLY with timestamps and actor IDs
- [x] **No Auto-Approval**: Rewrite suggestions are advisory-only, require explicit human acceptance

---

## 7. Regulatory Response Templates

### "How do you prevent AI from auto-publishing content?"
**Answer**: 
1. AI generates suggestions only, stored in `rewrite_suggestions` table with status `pending_user_acceptance`.
2. Human must explicitly call `POST /blogs/{id}/versions` to create a new version.
3. Approval requires `is_human=true` verified via database lookup, not self-asserted claims.
4. All approval attempts logged in `approval_attempts` table, including forbidden attempts.

### "How do you prevent rubber-stamp approvals?"
**Answer**:
1. Approvals within 30 seconds of version creation are flagged in `approval_states.notes`.
2. Fast approvals tracked in `fast_approvals` table.
3. Repeated fast approvals (3+ in 24h) trigger manager co-signature requirement.
4. All approval timestamps auditable via `approval_states.approved_at`.

### "How do you ensure score accuracy over time?"
**Answer**:
1. All detector scores include `model_version` in `details` JSONB.
2. Score regression detection skips comparisons when model versions differ.
3. UI displays warnings when showing scores from different model versions.
4. Historical scores remain immutable (INSERT-ONLY) for auditability.
