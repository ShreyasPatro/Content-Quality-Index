# API Contract (FastAPI 0.110+)

## Global Standards
- **Protocol**: HTTP/1.1
- **Format**: JSON (Request/Response)
- **Auth**: Bearer Token (JWT). Scopes: `writer`, `reviewer`, `admin`.
- **Validation**: Pydantic v2.
- **Concurrency**: `async def` endpoints using `asyncpg` + SQLAlchemy Core.

---

## 1. Content Management

### `POST /blogs`
**Purpose**: Initialize a new content identity (Blog).
*   **Auth**: `writer`
*   **Sync/Async**: Sync (Database Insert)
*   **Side Effects**: None.

#### Request Schema
```python
class BlogCreate(BaseModel):
    title_slug: str = Field(..., pattern=r"^[a-z0-9-]+$")
    project_id: UUID | None = None
```

#### Response Schema
```python
class BlogResponse(BaseModel):
    id: UUID
    title_slug: str
    created_at: AwareDatetime
```

---

### `POST /blogs/{blog_id}/versions`
**Purpose**: Create a NEW immutable version of the blog. This is the **only** way to "edit" content.
*   **Auth**: `writer`
*   **Sync/Async**: Sync (Database Insert)
*   **Invariant**: `parent_version_id` must match the user's current baseline.
*   **Side Effects**: Invalidates previous "Draft" states if logic dictates.
*   **AI Audit Trail**: When accepting an AI-generated rewrite suggestion, MUST provide `source_rewrite_cycle_id` to link the version to the rewrite cycle that generated it.

#### Request Schema
```python
class VersionCreate(BaseModel):
    parent_version_id: UUID | None = Field(None, description="NULL for first version only")
    content: dict[str, Any] = Field(..., description="Full JSON body")
    change_reason: str = Field(..., min_length=5)
    source_rewrite_cycle_id: UUID | None = Field(
        None, 
        description="If accepting an AI-generated rewrite suggestion, provide the rewrite_cycle.id to establish audit trail"
    )
```

#### Response Schema
```python
class VersionResponse(BaseModel):
    id: UUID
    version_number: int
    content_hash: str
    created_at: AwareDatetime
```

#### Failure Modes
- `409 Conflict`: If `parent_version_id` is not the latest (optional check) or if hash matches parent (no change).
- `400 Bad Request`: If DAG cycle detected (impossible by design but good check).

---

### `POST /versions/{version_id}/revert`
**Purpose**: Restore a historical version as the *new* latest version.
*   **Auth**: `writer`
*   **Behavior**:
    1.  Read content of `version_id`.
    2.  Find *current* latest version of the blog to set as `parent`.
    3.  Insert NEW version with content of `version_id`.
*   **Side Effects**: None.

#### Request Schema
```python
class RevertRequest(BaseModel):
    reason: str = Field("Reverting to previous version", min_length=5)
```

#### Response Schema
- Returns `VersionResponse` (The new version, NOT the old one).

---

## 2. AI & Evaluation (Async)

### `POST /versions/{version_id}/evaluate`
**Purpose**: Trigger a suite of AE/AEO/Quality checks.
*   **Auth**: `writer`, `reviewer`
*   **Sync/Async**: **Async**. Returns `202 Accepted` with `JobResponse`. Response indicates queued background execution.
*   **Side Effects**: Enqueues Celery tasks.

#### Request Schema
```python
class EvaluationRequest(BaseModel):
    include_detectors: bool = True
    include_aeo: bool = True
```

#### Response Schema
```python
class JobResponse(BaseModel):
    job_id: UUID
    status: Literal["queued", "processing"]
    eta_seconds: int
```

---

### `POST /versions/{version_id}/rewrite`
**Purpose**: Request AI to generate a *suggestion* for a rewrite.
*   **Auth**: `writer`
*   **Sync/Async**: **Async**. Returns `202 Accepted` with `JobResponse`. Response indicates queued background execution.
*   **Invariant**: **Advisory Only**. Does NOT create a new `ContentVersion` automatically. It creates a `RewriteSuggestion` (or similar) or returns data to UI to prompt user to `POST /versions`.
*   **Side Effects**: Enqueues LLM generation task.

#### Request Schema
```python
class RewriteRequest(BaseModel):
    prompt_template_id: UUID | None
    instructions: str
    target_sections: list[str] | None
```

#### Response Schema
- `JobResponse`

---

## 3. Human Review & Approval

### `POST /versions/{version_id}/review`
**Purpose**: Log a human review action (Comment, Request Changes, Reject).
*   **Auth**: `reviewer` (Human Only - strictly verified via `request.user.is_human`).
*   **Sync/Async**: Sync.
*   **Side Effects**: May update implicit workflow state (e.g. from "Pending" to "Changes Requested").

#### Request Schema
```python
class ReviewActionReq(BaseModel):
    action: Literal["COMMENT", "REQUEST_CHANGES", "REJECT", "APPROVE_INTENT"]
    comments: str
```

#### Idempotency
- Safe to retry. Multiple comments are allowed.

---

### `POST /blogs/{blog_id}/approve`
**Purpose**: The "Go Live" implementation. Sets the specific version as the `APPROVED` state for the blog.
*   **Auth**: `reviewer`, `admin` (Human Only - strictly verified via `request.user.is_human`).
*   **Invariant**:
    - `approved_version_id` MUST belong to `blog_id`.
    - User MUST be human.
*   **Side Effects**: Updates `approval_states` table. Triggers "Publish to CMS" webhook if configured.

#### Request Schema
```python
class ApprovalRequest(BaseModel):
    approved_version_id: UUID
    notes: str | None = None
```

#### Response Schema
```python
class ApprovalStateResponse(BaseModel):
    id: UUID
    version_number: int
    is_active: bool
    approved_at: AwareDatetime
```

#### Failure Modes
- `403 Forbidden`: If actor is a Service Account/Bot.
- `400 Bad Request`: If version belongs to wrong blog.
