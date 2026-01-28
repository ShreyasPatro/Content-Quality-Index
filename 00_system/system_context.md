Internal Content Quality Engine - Implementation Plan
Goal Description
Design and implement an "Internal Content Quality Engine" focused on immutable content versioning, human-in-the-loop enforcement, and AI-assisted rewrites. The system is built for auditability and defensibility.

User Review Required
IMPORTANT

Immutable Data Model: The core design relies on an INSERT-only strategy for content. This increases storage requirements but ensures perfect auditability.
Stack Selection: Confirming usage of Python 3.12, FastAPI, PostgreSQL (SQLAlchemy Core), Pydantic v2, Redis, Celery, and Next.js 14.
AI Model: Claude 3.5 Sonnet will be used. API keys and access will be needed.
Proposed Architecture
1. Data Model (PostgreSQL)
See schema.sql (to be created) for exact DDL.

Core Concept: ContentItem is the stable identity. ContentVersion is the immutable state.

content_items: Registry of unique content entities.

id: UUID (PK)
created_at: Timestamp
type: Enum (Article, ProductDescription, etc.)
content_versions: Immutable snapshots. INSERT-only.

id: UUID (PK)
content_item_id: UUID (FK)
version_number: Integer (Auto-increment per item)
body: JSONB (The actual content)
hash: SHA-256 (For integrity)
created_by: UserID (FK)
created_at: Timestamp
ai_generated: Boolean
workflow_states: Tracks the status of a specific version.

version_id: UUID (FK)
state: Enum (Draft, Pending_Review, Approved, Rejected, Published)
changed_by: UserID
changed_at: Timestamp
comments: Text
2. Backend (FastAPI + Python 3.12)
Layered Architecture:
api/: Routes and Controllers.
domain/: Business logic and Pydantic models.
service/: Orchestration (AI calls, Workflow transitions).
data/: SQLAlchemy Core queries.
Async: Fully async API handling.
Workers: Celery + Redis for long-running AI tasks.
3. Frontend (Next.js 14 App Router)
UI UX: "Diff" views are critical. Reviewers must see exactly what changed between versions.
State Management: React Server Components for fetching, Client Components for interactive review tools.
Proposed Changes
Backend Setup
[NEW] backend/
pyproject.toml: Dependencies (FastAPI, SQLAlchemy, asyncpg, celery, redis, pydantic-settings).
app/main.py: Entry point.
app/core/config.py: Configuration.
app/db/: Database connection and schema definitions.
Frontend Setup
[NEW] frontend/
Standard Next.js 14 setup with TypeScript and Tailwind CSS.
Verification Plan
Automated Tests
Backend: pytest for API endpoints and logic.
Database: Integration tests ensuring FK constraints and immutability (trying to UPDATE a version should fail or be strictly forbidden by logic).
Manual Verification
Workflow Walkthrough: Create content -> Edit (New Version) -> AI Rewrite -> Approve -> Publish.