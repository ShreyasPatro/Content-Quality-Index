/**
 * Approval API Client
 * 
 * This file is a transport-only API client. All approval authority lives on the backend.
 * 
 * This module provides thin wrappers around approval-related backend endpoints.
 * It performs NO business logic, NO optimistic updates, and NO decision-making.
 * All validation and authorization is enforced server-side.
 */

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/api/v1';

/**
 * Maps HTTP status codes to semantic error messages.
 */
function getErrorMessage(status: number, backendMessage?: string): string {
    if (backendMessage) {
        return backendMessage;
    }

    switch (status) {
        case 400:
            return 'Invalid state transition or validation failed';
        case 403:
            return 'Human verification or permission required';
        case 409:
            return 'Version already processed';
        case 500:
            return 'Server error - please contact support';
        default:
            return `Request failed with status ${status}`;
    }
}

/**
 * Start review for a version.
 * 
 * Endpoint: POST /versions/{versionId}/start-review
 * 
 * @throws Error if request fails or backend returns non-2xx status
 */
export async function startReview(
    versionId: string,
    token: string
): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/versions/${versionId}/start-review`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(getErrorMessage(response.status, errorData.detail));
    }

    return response.json();
}

/**
 * Approve a version with mandatory rationale.
 * 
 * Endpoint: POST /versions/{versionId}/approve
 * 
 * @throws Error if request fails or backend returns non-2xx status
 */
export async function approveVersion(
    versionId: string,
    rationale: string,
    token: string
): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/versions/${versionId}/approve`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ rationale }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(getErrorMessage(response.status, errorData.detail));
    }

    return response.json();
}

/**
 * Reject a version with mandatory rationale.
 * 
 * Endpoint: POST /versions/{versionId}/reject
 * 
 * @throws Error if request fails or backend returns non-2xx status
 */
export async function rejectVersion(
    versionId: string,
    rationale: string,
    token: string
): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/versions/${versionId}/reject`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ rationale }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(getErrorMessage(response.status, errorData.detail));
    }

    return response.json();
}

/**
 * Request override for approval with justification and risk acceptance.
 * 
 * Endpoint: POST /versions/{versionId}/request-override
 * 
 * @throws Error if request fails or backend returns non-2xx status
 */
export async function requestOverride(
    versionId: string,
    justification: string,
    riskAcceptance: string,
    token: string
): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/versions/${versionId}/request-override`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
            justification,
            risk_acceptance: riskAcceptance,
        }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(getErrorMessage(response.status, errorData.detail));
    }

    return response.json();
}
