# Internal Dashboard Design (Next.js 14 App Router)

**Status:** DESIGN SPECIFICATION
**Version:** 1.0.0
**Date:** 2026-01-29
**Framework:** Next.js 14 (App Router)

## Executive Summary
This document defines a Next.js 14 internal dashboard for content evaluation, rewriting, and approval. The UI enforces human-controlled workflows with strict safeguards against accidental or automated approvals.

---

## 1️⃣ Page & Route Structure

### 1.1 App Router Layout
```
app/
├── layout.tsx                    # Root layout with auth
├── page.tsx                      # Dashboard home (blog list)
├── blogs/
│   └── [blogId]/
│       ├── page.tsx              # Blog overview + timeline
│       ├── versions/
│       │   └── [versionId]/
│       │       ├── page.tsx      # Version detail (read-only)
│       │       └── diff/
│       │           └── [compareId]/
│       │               └── page.tsx  # Diff viewer
│       └── review/
│           └── [versionId]/
│               └── page.tsx      # Review action page (gated)
└── api/
    └── reviews/
        ├── start/route.ts        # POST: Start review
        ├── approve/route.ts      # POST: Approve (time-gated)
        └── reject/route.ts       # POST: Reject
```

### 1.2 Route Separation
| Route Type | Purpose | Mutations |
| :--- | :--- | :--- |
| `/blogs/[blogId]` | Read-only view | None |
| `/blogs/[blogId]/versions/[versionId]` | Version detail | None |
| `/blogs/[blogId]/versions/[versionId]/diff/[compareId]` | Diff viewer | None |
| `/blogs/[blogId]/review/[versionId]` | Review actions | State transitions |

---

## 2️⃣ Key UI Components

### 2.1 Timeline Graph Component
**File:** `components/VersionTimeline.tsx`

**Purpose:** Git-style version lineage visualization

**Features:**
- Vertical timeline with version nodes
- Parent-child connectors (visual lines)
- Approved version: Green badge + checkmark
- Latest version: Blue border (distinct from approved)
- Rejected versions: Red strikethrough
- Clickable nodes → version detail

**Data Structure:**
```typescript
interface VersionNode {
  id: string;
  versionNumber: number;
  state: 'draft' | 'in_review' | 'approved' | 'rejected' | 'archived';
  parentVersionId: string | null;
  createdAt: string;
  isLatest: boolean;
  isApproved: boolean;
}
```

**Visual Hierarchy:**
```
v1 (APPROVED) ✓ ━━━━━━━━━━━━━━━━━ [Green]
 │
v2 (REJECTED) ✗ ━━━━━━━━━━━━━━━━━ [Red, strikethrough]
 │
v3 (IN_REVIEW) ⏱ ━━━━━━━━━━━━━━━━ [Yellow]
 │
v4 (DRAFT) ━━━━━━━━━━━━━━━━━━━━━ [Blue border = Latest]
```

---

### 2.2 Diff Viewer Component
**File:** `components/DiffViewer.tsx`

**Purpose:** Side-by-side markdown diff with inline highlights

**Features:**
- Left pane: Previous version (read-only)
- Right pane: Current version (read-only)
- Inline highlights:
  - Green background: Added lines
  - Red background: Removed lines
  - Yellow background: Modified lines
- Synchronized scrolling
- Line numbers

**Library:** `react-diff-view` or custom implementation

**Props:**
```typescript
interface DiffViewerProps {
  previousContent: string;
  currentContent: string;
  previousVersionNumber: number;
  currentVersionNumber: number;
}
```

---

### 2.3 Score Panels Component
**File:** `components/ScorePanels.tsx`

**Purpose:** Visualize AI-likeness and AEO scores per version

**Features:**
- **AI-Likeness Panel:**
  - Total score (0-100)
  - Trend indicator (↑ ↓ →)
  - Category breakdown (expandable accordion)
  - Rubric version badge
  
- **AEO Score Panel:**
  - Total score (0-100)
  - Trend indicator
  - 7-pillar breakdown (expandable)
  - Rubric version badge ("v1.0.0")

**Data Structure:**
```typescript
interface ScoreData {
  versionId: string;
  aiLikeness: {
    total: number;
    categories: { name: string; score: number }[];
    rubricVersion: string;
  };
  aeo: {
    total: number;
    pillars: {
      answerability: number;
      structure: number;
      specificity: number;
      trust: number;
      coverage: number;
      freshness: number;
      readability: number;
    };
    rubricVersion: string;
  };
}
```

**Trend Calculation:**
```typescript
function calculateTrend(current: number, previous: number | null): 'up' | 'down' | 'neutral' {
  if (!previous) return 'neutral';
  if (current > previous + 5) return 'up';
  if (current < previous - 5) return 'down';
  return 'neutral';
}
```

---

### 2.4 Rewrite History Component
**File:** `components/RewriteHistory.tsx`

**Purpose:** Display rewrite cycle history

**Features:**
- Accordion list of rewrite cycles
- Each cycle shows:
  - Trigger reason (e.g., "AEO total < 70.0")
  - Trigger data (exact scores)
  - Rewrite prompt (read-only, expandable)
  - Resulting version link
  - Timestamp

**Data Structure:**
```typescript
interface RewriteCycle {
  id: string;
  parentVersionId: string;
  childVersionId: string;
  cycleNumber: number;
  triggerReasons: string[];
  triggerData: Record<string, any>;
  rewritePrompt: string;
  createdAt: string;
}
```

---

### 2.5 Review Action Modal
**File:** `components/ReviewActionModal.tsx`

**Purpose:** Gated approval/rejection interface

**Features:**
- **Start Review Button:**
  - Transitions version to `IN_REVIEW`
  - Starts timer
  - Disabled if already in review

- **Approve Button:**
  - Disabled if timer not elapsed
  - Shows countdown: "Approval available in 4:32"
  - Requires confirmation modal
  - Mandatory rationale textarea (min 20 chars)
  - Final confirmation: "I confirm this content is ready to publish"

- **Reject Button:**
  - Available immediately after review starts
  - Requires rejection reason (min 20 chars)
  - Confirmation modal

- **Override Path:**
  - Visibly marked with ⚠️ WARNING badge
  - Requires senior reviewer role
  - Mandatory override reason + risk acceptance note
  - Double confirmation

**State Management:**
```typescript
interface ReviewState {
  versionId: string;
  currentState: 'draft' | 'in_review' | 'approved' | 'rejected';
  reviewStartedAt: string | null;
  timeRemaining: number | null; // seconds
  canApprove: boolean;
  canReject: boolean;
  isOverride: boolean;
}
```

---

## 3️⃣ State Management Approach

### 3.1 Server Components (Default)
**Purpose:** Fetch data from backend, render read-only views

**Examples:**
- `app/blogs/[blogId]/page.tsx` (Server Component)
- `components/VersionTimeline.tsx` (Server Component)
- `components/ScorePanels.tsx` (Server Component)

**Data Fetching:**
```typescript
// app/blogs/[blogId]/page.tsx
export default async function BlogPage({ params }: { params: { blogId: string } }) {
  const blog = await fetch(`${API_URL}/blogs/${params.blogId}`).then(r => r.json());
  const versions = await fetch(`${API_URL}/blogs/${params.blogId}/versions`).then(r => r.json());
  
  return (
    <div>
      <VersionTimeline versions={versions} />
      <ScorePanels versionId={versions[0].id} />
    </div>
  );
}
```

### 3.2 Client Components (Interactions Only)
**Purpose:** Handle user interactions, form submissions

**Examples:**
- `components/ReviewActionModal.tsx` (Client Component)
- `components/DiffViewer.tsx` (Client Component for scroll sync)

**Directive:**
```typescript
'use client';

import { useState } from 'react';

export function ReviewActionModal({ versionId }: { versionId: string }) {
  const [rationale, setRationale] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Client-side interaction logic
}
```

### 3.3 No Client-Side Derived Authority
**Rule:** Never compute approval eligibility on client

**❌ FORBIDDEN:**
```typescript
// Client component
const canApprove = Date.now() - reviewStartedAt > 300000; // WRONG
```

**✅ CORRECT:**
```typescript
// Server component or API route
const reviewState = await fetch(`/api/reviews/${versionId}/state`).then(r => r.json());
// reviewState.canApprove is server-computed
```

---

## 4️⃣ UX Safeguards

### 4.1 Approved ≠ Latest Always Visible
**Implementation:**
- Timeline shows both "APPROVED" badge and "LATEST" border
- Version detail page header:
  ```
  Version 3 [APPROVED ✓]
  (Latest version is v4 - View Latest)
  ```

### 4.2 Approval Requires Deliberate Action
**Flow:**
1. Click "Start Review" → Confirmation modal
2. Wait minimum duration (timer visible)
3. Click "Approve" → Disabled until timer expires
4. Enter rationale (min 20 chars)
5. Click "Confirm Approval" → Final confirmation modal
6. Click "Yes, Approve" → Submit

**Total Clicks:** 4 (Start → Approve → Confirm → Yes)

### 4.3 No Single-Click Publish
**Enforcement:**
- No "Publish" button exists
- "Approve" is multi-step (see 4.2)
- All destructive actions require confirmation

### 4.4 Disabled States
**Button States:**
```typescript
<button
  disabled={!reviewState.canApprove || isSubmitting}
  className={reviewState.canApprove ? 'bg-green-600' : 'bg-gray-400 cursor-not-allowed'}
>
  {reviewState.canApprove 
    ? 'Approve' 
    : `Approval available in ${formatTime(reviewState.timeRemaining)}`}
</button>
```

---

## 5️⃣ Hard Constraints

### 5.1 Frontend is Never Source of Truth
**Rule:** All state transitions happen on backend

**Implementation:**
- API routes validate all preconditions
- Frontend displays backend-computed state
- No optimistic UI updates for approvals

### 5.2 No Optimistic Approval UI
**Forbidden:**
```typescript
// ❌ WRONG
const handleApprove = async () => {
  setVersionState('approved'); // Optimistic update
  await fetch('/api/approve', { method: 'POST' });
};
```

**Correct:**
```typescript
// ✅ CORRECT
const handleApprove = async () => {
  setIsSubmitting(true);
  const result = await fetch('/api/approve', { method: 'POST' });
  if (result.ok) {
    router.refresh(); // Re-fetch server state
  }
  setIsSubmitting(false);
};
```

### 5.3 UI Reflects Backend State Exactly
**Implementation:**
- Use `router.refresh()` after mutations
- Server Components re-fetch on navigation
- No client-side state caching for approval status

---

## 6️⃣ Acceptance Checklist

- ✅ Approved version clearly distinct from latest (badges + colors)
- ✅ Version lineage visually understandable (timeline graph)
- ✅ Diff readable without context loss (side-by-side with highlights)
- ✅ Approval requires deliberate human action (4-step flow)
- ✅ No "one-click publish" anywhere in UI (multi-step confirmation)

---

## 7️⃣ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Framework** | Next.js 14 (App Router) |
| **Styling** | Tailwind CSS |
| **UI Components** | Radix UI (headless) |
| **Diff Rendering** | `react-diff-view` |
| **Charts** | Recharts (for score trends) |
| **Forms** | React Hook Form + Zod validation |
| **Auth** | NextAuth.js (human-only sessions) |

---

## 8️⃣ Example Page Implementation

### 8.1 Blog Detail Page
**File:** `app/blogs/[blogId]/page.tsx`

```typescript
import { VersionTimeline } from '@/components/VersionTimeline';
import { ScorePanels } from '@/components/ScorePanels';
import { RewriteHistory } from '@/components/RewriteHistory';

export default async function BlogPage({ params }: { params: { blogId: string } }) {
  const blog = await fetchBlog(params.blogId);
  const versions = await fetchVersions(params.blogId);
  const latestVersion = versions[0];
  const approvedVersion = versions.find(v => v.state === 'approved');

  return (
    <div className="container mx-auto p-6">
      <header className="mb-6">
        <h1 className="text-3xl font-bold">{blog.title}</h1>
        <div className="flex gap-4 mt-2">
          {approvedVersion && (
            <span className="px-3 py-1 bg-green-100 text-green-800 rounded">
              Approved: v{approvedVersion.versionNumber}
            </span>
          )}
          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded">
            Latest: v{latestVersion.versionNumber}
          </span>
        </div>
      </header>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1">
          <VersionTimeline versions={versions} />
        </div>
        <div className="col-span-2">
          <ScorePanels versionId={latestVersion.id} />
          <RewriteHistory blogId={params.blogId} />
        </div>
      </div>
    </div>
  );
}
```

---

## 9️⃣ Security Considerations

1. **Authentication:** All routes require authenticated human user
2. **Authorization:** Role-based access (editor vs senior_editor)
3. **CSRF Protection:** Built-in Next.js API route protection
4. **Rate Limiting:** Prevent approval spam
5. **Audit Logging:** All actions logged with user ID + timestamp

---

## 🔒 Certification Status

**Status:** DESIGN SPECIFICATION
**Compliance:** Human-controlled, multi-step approval, no automation
**Ready for:** Frontend implementation, UX review

**Signed:** Antigravity
**Date:** 2026-01-29
