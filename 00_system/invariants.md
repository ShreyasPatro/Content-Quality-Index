# System Invariants & Constraints

This document defines the non-negotiable architectural rules (Hard Invariants) and flexible guidelines (Soft Rules) for the Internal Content Quality Engine. These constraints are designed to ensure auditability, defensibility, and human accountability.

## 1. Hard Invariants (Must Never Be Violated)

These are enforced by Database Constraints, Cryptographic Hashes, or Core Logic.

1.  **Immutability of Content Versions (The "Write-Once" Rule)**
    *   **Definition**: Once a `ContentVersion` row is committed, its `body` and `hash` columns CANNOT be updated.
    *   **Enforcement**: PostgreSQL `REVOKE UPDATE, DELETE ON content_versions` for the application user. Triggers raising exceptions on update attempts.
    *   **Violation Violation**: An `UPDATE` statement running against `content_versions`.

2.  **Identity Persistence**
    *   **Definition**: A `ContentItem` ID never changes, regardless of how many versions or rewrites occur.
    *   **Enforcement**: Foreign Keys link `ContentVersion` -> `ContentItem`.
    *   **Violation Violation**: Creating a new `ContentItem` for a "v2" of an article instead of a new `ContentVersion`.

3.  **Human Supremacy in Approval**
    *   **Definition**: The transition to an `APPROVED` or `PUBLISHED` state MUST record a human User ID. AI agents cannot sign off on content.
    *   **Enforcement**: Application logic checks `user.is_human` or ensures the API token used for approval belongs to a human scope, not a service account.
    *   **Violation Violation**: An automated cron job bulk-approving all items with a high AI score.

4.  **Strict Audit Chain**
    *   **Definition**: Every `ContentVersion` must reference a parent/source (unless it is the root).
    *   **Enforcement**: `parent_version_id` column (nullable only for v1).
    *   **Violation Violation**: A version appearing out of nowhere without history.

5.  **AI Is Advisory-Only**
    *   **Definition**: AI Scores and Suggestions are stored as metadata or separate entities, NEVER altering the canonical `ContentVersion` body directly without explicit user acceptance (which creates a NEW version).
    *   **Enforcement**: AI processes only have `INSERT` permission to `ContentSuggestions` or `ContentScores` tables, never `ContentVersions`.

---

## 2. Soft Rules (Policy / Can Evolve)

These are enforced by Application Logic but may have overrides or configuration changes.

1.  **Sequential Version Numbering**: Ideally versions refer to `v1, v2, v3`. However, distributed systems might cause gaps or timestamp-based ordering implies sequence.
    *   *Constraint*: Monotonic increase is preferred but not strictly enforced by DB lock (to avoid contention), as long as `created_at` provides order.

2.  **Score Thresholds for Review**: "Items with Quality Score < 80 cannot be Published."
    *   *Flexibility*: A Manager might override this for urgent hotfixes (Defensibility requires logging this override).

3.  **One Draft Per User**: "A user can only have one active draft of an item at a time."
    *   *Flexibility*: Good for UI simplicity, but backend could technically support concurrent drafts branches if requirements change.

---

## 3. Violations & Dangers

| Violation Example | Why it is Dangerous |
| :--- | :--- |
| **Updating a Typo in v2 Database Row** | Destroys auditability. If v2 was published and unauthorized, we lose proof of *what* was published. **Fix**: Create v3 with the typo fix. |
| **AI Auto-Publishing High Scores** | AI hallucinations could publish libelous or harmful content. Legal defensibility is lost ("The AI did it" is not a defense). |
| **Deleting "Draft" Versions** | If a draft contained sensitive IP or evidence of bad intent, deleting it removes the audit trail. **Fix**: "Soft Delete" or Archived status only. |
| **Bypassing Workflow State** | Manually creating a "Published" state on a "Draft" content without passing "Approved". limits accountability. |

---

## 4. Influence on Design

### Database Design (Schema)
*   **`content_versions`**:
    *   `updatable = False` (SQLAlchemy).
    *   `GRANT INSERT, SELECT` only.
    *   Columns: `body (JSONB)`, `content_hash (Computed/Immutable)`.
*   **`workflow_actions`**:
    *   New table to log *transitions* independently of version creation.
    *   `from_state`, `to_state`, `actor_id`, `reason`.

### API Design
*   **No `PUT /content/{id}`**: This HTTP verb implies replacement.
*   **Use `POST /content/{id}/versions`**: Explicitly creating a new version.
*   **`POST /content/{id}/approve`**: Separate endpoint, strictly checking user permissions.

### Workflows
1.  **Edit Flow**: GET v2 -> Edit -> POST as v3 (Status: Draft).
2.  **Review Flow**: GET v3 -> Compare w/ v2 -> (Add Comments OR Approve).
3.  **Publish Flow**: Check Status == Approved -> POST to CMS -> Update `published_at` (Metadata update, NOT content update).
