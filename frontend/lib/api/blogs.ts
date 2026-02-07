/**
 * Blog Ingestion API Client
 * 
 * REGULATORY CONSTRAINT: Transport-only layer for blog operations.
 * No business logic, no optimistic updates, no retries.
 */

const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/api/v1'

interface CreateBlogResponse {
    id: string
    name: string
    created_at: string
}

interface CreateVersionResponse {
    id: string
    blog_id: string
    version_number: number
    source: string
    created_at: string
}

interface TriggerEvaluationResponse {
    run_id: string
    status: string
}

interface EvaluationStatusResponse {
    run_id: string
    status: 'queued' | 'processing' | 'complete' | 'failed'
    version_id: string
    scores?: {
        ai_likeness?: {
            total: number
            breakdown: Array<{ category: string; score: number }>
        }
        aeo?: {
            total: number
            pillars: Array<{ name: string; score: number; max_score: number }>
        }
    }
    error?: string
}

/**
 * Create a new blog
 * 
 * AUDIT: Blog name is human-provided, immutable after creation
 */
export async function createBlog(
    name: string,
    token: string
): Promise<CreateBlogResponse> {
    const response = await fetch(`${API_URL}/blogs`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name }),
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
}

/**
 * Create first version for a blog
 * 
 * AUDIT: Content is paste-only, source is 'human_paste'
 * CONSTRAINT: Only one version allowed per blog at creation
 */
export async function createVersion(
    blogId: string,
    content: string,
    token: string
): Promise<CreateVersionResponse> {
    const response = await fetch(`${API_URL}/blogs/${blogId}/versions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
            content,
            source: 'human_paste',
        }),
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
}

/**
 * Trigger evaluation pipeline
 * 
 * AUDIT: Evaluation is human-initiated, not automatic
 * PIPELINE: Triggers AI Likeness + AEO scoring
 */
export async function triggerEvaluation(
    blogId: string,
    versionId: string,
    token: string
): Promise<TriggerEvaluationResponse> {
    const response = await fetch(`${API_URL}/versions/${versionId}/evaluate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
            include_detectors: true,
            include_aeo: true
        }),
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || `HTTP ${response.status}`)
    }

    const data = await response.json()
    return {
        run_id: data.job_id,
        status: data.status
    }
}

/**
 * Poll evaluation status
 * 
 * AUDIT: No optimistic updates, wait for backend completion
 */
export async function getEvaluationStatus(
    runId: string,
    token: string
): Promise<EvaluationStatusResponse> {
    const response = await fetch(`${API_URL}/evaluation-runs/${runId}`, {
        method: 'GET',
        headers: {
            Authorization: `Bearer ${token}`,
        },
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
}

/**
 * Poll evaluation status until completion
 * 
 * REGULATORY: No optimistic updates, polls backend until real completion
 */
export async function pollEvaluationStatus(
    runId: string,
    token: string,
    onUpdate?: (status: EvaluationStatusResponse) => void,
    maxAttempts: number = 60,
    intervalMs: number = 2000
): Promise<EvaluationStatusResponse> {
    let attempts = 0

    while (attempts < maxAttempts) {
        const status = await getEvaluationStatus(runId, token)

        // Notify caller of status update
        if (onUpdate) {
            onUpdate(status)
        }

        // Check if evaluation is complete
        if (status.status === 'complete' || status.status === 'failed') {
            return status
        }

        // Wait before next poll
        await new Promise(resolve => setTimeout(resolve, intervalMs))
        attempts++
    }

    throw new Error('Evaluation timeout: exceeded maximum polling attempts')
}
