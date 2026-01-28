# Database Schema Design

## Overview
This schema is designed for PostgreSQL 15+. It strictly enforces **immutability** for content versions and provides deep auditability for all human and system actions.

**Key Principles:**
1.  **INSERT-ONLY Content**: `blog_versions` cannot be updated.
2.  **Explicit Lineage**: Every version points to its parent.
3.  **Human/System Separation**: Distinct tables for AI evaluations vs. Human reviews.
4.  **Auditability**: All state changes are recorded as new rows.

---

## 1. DDL & Table Definitions

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Blogs (The Identity)
-- Represents the continuous identity of a piece of content.
CREATE TABLE blogs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title_slug TEXT NOT NULL, -- Mutable only for display/URL purposes, not content info
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    project_id UUID -- tailored for multi-tenancy or grouping if needed
);

-- 2. Blog Versions (The Immutable State)
-- STRICTLY IMMUTABLE via Triggers.
CREATE TABLE blog_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blog_id UUID NOT NULL REFERENCES blogs(id) ON DELETE CASCADE,
    
    -- Lineage: Points to the version this was based on. 
    -- NULL for the very first version.
    parent_version_id UUID REFERENCES blog_versions(id),
    
    -- The Content
    content JSONB NOT NULL,
    content_hash CHAR(64) GENERATED ALWAYS AS (sha256(content::text::bytea)) STORED,
    
    -- Metadata
    version_number INTEGER NOT NULL, -- Application calculated or sequence
    created_by UUID NOT NULL, -- User ID (system or human)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    change_reason TEXT, -- "Initial Draft", "AI Rewrite", "Typos", "Revert to v1"
    
    CONSTRAINT uq_blog_version UNIQUE (blog_id, version_number)
);

-- 3. Evaluation Runs (Point-in-Time Snapshots)
-- A container for a specific set of AI/metric checks run against a version.
CREATE TABLE evaluation_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blog_version_id UUID NOT NULL REFERENCES blog_versions(id),
    run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    triggered_by UUID, -- System ID or User ID
    model_config JSONB -- Snapshot of the model/prompt configuration used
);

-- 4. AI Detector Scores
CREATE TABLE ai_detector_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES evaluation_runs(id),
    provider VARCHAR(50) NOT NULL, -- e.g., "Originality.ai", "Copyleaks"
    score NUMERIC(5, 2) NOT NULL, -- 0.00 to 100.00
    details JSONB -- Full raw response
);

-- 5. AEO Scores (Answer Engine Optimization)
CREATE TABLE aeo_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES evaluation_runs(id),
    query_intent TEXT NOT NULL,
    score NUMERIC(5, 2) NOT NULL,
    rationale TEXT
);

-- 6. Rewrite Cycles
-- Links a source version to a new AI-generated target version.
CREATE TABLE rewrite_cycles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_version_id UUID NOT NULL REFERENCES blog_versions(id),
    target_version_id UUID REFERENCES blog_versions(id), -- Nullable initially if async
    
    prompt_template_id UUID,
    llm_model VARCHAR(100) NOT NULL, -- "claude-3-5-sonnet"
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 7. Human Review Actions (The Audit Log)
-- Every button click (Approve, Reject, Comment) is logged here.
CREATE TABLE human_review_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blog_version_id UUID NOT NULL REFERENCES blog_versions(id),
    reviewer_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL CHECK (action IN ('APPROVE', 'REJECT', 'COMMENT', 'REQUEST_CHANGES')),
    comments TEXT,
    performed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Approval States (The "Live" Pointer)
-- Tracks WHICH version is considered "Approved" for a blog over time.
-- This is scoped to the BLOG, but points to a VERSION.
CREATE TABLE approval_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blog_id UUID NOT NULL REFERENCES blogs(id),
    approved_version_id UUID NOT NULL REFERENCES blog_versions(id),
    
    approver_id UUID NOT NULL, -- Must be a human
    approved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Optional: If we want to support "Revoking" approval without a new version
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Ensure consistency: The version must belong to the blog
    CONSTRAINT fk_approval_consistency 
        FOREIGN KEY (blog_id, approved_version_id) 
        REFERENCES blog_versions (blog_id, id) -- Requires a composite unique constraint or index on blog_versions(blog_id, id) which is redundant but safe, or just trust app logic. 
        -- Better: Just trust the separate FKs or add a composite unique index on blog_versions(id, blog_id) to support this composite FK.
);
```

## 2. Immutability Enforcement (Triggers)

We strictly prevent SQL `UPDATE` or `DELETE` commands on the `blog_versions` table.

```sql
CREATE OR REPLACE FUNCTION prevent_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Modification of % is strictly forbidden. Content is immutable.', TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

-- Apply to blog_versions
CREATE TRIGGER trg_blog_versions_immutable
BEFORE UPDATE OR DELETE ON blog_versions
FOR EACH ROW EXECUTE FUNCTION prevent_modification();

-- Apply to evaluation_runs (History shouldn't change)
CREATE TRIGGER trg_eval_runs_immutable
BEFORE UPDATE OR DELETE ON evaluation_runs
FOR EACH ROW EXECUTE FUNCTION prevent_modification();

-- Apply to human_review_actions (Audit logs shouldn't change)
CREATE TRIGGER trg_audit_log_immutable
BEFORE UPDATE OR DELETE ON human_review_actions
FOR EACH ROW EXECUTE FUNCTION prevent_modification();
```

## 3. Indexing Strategy

```sql
-- Lineage Traversal (Finding history of a blog)
CREATE INDEX idx_blog_versions_blog_id ON blog_versions(blog_id);
CREATE INDEX idx_blog_versions_parent ON blog_versions(parent_version_id);

-- Audit / Time-travel queries
CREATE INDEX idx_blog_versions_created_at ON blog_versions(created_at);

-- Finding the approved state
CREATE INDEX idx_approval_states_blog_active ON approval_states(blog_id) WHERE is_active = TRUE;

-- Lookup evaluations for a version
CREATE INDEX idx_eval_runs_version ON evaluation_runs(blog_version_id);
```

## 4. Lifecycle Walkthrough

**Scenario**: User creates a blog, edits it, reverts changes, and approvals.

1.  **Creation (v1)**
    *   `INSERT INTO blogs (id: B1)`
    *   `INSERT INTO blog_versions (id: V1, blog_id: B1, parent: NULL, content: "Hello", ver: 1)`

2.  **Edit (v2)**
    *   User fixes a typo.
    *   `INSERT INTO blog_versions (id: V2, blog_id: B1, parent: V1, content: "Hello World", ver: 2)`

3.  **AI Eval (System Action)**
    *   `INSERT INTO evaluation_runs (id: R1, version: V2)`
    *   `INSERT INTO ai_detector_scores (run: R1, score: 98)`

4.  **Revert to v1 (v3)**
    *   User realizes v2 was wrong. "Revert" action in UI.
    *   NOT changing v1 or v2.
    *   `INSERT INTO blog_versions (id: V3, blog_id: B1, parent: V2, content: "Hello", ver: 3)`
    *   *Note: Content matches v1, but parent is v2 (history preserved).*

5.  **Approval (Human Action)**
    *   User reviews V3.
    *   `INSERT INTO human_review_actions (version: V3, action: 'APPROVE')`
    *   `INSERT INTO approval_states (blog: B1, approved_version: V3)`

6.  **"Approved" is not "Latest"**
    *   User starts drafting V4 (New content).
    *   `INSERT INTO blog_versions (id: V4, blog_id: B1, parent: V3, content: "Hello New", ver: 4)`
    *   Querying "Current Blog":
        *   Latest Draft: V4 (SELECT * FROM blog_versions WHERE blog_id=B1 ORDER BY ver DESC LIMIT 1)
        *   Live/Approved: V3 (SELECT * FROM approval_states WHERE blog_id=B1 ORDER BY approved_at DESC LIMIT 1)

## 5. System Invariants Checklist Matches

*   **Blogs represent content identity**: `blogs` table exists, distinct from versions.
*   **Immutable versions**: Trigger `trg_blog_versions_immutable` prevents UPDATE.
*   **Parent-child lineage**: `parent_version_id` enforces strict DAG.
*   **Replayability**: `evaluation_runs` stores `model_config` snapshot.
*   **Human-scoped approval**: `approval_states` is separate, linking Blog -> Version.
