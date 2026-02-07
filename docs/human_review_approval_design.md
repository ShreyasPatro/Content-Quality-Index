# Human Review and Approval Workflow Design (Stage 8)

**Status:** DESIGN FREEZE CANDIDATE
**Version:** 1.0.0
**Date:** 2026-01-29
**Auditor:** Antigravity (Hostile Backend Architect)

## Executive Summary
This document defines a **human-controlled review and approval workflow** that enforces irreversible human authority over publishing decisions. The system prevents AI automation, enforces minimum review durations, and maintains immutable audit trails.

---

## 1️⃣ Review State Machine

### 1.1 State Definitions
```
DRAFT → IN_REVIEW → APPROVED
                  → REJECTED
                  → ARCHIVED
```

### 1.2 State Transition Rules
| From State | To State | Trigger | Requirements |
| :--- | :--- | :--- | :--- |
| `DRAFT` | `IN_REVIEW` | Human action: "Submit for Review" | Version must exist |
| `IN_REVIEW` | `APPROVED` | Human action: "Approve" | Min review time elapsed + rationale |
| `IN_REVIEW` | `REJECTED` | Human action: "Reject" | Rationale required |
| `IN_REVIEW` | `ARCHIVED` | System/Human: "Archive" | Escalation or abandonment |
| `REJECTED` | `IN_REVIEW` | New version created | Parent linkage preserved |

### 1.3 Forbidden Transitions
❌ `DRAFT` → `APPROVED` (direct approval)
❌ `APPROVED` → `IN_REVIEW` (backward transition)
❌ `REJECTED` → `APPROVED` (same version)
❌ Any transition without human actor

### 1.4 State Machine Implementation
```python
class ReviewState(Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

ALLOWED_TRANSITIONS = {
    ReviewState.DRAFT: [ReviewState.IN_REVIEW],
    ReviewState.IN_REVIEW: [ReviewState.APPROVED, ReviewState.REJECTED, ReviewState.ARCHIVED],
    ReviewState.REJECTED: [],  # No direct transitions; new version required
    ReviewState.APPROVED: [],  # Terminal state
    ReviewState.ARCHIVED: [],  # Terminal state
}

def validate_transition(current_state, next_state):
    if next_state not in ALLOWED_TRANSITIONS.get(current_state, []):
        raise InvalidTransitionError(f"Cannot transition from {current_state} to {next_state}")
```

---

## 2️⃣ Timing Enforcement Strategy

### 2.1 Minimum Review Duration
**Requirement:** Approval/rejection blocked until minimum time elapsed.

**Configuration:**
```python
MIN_REVIEW_DURATION_SECONDS = 300  # 5 minutes (configurable per deployment)
```

### 2.2 Timer Mechanism
```python
class ReviewTimer:
    def __init__(self, version_id):
        self.version_id = version_id
        self.review_started_at = None  # System-generated timestamp
    
    def start_review(self):
        """Called when state transitions to IN_REVIEW."""
        self.review_started_at = datetime.utcnow()
    
    def can_approve_or_reject(self):
        """Check if minimum duration has elapsed."""
        if not self.review_started_at:
            return False
        
        elapsed = (datetime.utcnow() - self.review_started_at).total_seconds()
        return elapsed >= MIN_REVIEW_DURATION_SECONDS
    
    def time_remaining(self):
        """Return seconds remaining before action allowed."""
        if not self.review_started_at:
            return MIN_REVIEW_DURATION_SECONDS
        
        elapsed = (datetime.utcnow() - self.review_started_at).total_seconds()
        return max(0, MIN_REVIEW_DURATION_SECONDS - elapsed)
```

### 2.3 Enforcement at API Level
```python
async def approve_version(version_id, reviewer_id, rationale):
    timer = await fetch_review_timer(version_id)
    
    if not timer.can_approve_or_reject():
        raise ReviewTimerError(
            f"Approval blocked. {timer.time_remaining():.0f} seconds remaining."
        )
    
    # Proceed with approval
    await record_approval(version_id, reviewer_id, rationale)
```

---

## 3️⃣ Approval & Override Logging

### 3.1 Table: `review_actions`
```sql
CREATE TABLE review_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version_id UUID NOT NULL REFERENCES blog_versions(id),
    
    -- Human Actor (CRITICAL)
    reviewer_id UUID NOT NULL REFERENCES users(id),
    reviewer_role TEXT NOT NULL,  -- 'editor', 'senior_editor', 'admin'
    
    -- Action Details
    action_type TEXT NOT NULL,  -- 'approve', 'reject', 'override', 'archive'
    rationale TEXT NOT NULL,
    
    -- Timing
    action_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    review_started_at TIMESTAMP,  -- When IN_REVIEW state began
    review_duration_seconds INTEGER,  -- Calculated: action_timestamp - review_started_at
    
    -- Override Context (if applicable)
    is_override BOOLEAN NOT NULL DEFAULT FALSE,
    override_reason TEXT,  -- Required if is_override = TRUE
    risk_acceptance_note TEXT,  -- Required if is_override = TRUE
    
    -- Version Lineage
    parent_version_id UUID REFERENCES blog_versions(id),
    
    -- Immutability
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT chk_rationale_not_empty CHECK (LENGTH(rationale) > 0),
    CONSTRAINT chk_override_requires_reason CHECK (
        (is_override = FALSE) OR 
        (is_override = TRUE AND override_reason IS NOT NULL AND risk_acceptance_note IS NOT NULL)
    )
);

CREATE INDEX idx_review_actions_version ON review_actions(version_id);
CREATE INDEX idx_review_actions_reviewer ON review_actions(reviewer_id);
```

### 3.2 Insert-Only Semantics
- Each action creates a **new row**
- NO updates or deletes allowed
- `rationale`, `override_reason`, and `risk_acceptance_note` are immutable

### 3.3 Human Identity Verification
```python
async def verify_human_reviewer(reviewer_id):
    """Ensure reviewer is a human user, not a service account."""
    user = await fetch_user(reviewer_id)
    
    if user.account_type in ['service', 'system', 'bot']:
        raise ForbiddenReviewerError(
            f"User {reviewer_id} is not a human reviewer (type: {user.account_type})"
        )
    
    if not user.has_permission('review_content'):
        raise InsufficientPermissionsError(
            f"User {reviewer_id} lacks 'review_content' permission"
        )
    
    return user
```

---

## 4️⃣ Manual Edit Handling

### 4.1 Edit During Review Rule
**Principle:** Any edit during review creates a new version.

### 4.2 Workflow
```
1. Version v3 is IN_REVIEW
2. Reviewer makes manual edit
3. System creates v4 with:
   - parent_version_id = v3.id
   - state = DRAFT
4. v3 state remains IN_REVIEW (immutable)
5. Reviewer must submit v4 for review
6. Review timer restarts for v4
```

### 4.3 Implementation
```python
async def edit_version_during_review(version_id, reviewer_id, new_content):
    """Handle manual edit during review."""
    parent_version = await fetch_version(version_id)
    
    if parent_version.review_state != ReviewState.IN_REVIEW:
        raise InvalidStateError("Version is not in review")
    
    # Create new version
    new_version = await create_blog_version(
        blog_id=parent_version.blog_id,
        content=new_content,
        parent_version_id=version_id,
        review_state=ReviewState.DRAFT,
        edited_by=reviewer_id
    )
    
    # Log the edit action
    await log_review_action(
        version_id=new_version.id,
        reviewer_id=reviewer_id,
        action_type="manual_edit",
        rationale=f"Edited during review of v{parent_version.version_number}",
        parent_version_id=version_id
    )
    
    return new_version
```

---

## 5️⃣ Loop-Breaking & Escalation Rules

### 5.1 Maximum Review Cycles
**Constraint:** Prevent infinite reject → rewrite → review loops.

```python
MAX_REVIEW_CYCLES_PER_BLOG = 5
```

### 5.2 Cycle Counting Logic
```python
async def count_review_cycles(blog_id):
    """Count number of review cycles for a blog."""
    # A cycle = submission to IN_REVIEW
    cycles = await db.execute(
        """
        SELECT COUNT(DISTINCT version_id)
        FROM review_actions
        WHERE version_id IN (
            SELECT id FROM blog_versions WHERE blog_id = :blog_id
        )
        AND action_type = 'submit_for_review'
        """,
        {"blog_id": blog_id}
    )
    return cycles.scalar()
```

### 5.3 Escalation Trigger
```python
async def check_escalation_required(blog_id):
    """Determine if escalation is required."""
    cycles = await count_review_cycles(blog_id)
    
    if cycles >= MAX_REVIEW_CYCLES_PER_BLOG:
        return True, "max_cycles_reached"
    
    # Check for repeated rejections by same reviewer
    recent_rejections = await db.execute(
        """
        SELECT COUNT(*)
        FROM review_actions
        WHERE version_id IN (
            SELECT id FROM blog_versions WHERE blog_id = :blog_id
        )
        AND action_type = 'reject'
        AND action_timestamp > NOW() - INTERVAL '7 days'
        """,
        {"blog_id": blog_id}
    )
    
    if recent_rejections.scalar() >= 3:
        return True, "repeated_rejections"
    
    return False, None
```

### 5.4 Escalation Actions
| Escalation Reason | Action | Outcome |
| :--- | :--- | :--- |
| `max_cycles_reached` | Assign to senior reviewer | Override or archive |
| `repeated_rejections` | Assign to different reviewer | Fresh perspective |
| `stale_review` (>7 days in review) | Auto-archive | Terminal state |

### 5.5 Escalation Logging
```sql
CREATE TABLE review_escalations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blog_id UUID NOT NULL REFERENCES blogs(id),
    version_id UUID NOT NULL REFERENCES blog_versions(id),
    
    escalation_reason TEXT NOT NULL,
    escalated_from_reviewer_id UUID REFERENCES users(id),
    escalated_to_reviewer_id UUID REFERENCES users(id),
    
    escalation_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    resolution_action TEXT,  -- 'override_approved', 'archived', 'reassigned'
    resolution_timestamp TIMESTAMP,
    
    UNIQUE(version_id, escalation_timestamp)
);
```

---

## 6️⃣ End-to-End Audit Trail Example

### 6.1 Scenario: v3 → Approved

**Timeline:**
```
T0: v3 created (state = DRAFT)
T1: Editor submits v3 for review (state = IN_REVIEW, timer starts)
T2: Editor attempts approval at T1 + 2 min → BLOCKED (min 5 min required)
T3: Editor approves at T1 + 6 min → SUCCESS
```

### 6.2 Database Records

**`blog_versions` table:**
```json
{
  "id": "v3-uuid",
  "blog_id": "blog-123",
  "version_number": 3,
  "content": "[content]",
  "review_state": "approved",
  "parent_version_id": "v2-uuid",
  "created_at": "2026-01-29T10:00:00Z"
}
```

**`review_actions` table:**
```json
[
  {
    "id": "action-1",
    "version_id": "v3-uuid",
    "reviewer_id": "user-456",
    "reviewer_role": "editor",
    "action_type": "submit_for_review",
    "rationale": "Ready for review after AEO improvements",
    "action_timestamp": "2026-01-29T10:05:00Z",
    "review_started_at": "2026-01-29T10:05:00Z",
    "is_override": false
  },
  {
    "id": "action-2",
    "version_id": "v3-uuid",
    "reviewer_id": "user-456",
    "reviewer_role": "editor",
    "action_type": "approve",
    "rationale": "Content meets AEO standards and AI-likeness is acceptable",
    "action_timestamp": "2026-01-29T10:11:00Z",
    "review_started_at": "2026-01-29T10:05:00Z",
    "review_duration_seconds": 360,
    "is_override": false
  }
]
```

### 6.3 Audit Query
```sql
-- Reconstruct approval timeline for v3
SELECT 
    ra.action_type,
    ra.action_timestamp,
    ra.review_duration_seconds,
    u.email AS reviewer_email,
    ra.rationale,
    ra.is_override
FROM review_actions ra
JOIN users u ON ra.reviewer_id = u.id
WHERE ra.version_id = 'v3-uuid'
ORDER BY ra.action_timestamp;
```

---

## 7️⃣ Acceptance Checklist

- ✅ Human dominance provable in logs (`reviewer_id` FK to `users`)
- ✅ Review duration objectively enforced (system-generated timestamps)
- ✅ Notes immutable and non-editable (INSERT-ONLY table)
- ✅ Reviewer accountability explicit (`reviewer_role`, `rationale`)
- ✅ System can block rubber-stamping (minimum review duration)
- ✅ Infinite rewrite/review loops impossible (max cycles + escalation)

---

## 8️⃣ Forbidden Behavior

The following are **EXPLICITLY PROHIBITED**:

❌ AI-initiated approvals or rejections
❌ Service accounts as reviewers
❌ Bypassing minimum review duration
❌ Editing `rationale` or `override_reason` after submission
❌ Direct `DRAFT` → `APPROVED` transitions
❌ Backward state transitions
❌ Deleting or updating `review_actions` rows

---

## 9️⃣ Safety Guarantees

1. **Human Authority:** Every approval requires authenticated human user
2. **Timing Integrity:** System-enforced minimum review duration
3. **Immutability:** All review actions are append-only
4. **Traceability:** Complete audit trail from draft to approval
5. **Loop Prevention:** Max cycles + escalation prevents infinite loops
6. **Version Integrity:** Manual edits create new versions, preserving lineage

---

## 🔒 Certification Status

**Status:** DESIGN FREEZE CANDIDATE
**Compliance:** Human-controlled, audit-grade, immutable
**Ready for:** Backend implementation, compliance review, external audit

**Signed:** Antigravity (Hostile Backend Architect)
**Date:** 2026-01-29
