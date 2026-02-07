# Evaluation Pipeline - Running Guide

## Overview

The evaluation pipeline runs AI Likeness detection and AEO scoring on pasted blog content. It supports both **asynchronous (Celery)** and **synchronous fallback** modes.

---

## Prerequisites

### Required
- PostgreSQL database running
- Python 3.12+
- Backend dependencies installed (`pip install -e .`)

### Optional (for async mode)
- Redis server running (for Celery task queue)

---

## Database Setup

### 1. Run Migration

Apply the blog ingestion schema changes:

```bash
cd backend
alembic upgrade head
```

This creates:
- `blogs.name` column (human-provided, immutable)
- `blogs.created_by` column (audit trail)
- `blog_versions.source` column with CHECK constraint (`human_paste`, `ai_rewrite`, `human_edit`)
- Changes `blog_versions.content` from JSONB to TEXT

### 2. Verify Migration

```bash
alembic current
# Should show: 20260131_001 (head)
```

---

## Running Modes

### Mode 1: Synchronous (No Redis Required)

**Use when:** Testing locally without Redis

**Setup:**
```bash
# Set environment variable
export USE_CELERY=false

# Start backend
cd backend
python -m uvicorn app.main:app --reload
```

**Behavior:**
- Evaluation runs inline (blocks HTTP request)
- No task queue needed
- Slower response times (~2-5 seconds)
- Good for development/testing

---

### Mode 2: Asynchronous (Celery + Redis)

**Use when:** Production or realistic testing

**Setup:**

1. **Start Redis:**
```bash
redis-server
```

2. **Start Celery Worker:**
```bash
cd backend
celery -A celery_worker worker --loglevel=info --pool=solo
```

3. **Start Backend:**
```bash
# Set environment variable (or omit, defaults to true)
export USE_CELERY=true

python -m uvicorn app.main:app --reload
```

**Behavior:**
- Evaluation runs asynchronously in background
- Fast HTTP response (~100ms)
- Status polling required
- Production-ready

---

## API Usage

### 1. Create Blog

```bash
POST /blogs
{
  "name": "My Blog Post"
}

# Response:
{
  "id": "uuid-here",
  "name": "My Blog Post",
  "created_at": "2026-01-31T10:00:00Z"
}
```

### 2. Create Version (Paste Content)

```bash
POST /blogs/{blog_id}/versions
{
  "content": "Your pasted blog content here...",
  "source": "human_paste"
}

# Response:
{
  "id": "version-uuid",
  "blog_id": "blog-uuid",
  "version_number": 1,
  "source": "human_paste",
  "created_at": "2026-01-31T10:01:00Z"
}
```

### 3. Trigger Evaluation

```bash
POST /evaluation-runs
{
  "blog_id": "blog-uuid",
  "version_id": "version-uuid"
}

# Response:
{
  "job_id": "run-uuid",
  "status": "queued",
  "eta_seconds": 30
}
```

### 4. Poll Evaluation Status

```bash
GET /evaluation-runs/{run_id}

# Response (queued):
{
  "run_id": "run-uuid",
  "status": "queued",
  "ai_likeness_score": null,
  "aeo_score": null,
  "completed_at": null
}

# Response (completed):
{
  "run_id": "run-uuid",
  "status": "completed",
  "ai_likeness_score": 23.5,
  "aeo_score": 68.0,
  "completed_at": "2026-01-31T10:01:30Z"
}
```

---

## Verification

### Test Synchronous Mode

```bash
# 1. Start backend with USE_CELERY=false
export USE_CELERY=false
python -m uvicorn app.main:app --reload

# 2. Create blog and version via API
# 3. Trigger evaluation
# 4. Check logs for inline execution
```

**Expected logs:**
```
INFO: Starting full evaluation: run_id=... version_id=...
INFO: Running AI Likeness detection...
INFO: AI Likeness detection completed successfully
INFO: Running AEO scoring...
INFO: AEO scoring completed successfully
INFO: Full evaluation completed: run_id=...
```

### Test Asynchronous Mode

```bash
# 1. Start Redis
redis-server

# 2. Start Celery worker
celery -A celery_worker worker --loglevel=info --pool=solo

# 3. Start backend with USE_CELERY=true
export USE_CELERY=true
python -m uvicorn app.main:app --reload

# 4. Trigger evaluation via API
# 5. Check Celery worker logs
```

**Expected Celery logs:**
```
[INFO] Task workflows.run_full_evaluation[uuid] received
[INFO] Starting full evaluation: run_id=...
[INFO] AI Likeness detection completed successfully
[INFO] AEO scoring completed successfully
[INFO] Task workflows.run_full_evaluation[uuid] succeeded
```

---

## Troubleshooting

### Issue: "Failed to create evaluation run"

**Cause:** Database migration not applied

**Fix:**
```bash
cd backend
alembic upgrade head
```

### Issue: Celery task not executing

**Cause:** Redis not running or Celery worker not started

**Fix:**
```bash
# Check Redis
redis-cli ping
# Should return: PONG

# Check Celery worker
celery -A celery_worker inspect active
# Should list active workers
```

### Issue: Scores not appearing

**Cause:** Evaluation failed or still processing

**Fix:**
1. Check evaluation_runs status: `GET /evaluation-runs/{run_id}`
2. Check backend logs for errors
3. Verify scoring workflows are working:
   ```bash
   # Test AI Likeness scoring
   pytest backend/tests/workflows/test_ai_detection.py
   
   # Test AEO scoring
   pytest backend/tests/workflows/test_aeo_scoring.py
   ```

---

## Regulatory Compliance Checklist

✅ **INSERT-ONLY Operations**
- All evaluation data uses INSERT statements
- No UPDATE/DELETE on score tables
- Status transitions via allowed columns only

✅ **Deterministic Scoring**
- Same content = same scores
- No ML inference
- Regex/structure-based only

✅ **Full Audit Trail**
- Every evaluation logged in `evaluation_runs`
- Scores linked to evaluation runs
- Human trigger recorded (`triggered_by`)

✅ **Idempotent Tasks**
- Safe to retry
- Duplicate detection in scoring workflows
- No side effects on re-execution

✅ **Human-Initiated Only**
- Evaluation requires explicit API call
- No auto-evaluation
- No background triggers

---

## Performance Characteristics

### Synchronous Mode
- **Response time:** 2-5 seconds (blocking)
- **Throughput:** ~1 evaluation/second
- **Resource usage:** Low (single process)

### Asynchronous Mode
- **Response time:** ~100ms (non-blocking)
- **Throughput:** ~10 evaluations/second
- **Resource usage:** Medium (Celery worker + Redis)

### Scoring Time
- **AI Likeness:** ~500ms - 1s
- **AEO Scoring:** ~500ms - 1s
- **Total:** ~1-2 seconds per evaluation

---

## Next Steps

1. **Frontend Integration:** Update frontend to poll `/evaluation-runs/{run_id}`
2. **Error Handling:** Add retry logic for transient failures
3. **Monitoring:** Set up alerts for failed evaluations
4. **Scaling:** Add more Celery workers for higher throughput
