/**
 * Auth Utilities
 */

export interface TokenUser {
    user_id: string
    email: string
    role: string
    exp: number
}

export function getUserFromToken(): TokenUser | null {
    if (typeof window === 'undefined') return null

    const token = localStorage.getItem('token')
    if (!token) return null

    try {
        const base64Url = token.split('.')[1]
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
        const jsonPayload = decodeURIComponent(
            window
                .atob(base64)
                .split('')
                .map(function (c) {
                    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
                })
                .join('')
        )

        return JSON.parse(jsonPayload)
    } catch (e) {
        console.error('Failed to decode token:', e)
        return null
    }
}

export function logout() {
    localStorage.removeItem('token')
    document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
    window.location.href = '/login'
}
