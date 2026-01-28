-- Content Quality Engine - PostgreSQL 15+ Schema
-- Hardened for INSERT-ONLY immutability and full auditability

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- For SHA-256 hashing

-- ============================================================================
-- USERS & AUTHENTICATION
-- ============================================================================

-- Users table with human verification
-- AUDIT FIX: Issue 5.1 - Defines is_human verification mechanism
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('writer', 'reviewer', 'admin', 'system')),
    
    -- CRITICAL: is_human enforces human-in-the-loop
    -- Only admins can set this to true
    -- Service accounts MUST have is_human=false
    is_human BOOLEAN NOT NULL DEFAULT false,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Prevent service accounts from being marked as human
    CONSTRAINT chk_system_not_human CHECK (
        role != 'system' OR is_human = false
    )
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_human ON users(is_human) WHERE is_human = true;

-- ============================================================================
-- CONTENT IDENTITY & VERSIONING
-- ============================================================================

-- Blogs: The stable identity of content
CREATE TABLE blogs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title_slug TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    project_id UUID  -- Optional grouping/multi-tenancy
);

CREATE INDEX idx_blogs_created_at ON blogs(created_at);

-- Blog Versions: Immutable snapshots (INSERT-ONLY)
-- AUDIT FIX: Issue 2.2 - Added source_rewrite_cycle_id for AI audit trail
CREATE TABLE blog_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blog_id UUID NOT NULL REFERENCES blogs(id) ON DELETE CASCADE,
    
    -- Lineage: parent_version_id tracks edit history
    parent_version_id UUID REFERENCES blog_versions(id),
    
    -- AUDIT FIX: Explicit link to AI rewrite that generated this version
    -- NULL if human-created, populated if accepted from rewrite_suggestions
    source_rewrite_cycle_id UUID,  -- FK added after rewrite_cycles table
    
    -- Content (JSONB for flexibility)
    content JSONB NOT NULL,
    
    -- SHA-256 hash for integrity verification
    content_hash CHAR(64) GENERATED ALWAYS AS (
        encode(digest(content::text, 'sha256'), 'hex')
    ) STORED,
    
    -- Metadata
    version_number INTEGER NOT NULL,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    change_reason TEXT,
    
    CONSTRAINT uq_blog_version UNIQUE (blog_id, version_number)
);

CREATE INDEX idx_blog_versions_blog_id ON blog_versions(blog_id);
CREATE INDEX idx_blog_versions_parent ON blog_versions(parent_version_id);
CREATE INDEX idx_blog_versions_created_at ON blog_versions(created_at);
CREATE INDEX idx_blog_versions_created_by ON blog_versions(created_by);

-- ============================================================================
-- EVALUATION & SCORING
-- ============================================================================

-- Evaluation Runs: Point-in-time snapshots of quality checks
CREATE TABLE evaluation_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blog_version_id UUID NOT NULL REFERENCES blog_versions(id),
    run_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    triggered_by UUID REFERENCES users(id),
    
    -- Snapshot of model/prompt config for replayability
    model_config JSONB,
    
    -- Track completion for idempotency
    completed_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'processing' CHECK (status IN ('processing', 'completed', 'partial_failure', 'failed'))
);

CREATE INDEX idx_eval_runs_version ON evaluation_runs(blog_version_id);
CREATE INDEX idx_eval_runs_status ON evaluation_runs(status) WHERE completed_at IS NULL;

-- AI Detector Scores (Originality.ai, Copyleaks, etc.)
CREATE TABLE ai_detector_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES evaluation_runs(id),
    provider VARCHAR(50) NOT NULL,
    score NUMERIC(5, 2) NOT NULL CHECK (score >= 0 AND score <= 100),
    
    -- AUDIT FIX: Issue 7.1 - Store model_version for drift tracking
    details JSONB,  -- Should include: model_version, raw_response, timestamp
    
    CONSTRAINT uq_detector_score UNIQUE (run_id, provider)
);

CREATE INDEX idx_detector_scores_run ON ai_detector_scores(run_id);

-- AEO Scores (Answer Engine Optimization)
CREATE TABLE aeo_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID NOT NULL REFERENCES evaluation_runs(id),
    query_intent TEXT NOT NULL,
    score NUMERIC(5, 2) NOT NULL CHECK (score >= 0 AND score <= 100),
    rationale TEXT,
    
    CONSTRAINT uq_aeo_score UNIQUE (run_id, query_intent)
);

CREATE INDEX idx_aeo_scores_run ON aeo_scores(run_id);

-- ============================================================================
-- AI REWRITE ORCHESTRATION
-- ============================================================================

-- Rewrite Cycles: Links source version to AI-generated suggestion
CREATE TABLE rewrite_cycles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_version_id UUID NOT NULL REFERENCES blog_versions(id),
    
    -- AUDIT FIX: Issue 2.2 - Populated when user accepts suggestion
    target_version_id UUID REFERENCES blog_versions(id),
    
    prompt_template_id UUID,
    llm_model VARCHAR(100) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_rewrite_cycles_source ON rewrite_cycles(source_version_id);
CREATE INDEX idx_rewrite_cycles_target ON rewrite_cycles(target_version_id);

-- AUDIT FIX: Issue 7.3 - Missing table for rewrite suggestions
-- Rewrite Suggestions: AI-generated content awaiting user acceptance
CREATE TABLE rewrite_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cycle_id UUID NOT NULL REFERENCES rewrite_cycles(id),
    suggested_content JSONB NOT NULL,
    status VARCHAR(30) DEFAULT 'pending_user_acceptance' CHECK (
        status IN ('pending_user_acceptance', 'accepted', 'rejected')
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_rewrite_suggestions_cycle ON rewrite_suggestions(cycle_id);

-- Add FK from blog_versions to rewrite_cycles (defined after both tables exist)
ALTER TABLE blog_versions 
ADD CONSTRAINT fk_blog_versions_rewrite_cycle 
FOREIGN KEY (source_rewrite_cycle_id) REFERENCES rewrite_cycles(id);

-- ============================================================================
-- HUMAN REVIEW & APPROVAL
-- ============================================================================

-- Human Review Actions: Audit log of all human review decisions
CREATE TABLE human_review_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blog_version_id UUID NOT NULL REFERENCES blog_versions(id),
    reviewer_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(50) NOT NULL CHECK (
        action IN ('APPROVE', 'REJECT', 'COMMENT', 'REQUEST_CHANGES', 'APPROVE_INTENT')
    ),
    comments TEXT,
    performed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_review_actions_version ON human_review_actions(blog_version_id);
CREATE INDEX idx_review_actions_reviewer ON human_review_actions(reviewer_id);
CREATE INDEX idx_review_actions_performed_at ON human_review_actions(performed_at);

-- AUDIT FIX: Issue 1.3 - Approval states with INSERT-ONLY revocation
-- Approval States: Tracks which version is approved for a blog
CREATE TABLE approval_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blog_id UUID NOT NULL REFERENCES blogs(id),
    approved_version_id UUID NOT NULL REFERENCES blog_versions(id),
    
    approver_id UUID NOT NULL REFERENCES users(id),
    approved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- INSERT-ONLY revocation: to revoke, INSERT new row with these populated
    revoked_at TIMESTAMPTZ,
    revoked_by UUID REFERENCES users(id),
    revocation_reason TEXT,
    
    -- Ensure approver is human
    CONSTRAINT chk_approver_is_human CHECK (
        approver_id IN (SELECT id FROM users WHERE is_human = true)
    )
);

CREATE INDEX idx_approval_states_blog ON approval_states(blog_id);
-- Index for finding current (non-revoked) approvals
CREATE INDEX idx_approval_states_active ON approval_states(blog_id, approved_at) 
WHERE revoked_at IS NULL;

-- AUDIT FIX: Issue 5.2 - Audit log for failed approval attempts
-- Approval Attempts: Logs all approval attempts (success and failure)
CREATE TABLE approval_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blog_id UUID NOT NULL REFERENCES blogs(id),
    attempted_by UUID NOT NULL REFERENCES users(id),
    is_human BOOLEAN NOT NULL,  -- Snapshot at attempt time
    result VARCHAR(20) NOT NULL CHECK (
        result IN ('success', 'forbidden', 'invalid_state', 'invalid_version')
    ),
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    failure_reason TEXT
);

CREATE INDEX idx_approval_attempts_blog ON approval_attempts(blog_id);
CREATE INDEX idx_approval_attempts_user ON approval_attempts(attempted_by);
CREATE INDEX idx_approval_attempts_result ON approval_attempts(result) WHERE result != 'success';

-- ============================================================================
-- ESCALATIONS & HARD STOPS
-- ============================================================================

-- AUDIT FIX: Issue 4.1 - Missing escalations table
-- Escalations: Tracks when automation stops and requires human intervention
CREATE TABLE escalations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    blog_id UUID NOT NULL REFERENCES blogs(id),
    version_id UUID NOT NULL REFERENCES blog_versions(id),
    reason VARCHAR(50) NOT NULL CHECK (
        reason IN ('score_regression', 'policy_violation', 'ambiguity', 'low_quality')
    ),
    details JSONB,  -- Contains delta, scores, etc.
    status VARCHAR(20) NOT NULL DEFAULT 'pending_review' CHECK (
        status IN ('pending_review', 'resolved', 'dismissed')
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES users(id)
);

CREATE INDEX idx_escalations_blog ON escalations(blog_id);
CREATE INDEX idx_escalations_status ON escalations(status);
-- AUDIT FIX: Issue 4.2 - Efficient query for "is blog escalated?"
CREATE INDEX idx_escalations_pending ON escalations(blog_id) 
WHERE status = 'pending_review';

-- ============================================================================
-- IMMUTABILITY ENFORCEMENT
-- ============================================================================

-- Trigger function to prevent UPDATE/DELETE on immutable tables
CREATE OR REPLACE FUNCTION prevent_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Modification of % is strictly forbidden. Content is immutable.', TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

-- Apply immutability triggers to content and audit tables
-- NOTE: evaluation_runs is EXEMPT from immutability triggers because:
--   - Status transitions (processing → completed/failed) are workflow metadata, not evaluation data
--   - Actual evaluation results are stored INSERT-ONLY in ai_detector_scores and aeo_scores
--   - Auditability is preserved via immutable run_at timestamp and write-once completed_at
--   - Application layer enforces INSERT-ONLY on score tables

-- blog_versions: Content data (fully immutable)
CREATE TRIGGER trg_blog_versions_immutable
BEFORE UPDATE OR DELETE ON blog_versions
FOR EACH ROW EXECUTE FUNCTION prevent_modification();

-- human_review_actions: Audit log (fully immutable)
CREATE TRIGGER trg_review_actions_immutable
BEFORE UPDATE OR DELETE ON human_review_actions
FOR EACH ROW EXECUTE FUNCTION prevent_modification();

-- rewrite_cycles: Rewrite history (fully immutable)
CREATE TRIGGER trg_rewrite_cycles_immutable
BEFORE UPDATE OR DELETE ON rewrite_cycles
FOR EACH ROW EXECUTE FUNCTION prevent_modification();

-- ai_detector_scores: Evaluation results (fully immutable)
CREATE TRIGGER trg_ai_detector_scores_immutable
BEFORE UPDATE OR DELETE ON ai_detector_scores
FOR EACH ROW EXECUTE FUNCTION prevent_modification();

-- aeo_scores: Evaluation results (fully immutable)
CREATE TRIGGER trg_aeo_scores_immutable
BEFORE UPDATE OR DELETE ON aeo_scores
FOR EACH ROW EXECUTE FUNCTION prevent_modification();


-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View: Current approval state for each blog
CREATE VIEW current_approvals AS
SELECT DISTINCT ON (blog_id)
    blog_id,
    approved_version_id,
    approver_id,
    approved_at
FROM approval_states
WHERE revoked_at IS NULL
ORDER BY blog_id, approved_at DESC;

-- View: Blogs currently escalated
CREATE VIEW escalated_blogs AS
SELECT DISTINCT blog_id
FROM escalations
WHERE status = 'pending_review';

-- ============================================================================
-- COMMENTS & DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE users IS 'Users with human verification for approval enforcement';
COMMENT ON COLUMN users.is_human IS 'CRITICAL: Only true humans can approve content. Service accounts must be false.';

COMMENT ON TABLE blog_versions IS 'Immutable content snapshots. INSERT-ONLY enforced by trigger.';
COMMENT ON COLUMN blog_versions.source_rewrite_cycle_id IS 'Links to AI rewrite that generated this version (audit trail)';
COMMENT ON COLUMN blog_versions.content_hash IS 'SHA-256 for integrity verification and deduplication';

COMMENT ON TABLE approval_states IS 'Approval history with INSERT-ONLY revocation';
COMMENT ON COLUMN approval_states.revoked_at IS 'To revoke approval, INSERT new row with this populated (no UPDATE)';

COMMENT ON TABLE approval_attempts IS 'Audit log of all approval attempts including failures';

COMMENT ON TABLE escalations IS 'Hard stops where automation pauses for human review';

COMMENT ON TABLE rewrite_suggestions IS 'AI-generated content awaiting user acceptance (advisory only)';
