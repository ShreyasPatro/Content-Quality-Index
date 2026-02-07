/**
 * AEO Sandbox API Client
 */

const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/api/v1'

export interface PillarScore {
    score: number
    max_score: number
    reason: string[]
}

export interface AEOScoreResult {
    total_score: number
    rubric_version: string
    pillars: Record<string, PillarScore>
    details: any
}

export interface SandboxAnalyzeResponse {
    aeo: AEOScoreResult
}

// --- AI Sandbox Types ---

export interface SubScoreItem {
    score: number
    max_score: number
    percentage: number
    explanation: string
    evidence: string[]
}

export interface RubricRawResponse {
    rubric_version: string
    total_score: number
    subscores: Record<string, SubScoreItem>
    metadata: any
}

export interface SandboxAIResponse {
    score: number
    model_version: string
    timestamp: string
    raw_response: RubricRawResponse
}

export async function analyzeAEOSandbox(
    content: string,
    token: string
): Promise<SandboxAnalyzeResponse> {
    const response = await fetch(`${API_URL}/sandbox/aeo`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ content }),
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
}

export async function analyzeAISandbox(
    content: string,
    token: string
): Promise<SandboxAIResponse> {
    const response = await fetch(`${API_URL}/sandbox/ai`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ content }),
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
}
