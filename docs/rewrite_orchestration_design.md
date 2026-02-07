# Rewrite Orchestration System Design (Stage 7)

**Status:** DESIGN FREEZE CANDIDATE
**Version:** 1.0.0
**Date:** 2026-01-29
**Auditor:** Antigravity (Hostile Backend Architect)

## Executive Summary
This document defines a **deterministic, explainable Rewrite Orchestration System** that uses Claude 4.5 Sonnet as a controlled rewrite engine. The system operates exclusively on versioned blog content and explicit scoring signals. All decisions are loggable, reproducible, and auditable.

---

## 1️⃣ Rewrite Trigger Rules

### 1.1 Trigger Conditions
A rewrite is triggered if **ANY** of the following conditions are met:

| Trigger ID | Condition | Trigger Type | Trigger Data |
| :--- | :--- | :--- | :--- |
| **T1** | `aeo_total < 70.0` | `aeo_total_low` | `{"aeo_total": <value>}` |
| **T2** | `aeo_answerability < 15.0` | `aeo_pillar_critical` | `{"pillar": "answerability", "score": <value>, "min": 15.0}` |
| **T3** | `aeo_structure < 12.0` | `aeo_pillar_critical` | `{"pillar": "structure", "score": <value>, "min": 12.0}` |
| **T4** | `ai_likeness_total > 60.0` | `ai_likeness_high` | `{"ai_likeness_total": <value>}` |
| **T5** | Any AI rubric category > 70.0 | `ai_category_critical` | `{"category": <name>, "score": <value>}` |

### 1.2 Trigger Evaluation Logic
```python
def evaluate_triggers(aeo_scores, ai_likeness_scores):
    triggers = []
    
    if aeo_scores.aeo_total < 70.0:
        triggers.append({
            "trigger_type": "aeo_total_low",
            "trigger_reason": f"AEO total score {aeo_scores.aeo_total} below threshold 70.0",
            "trigger_data": {"aeo_total": aeo_scores.aeo_total}
        })
    
    if aeo_scores.aeo_answerability < 15.0:
        triggers.append({
            "trigger_type": "aeo_pillar_critical",
            "trigger_reason": f"Answerability score {aeo_scores.aeo_answerability} below minimum 15.0",
            "trigger_data": {"pillar": "answerability", "score": aeo_scores.aeo_answerability, "min": 15.0}
        })
    
    # ... (similar for other triggers)
    
    return triggers
```

### 1.3 No-Rewrite Conditions
If `len(triggers) == 0`, log:
```json
{
  "rewrite_required": false,
  "reason": "All quality thresholds met",
  "aeo_total": <value>,
  "ai_likeness_total": <value>
}
```

---

## 2️⃣ Locked Rewrite Prompt Template

### 2.1 Canonical Template
```
You are a content rewriter. Your task is to rewrite the following blog post to address specific quality issues.

ORIGINAL CONTENT:
---
{original_content}
---

REQUIRED FIXES:
{fix_instructions}

STRICT PROHIBITIONS:
- Do NOT add new facts, statistics, or claims not present in the original
- Do NOT change the core message or argument
- Do NOT alter technical accuracy
- Do NOT expand content length by more than 10%
- Do NOT change tone unless explicitly instructed

OUTPUT REQUIREMENTS:
- Return ONLY the rewritten content
- Maintain markdown formatting
- Preserve all existing citations and links

Begin rewrite:
```

### 2.2 Fix Instructions Generation
Fix instructions are derived **deterministically** from triggered rules and pillar scores:

```python
def generate_fix_instructions(triggers, aeo_scores, ai_likeness_scores):
    instructions = []
    
    for trigger in triggers:
        if trigger["trigger_type"] == "aeo_pillar_critical":
            pillar = trigger["trigger_data"]["pillar"]
            if pillar == "answerability":
                instructions.append("- Move the direct answer to the first paragraph (within first 120 words)")
            elif pillar == "structure":
                instructions.append("- Add H2/H3 headers to break up content")
                instructions.append("- Convert key points into bullet lists")
        
        elif trigger["trigger_type"] == "ai_likeness_high":
            instructions.append("- Vary sentence structure to reduce AI-like patterns")
            instructions.append("- Add specific examples and concrete details")
    
    return "\n".join(instructions)
```

### 2.3 Prompt Storage
The **filled prompt** (with all variables substituted) MUST be stored verbatim in `rewrite_cycles.rewrite_prompt`.

---

## 3️⃣ Rewrite Execution Flow

### 3.1 Sequence Diagram
```
1. Fetch parent_version (blog_versions.id)
2. Fetch aeo_scores (WHERE run_id = parent_run_id)
3. Fetch ai_likeness_rubric_scores (WHERE run_id = parent_run_id)
4. Evaluate triggers → triggers[]
5. IF triggers.length == 0:
     → Log "no_rewrite_required"
     → STOP
6. Generate fix_instructions from triggers
7. Fill rewrite_prompt template
8. Store rewrite_prompt in rewrite_cycles
9. Call Claude API with filled prompt
10. Store response as new blog_version (child)
11. Link parent_version_id → child_version_id
12. Increment rewrite_cycle_number
13. Create new evaluation_run for child version
```

### 3.2 Pseudocode
```python
async def execute_rewrite(parent_version_id):
    # Step 1-3: Fetch data
    parent = await fetch_blog_version(parent_version_id)
    aeo = await fetch_aeo_scores(parent.evaluation_run_id)
    ai_likeness = await fetch_ai_likeness_scores(parent.evaluation_run_id)
    
    # Step 4-5: Evaluate
    triggers = evaluate_triggers(aeo, ai_likeness)
    if not triggers:
        await log_no_rewrite(parent_version_id)
        return None
    
    # Step 6-7: Generate prompt
    fix_instructions = generate_fix_instructions(triggers, aeo, ai_likeness)
    filled_prompt = REWRITE_TEMPLATE.format(
        original_content=parent.content,
        fix_instructions=fix_instructions
    )
    
    # Step 8: Store cycle
    cycle = await create_rewrite_cycle(
        parent_version_id=parent_version_id,
        rewrite_prompt=filled_prompt,
        trigger_reasons=[t["trigger_reason"] for t in triggers]
    )
    
    # Step 9: Call Claude
    rewritten_content = await call_claude(filled_prompt)
    
    # Step 10-11: Create child version
    child_version = await create_blog_version(
        blog_id=parent.blog_id,
        content=rewritten_content,
        parent_version_id=parent_version_id
    )
    
    # Step 12-13: Update cycle and trigger evaluation
    await update_cycle_with_child(cycle.id, child_version.id)
    await trigger_evaluation_run(child_version.id)
    
    return child_version.id
```

---

## 4️⃣ Trend Analysis Logic

### 4.1 Comparison Metrics
Compare parent vs child on:
- `aeo_total_delta = child.aeo_total - parent.aeo_total`
- `ai_likeness_delta = parent.ai_likeness_total - child.ai_likeness_total` (note: lower is better)

### 4.2 Trend Classification Rules
| Condition | Trend Outcome | Numeric Code |
| :--- | :--- | :--- |
| `aeo_total_delta >= 5.0 AND ai_likeness_delta >= 5.0` | `improving` | 1 |
| `aeo_total_delta >= 5.0 AND ai_likeness_delta < 5.0` | `partial_improvement` | 2 |
| `-5.0 < aeo_total_delta < 5.0` | `stagnant` | 3 |
| `aeo_total_delta < -5.0 OR ai_likeness_delta < -5.0` | `regressing` | 4 |

### 4.3 Implementation
```python
def classify_trend(parent_aeo, child_aeo, parent_ai, child_ai):
    aeo_delta = child_aeo - parent_aeo
    ai_delta = parent_ai - child_ai  # Lower AI score is better
    
    if aeo_delta >= 5.0 and ai_delta >= 5.0:
        return "improving", 1
    elif aeo_delta >= 5.0:
        return "partial_improvement", 2
    elif -5.0 < aeo_delta < 5.0:
        return "stagnant", 3
    else:
        return "regressing", 4
```

---

## 5️⃣ Loop-Breaking & Safety Controls

### 5.1 Hard Stop Conditions
| Stop ID | Condition | Stop Reason | Action |
| :--- | :--- | :--- | :--- |
| **S1** | `rewrite_cycle_number >= 3` | `max_cycles_reached` | Mark terminal, stop |
| **S2** | Trend = `stagnant` for 2 consecutive cycles | `no_improvement` | Mark terminal, stop |
| **S3** | Trend = `regressing` | `quality_degradation` | Mark terminal, stop |
| **S4** | Oscillation detected (score variance < 3.0 across 3 cycles) | `oscillation_detected` | Mark terminal, stop |

### 5.2 Stop Logic
```python
def should_stop_rewriting(cycle_history):
    latest_cycle = cycle_history[-1]
    
    # S1: Max cycles
    if latest_cycle.cycle_number >= 3:
        return True, "max_cycles_reached"
    
    # S2: Stagnant
    if len(cycle_history) >= 2:
        if cycle_history[-1].trend == "stagnant" and cycle_history[-2].trend == "stagnant":
            return True, "no_improvement"
    
    # S3: Regression
    if latest_cycle.trend == "regressing":
        return True, "quality_degradation"
    
    # S4: Oscillation
    if len(cycle_history) >= 3:
        scores = [c.child_aeo_total for c in cycle_history[-3:]]
        if max(scores) - min(scores) < 3.0:
            return True, "oscillation_detected"
    
    return False, None
```

---

## 6️⃣ Data Model Requirements

### 6.1 Table: `rewrite_cycles`
```sql
CREATE TABLE rewrite_cycles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_version_id UUID NOT NULL REFERENCES blog_versions(id),
    child_version_id UUID REFERENCES blog_versions(id),
    cycle_number INTEGER NOT NULL,
    
    -- Trigger Context
    trigger_reasons JSONB NOT NULL,
    trigger_data JSONB NOT NULL,
    
    -- Prompt Storage (CRITICAL)
    rewrite_prompt TEXT NOT NULL,
    
    -- Trend Analysis
    parent_aeo_total NUMERIC(5,2),
    child_aeo_total NUMERIC(5,2),
    parent_ai_likeness NUMERIC(5,2),
    child_ai_likeness NUMERIC(5,2),
    trend_outcome TEXT,
    trend_code INTEGER,
    
    -- Loop Control
    rewrite_status TEXT NOT NULL DEFAULT 'pending', -- pending | completed | terminal
    stop_reason TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(parent_version_id, cycle_number)
);
```

### 6.2 Insert-Only Semantics
- Each rewrite creates a **new row** in `rewrite_cycles`.
- `rewrite_status` transitions: `pending` → `completed` (or `terminal`).
- NO updates to `rewrite_prompt`, `trigger_reasons`, or scores.

---

## 7️⃣ Worked Example: v2 → v3

### 7.1 Input State
**Version v2 Scores:**
- `aeo_total = 65.0`
- `aeo_answerability = 12.0` ⚠️
- `aeo_structure = 18.0`
- `ai_likeness_total = 45.0`

### 7.2 Trigger Evaluation
```json
[
  {
    "trigger_type": "aeo_total_low",
    "trigger_reason": "AEO total score 65.0 below threshold 70.0",
    "trigger_data": {"aeo_total": 65.0}
  },
  {
    "trigger_type": "aeo_pillar_critical",
    "trigger_reason": "Answerability score 12.0 below minimum 15.0",
    "trigger_data": {"pillar": "answerability", "score": 12.0, "min": 15.0}
  }
]
```

### 7.3 Generated Rewrite Prompt
```
You are a content rewriter. Your task is to rewrite the following blog post to address specific quality issues.

ORIGINAL CONTENT:
---
[v2 content here]
---

REQUIRED FIXES:
- Move the direct answer to the first paragraph (within first 120 words)

STRICT PROHIBITIONS:
- Do NOT add new facts, statistics, or claims not present in the original
- Do NOT change the core message or argument
- Do NOT alter technical accuracy
- Do NOT expand content length by more than 10%
- Do NOT change tone unless explicitly instructed

OUTPUT REQUIREMENTS:
- Return ONLY the rewritten content
- Maintain markdown formatting
- Preserve all existing citations and links

Begin rewrite:
```

### 7.4 Expected Outcome
**Version v3 Created:**
- `parent_version_id = v2.id`
- `content = [Claude's rewritten output]`

**Rewrite Cycle Record:**
```json
{
  "cycle_number": 1,
  "parent_version_id": "v2-uuid",
  "child_version_id": "v3-uuid",
  "rewrite_prompt": "[full prompt above]",
  "trigger_reasons": ["AEO total score 65.0 below threshold 70.0", "Answerability score 12.0 below minimum 15.0"]
}
```

### 7.5 Trend Decision (After v3 Evaluation)
**Assume v3 Scores:**
- `aeo_total = 72.0` (+7.0)
- `ai_likeness_total = 42.0` (-3.0)

**Trend Classification:**
- `aeo_delta = 7.0` ✅
- `ai_delta = 3.0` ✅
- **Outcome:** `improving` (code 1)

**Decision:** Continue monitoring. If v3 still has triggers, proceed to cycle 2.

---

## 8️⃣ Forbidden Behavior

The following are **EXPLICITLY PROHIBITED**:

❌ Claude deciding what to fix (must be derived from triggers)
❌ Claude changing facts or adding new information
❌ Claude adjusting tone unless explicitly instructed
❌ Claude summarizing signals or scores
❌ Claude running multiple drafts or iterations
❌ Any AI scoring within this stage
❌ Silent retries or hidden rewrite attempts
❌ Hallucinated improvement goals

---

## 9️⃣ Acceptance Checklist

- ✅ Rewrite prompt stored verbatim
- ✅ Trigger reason logged
- ✅ Parent version linked
- ✅ Trend-based continuation or stop
- ✅ Max rewrite cycles enforced (3)
- ✅ No black-box logic
- ✅ Fully auditable

---

## 🔒 Certification Status

**Status:** DESIGN FREEZE CANDIDATE
**Compliance:** Audit-grade, deterministic, explainable
**Ready for:** Backend implementation, compliance review, external audit

**Signed:** Antigravity (Hostile Backend Architect)
**Date:** 2026-01-29
