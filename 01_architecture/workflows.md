# Hardened Background Workflows

## Overview
This document contains the **PATCHED** Celery workflows with race condition fixes, idempotency improvements, and enforcement gaps closed. All changes are marked with `# NEW CHECK` or `# AUDIT FIX`.

---

## Workflow 1: AI Detection Evaluation (HARDENED)

### Celery Job Sequence
```python
@celery.task(bind=True, max_retries=3)
def evaluate_version(self, version_id: UUID, config: dict):
    # AUDIT FIX: Issue 3.1 - State-based idempotency (not time-based)
    # NEW CHECK: Look for in-progress runs, not time window
    existing = db.query(evaluation_runs).filter(
        blog_version_id == version_id,
        completed_at IS NULL  # Still processing
    ).first()
    
    if existing:
        # Reuse existing run (idempotent retry)
        return {"run_id": existing.id, "status": "processing"}
    
    # Step 1: Create evaluation_run (INSERT)
    run_id = db.insert_evaluation_run(
        blog_version_id=version_id,
        triggered_by=config["triggered_by"],
        model_config=config,
        status="processing"
    )
    
    # Step 2: Fan-out to detector tasks (parallel)
    detector_results = []
    if config["include_detectors"]:
        detector_group = group([
            run_ai_detector.s(run_id, "originality_ai"),
            run_ai_detector.s(run_id, "copyleaks"),
            run_ai_detector.s(run_id, "gptzero")
        ])
        detector_results = detector_group.apply_async()
    
    # Step 3: Fan-out to AEO scoring (parallel)
    if config["include_aeo"]:
        run_aeo_scoring.delay(run_id)
    
    # Step 4: Register completion callback
    # AUDIT FIX: Issue 3.3 - Check for total detector failure
    chord(detector_results)(finalize_evaluation.s(run_id))
    
    return {"run_id": run_id, "status": "processing"}


@celery.task
def finalize_evaluation(detector_results, run_id: UUID):
    """
    AUDIT FIX: Issue 3.3 - Detect partial vs total failure
    """
    # NEW CHECK: Count successful vs failed detectors
    successful_detectors = sum(1 for r in detector_results if r.get("status") == "success")
    total_detectors = len(detector_results)
    
    if successful_detectors == 0:
        # Total failure - mark as failed
        db.update_evaluation_run(run_id, status="failed")
    elif successful_detectors < total_detectors:
        # Partial failure - still usable but incomplete
        db.update_evaluation_run(run_id, status="partial_failure")
    else:
        # All succeeded
        db.update_evaluation_run(run_id, status="completed")
    
    db.update_evaluation_run(run_id, completed_at=NOW())
    
    # Trigger regression detection
    version = db.get_version_by_run_id(run_id)
    detect_score_regression.delay(run_id, version.blog_id)
```

**Why This Fixes Issue 3.1**: State-based idempotency checks for `completed_at IS NULL` instead of "within 5 minutes", preventing duplicate runs on retry after timeout.

**Why This Fixes Issue 3.3**: Distinguishes total failure (no data) from partial failure (some data), allowing user to make informed decisions.

---

## Workflow 2: AEO Scoring (HARDENED)

```python
@celery.task(bind=True, max_retries=3)
def run_aeo_scoring(self, run_id: UUID):
    # Step 1: Fetch version content
    version = db.get_version_by_run_id(run_id)
    
    # Step 2: Call Claude 3.5 Sonnet for each query intent
    query_intents = ["how to", "what is", "best practices"]
    
    for intent in query_intents:
        # NEW CHECK: Idempotent - skip if already scored
        existing = db.query(aeo_scores).filter(
            run_id == run_id,
            query_intent == intent
        ).first()
        
        if existing:
            continue  # Already scored (retry safety)
        
        try:
            score, rationale = llm.score_aeo(
                content=version.content,
                query_intent=intent,
                timeout=60  # AUDIT FIX: Issue 6.1 - Explicit timeout
            )
            
            # Step 3: INSERT score
            db.insert_aeo_score(
                run_id=run_id,
                query_intent=intent,
                score=score,
                rationale=rationale
            )
        except TimeoutError:
            # Log timeout, continue with other intents
            logger.warning(f"AEO scoring timeout for intent={intent}, run={run_id}")
            continue
```

**Why This Fixes Issue 6.1**: Adds explicit 60s timeout per intent, preventing 6-hour hangs.

---

## Workflow 3: Rewrite Orchestration (HARDENED)

```python
@celery.task(bind=True, max_retries=1)
def orchestrate_rewrite(self, source_version_id: UUID, config: dict):
    # AUDIT FIX: Issue 1.2 - TOCTOU race protection
    # NEW CHECK: Re-check approval state INSIDE task (not just API)
    version = db.get_version(source_version_id)
    blog = db.get_blog(version.blog_id)
    
    # Defense in depth: Check if blog became approved while queued
    current_approval = db.query(approval_states).filter(
        blog_id == blog.id,
        revoked_at IS NULL
    ).order_by(approved_at.desc()).first()
    
    if current_approval:
        raise ApprovedContentError(
            f"Cannot rewrite approved blog {blog.id}. "
            f"Approval granted at {current_approval.approved_at}"
        )
    
    # AUDIT FIX: Issue 7.2 - Enforce rewrite cap in task (defense in depth)
    # NEW CHECK: Count rewrite cycles for this blog
    rewrite_count = db.query(rewrite_cycles).join(blog_versions).filter(
        blog_versions.blog_id == blog.id
    ).count()
    
    if rewrite_count >= 10:
        raise RewriteCapExceeded(
            f"Blog {blog.id} has reached max rewrite cycles (10)"
        )
    
    # Step 1: Create rewrite_cycle (INSERT)
    cycle_id = db.insert_rewrite_cycle(
        source_version_id=source_version_id,
        llm_model="claude-3-5-sonnet",
        prompt_template_id=config["prompt_template_id"]
    )
    
    # Step 2: Fetch source content
    source = db.get_version(source_version_id)
    
    # Step 3: Call LLM for rewrite
    try:
        rewritten_content = llm.rewrite(
            content=source.content,
            instructions=config["instructions"],
            timeout=120  # 2 minutes max
        )
    except TimeoutError:
        db.update_rewrite_cycle(cycle_id, completed_at=NOW(), status="timeout")
        raise
    
    # Step 4: ADVISORY ONLY - Store suggestion
    db.insert_rewrite_suggestion(
        cycle_id=cycle_id,
        suggested_content=rewritten_content,
        status="pending_user_acceptance"
    )
    
    db.update_rewrite_cycle(cycle_id, completed_at=NOW())
    
    return {"cycle_id": cycle_id, "status": "suggestion_ready"}
```

**Why This Fixes Issue 1.2**: Re-checks approval state inside the task after queue delay, preventing TOCTOU race where blog is approved mid-rewrite.

**Why This Fixes Issue 7.2**: Enforces rewrite cap inside task, not just API (defense in depth against direct Celery invocation).

---

## Workflow 4: Score Regression Detection (HARDENED)

```python
@celery.task
def detect_score_regression(current_run_id: UUID, blog_id: UUID):
    # Step 1: Fetch current scores
    current_scores = db.get_scores_by_run(current_run_id)
    
    # AUDIT FIX: Issue 3.2 - Respect approval state
    # NEW CHECK: If blog already approved, scores are advisory only
    current_approval = db.query(approval_states).filter(
        blog_id == blog_id,
        revoked_at IS NULL
    ).order_by(approved_at.desc()).first()
    
    if current_approval:
        # Blog already approved - human has overridden scores
        logger.info(
            f"Skipping regression detection for approved blog {blog_id}. "
            f"Approval is human override of scores."
        )
        return  # No escalation needed
    
    # Step 2: Fetch previous approved version's scores (if any)
    # If no previous approval, use latest evaluation as baseline
    previous_run = db.get_latest_completed_run_for_blog(blog_id, exclude_run=current_run_id)
    
    if not previous_run:
        return  # No baseline, skip
    
    previous_scores = db.get_scores_by_run(previous_run.id)
    
    # Step 3: Compare scores
    regression_detected = False
    regression_details = {}
    
    for metric in ["ai_detector_avg", "aeo_avg"]:
        delta = current_scores.get(metric, 0) - previous_scores.get(metric, 0)
        if delta < -10:  # 10-point drop
            regression_detected = True
            regression_details[metric] = delta
    
    # Step 4: If regression, escalate
    if regression_detected:
        current_run = db.get_evaluation_run(current_run_id)
        escalate_to_human.delay(
            version_id=current_run.blog_version_id,
            reason="score_regression",
            details=regression_details
        )
```

**Why This Fixes Issue 3.2**: Checks if blog is already approved before escalating. Approval is a human decision that overrides scores, so escalation after approval is unnecessary.

---

## Workflow 5: Escalation to Human Review (HARDENED)

```python
@celery.task
def escalate_to_human(version_id: UUID, reason: str, details: dict):
    # Get blog_id from version
    version = db.get_version(version_id)
    blog_id = version.blog_id
    
    # NEW CHECK: Idempotent - don't create duplicate escalations
    existing = db.query(escalations).filter(
        blog_id == blog_id,
        version_id == version_id,
        reason == reason,
        status == "pending_review"
    ).first()
    
    if existing:
        return {"escalation_id": existing.id, "status": "already_escalated"}
    
    # Step 1: Create escalation record (INSERT)
    escalation_id = db.insert_escalation(
        blog_id=blog_id,
        version_id=version_id,
        reason=reason,
        details=details,
        status="pending_review"
    )
    
    # Step 2: Notify reviewers
    notification.send(
        to=config.REVIEWER_EMAILS,
        subject=f"Review Required: {reason}",
        body=f"Blog {blog_id}, Version {version_id} requires human review.\n"
             f"Reason: {reason}\n"
             f"Details: {json.dumps(details, indent=2)}"
    )
    
    # Step 3: Blog is now escalated
    # AUDIT FIX: Issue 4.2 - No mutable flag, inferred from escalations table
    # Query: SELECT 1 FROM escalations WHERE blog_id=X AND status='pending_review'
    
    return {"escalation_id": escalation_id, "status": "escalated"}
```

**Why This Fixes Issue 4.2**: No mutable `is_escalated` flag on `blogs` table. Escalation state is inferred from `escalations` table with indexed query.

---

## Workflow 6: Hard Stop Conditions (UPDATED)

### Actions Automation is NOT Allowed to Perform
1. **Create blog_version**: Only humans via `POST /blogs/{id}/versions`
2. **Approve blog**: Only humans via `POST /blogs/{id}/approve`
3. **Publish content**: Only humans (external CMS integration)
4. **Delete versions**: No one (immutable)
5. **Update existing versions**: No one (immutable)
6. **Auto-accept rewrites**: Rewrites are suggestions only
7. **Bypass escalations**: Once escalated, human must resolve
8. **Rewrite approved blogs**: Blocked at API + Celery task level

### Conditions That Trigger Hard Stop
1. **Score regression > 10 points** (unless already approved)
2. **AI detector score < 70** (likely AI-generated)
3. **AEO score < 60** (poor quality)
4. **Rewrite cycle count > 10** (infinite loop protection)
5. **Approved blog rewrite attempt** (TOCTOU protection)

---

## Summary of Audit Fixes

| Issue | Severity | Fix Location | Fix Description |
|-------|----------|--------------|-----------------|
| 1.2 | HIGH | `orchestrate_rewrite` | Added approval check inside task (TOCTOU protection) |
| 3.1 | HIGH | `evaluate_version` | Changed to state-based idempotency (`completed_at IS NULL`) |
| 3.2 | MEDIUM | `detect_score_regression` | Skip escalation if blog already approved |
| 3.3 | MEDIUM | `finalize_evaluation` | Distinguish partial vs total detector failure |
| 4.2 | HIGH | `escalate_to_human` | No mutable flag, inferred from `escalations` table |
| 6.1 | MEDIUM | `run_aeo_scoring` | Added explicit 60s timeout per intent |
| 7.2 | MEDIUM | `orchestrate_rewrite` | Enforce rewrite cap inside task (defense in depth) |
