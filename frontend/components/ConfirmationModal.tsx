'use client'

import { useEffect, useRef } from 'react'

/**
 * ConfirmationModal Component
 * 
 * SAFETY-CRITICAL: This modal is the LAST human friction layer before irreversible backend actions.
 * 
 * DESIGN PRINCIPLES:
 * 1. Accidental approval MUST be impossible
 * 2. Confirm button NEVER auto-focused
 * 3. Enter key NEVER triggers confirm
 * 4. ESC always cancels
 * 5. Visual severity matches action risk
 * 
 * WHAT THIS MODAL MUST NOT DO:
 * - NO optimistic UI updates
 * - NO routing/navigation
 * - NO API calls
 * - NO state mutation outside callbacks
 * - NO business logic
 * - NO approval semantics or decisions
 */

interface ConfirmationModalProps {
    /** Modal title */
    title: string

    /** Explicit consequence statement (e.g., "This will permanently approve version 3") */
    message: string

    /** Confirm button text (e.g., "Approve Version") */
    confirmText: string

    /** Cancel button text */
    cancelText?: string

    /** Callback when user explicitly clicks confirm */
    onConfirm: () => Promise<void> | void

    /** Callback when user cancels (ESC, backdrop click, or cancel button) */
    onCancel: () => void

    /** Visual severity: approve (low), reject (medium), override (high) */
    variant: 'approve' | 'reject' | 'override'

    /** Loading state (disables confirm button) */
    isLoading?: boolean
}

export function ConfirmationModal({
    title,
    message,
    confirmText,
    cancelText = 'Cancel',
    onConfirm,
    onCancel,
    variant,
    isLoading = false,
}: ConfirmationModalProps) {
    const cancelButtonRef = useRef<HTMLButtonElement>(null)

    // SAFETY: Focus cancel button on mount (NEVER confirm button)
    useEffect(() => {
        cancelButtonRef.current?.focus()
    }, [])

    // SAFETY: ESC key always cancels
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') {
                onCancel()
            }
        }

        window.addEventListener('keydown', handleEscape)
        return () => window.removeEventListener('keydown', handleEscape)
    }, [onCancel])

    // SAFETY: Prevent Enter key from triggering confirm
    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            e.preventDefault()
            e.stopPropagation()
            // Do nothing - user must explicitly click confirm
        }
    }

    // Visual styling based on severity
    const variantStyles = {
        approve: {
            confirmButton: 'bg-green-600 hover:bg-green-700 text-white',
            icon: (
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
            ),
        },
        reject: {
            confirmButton: 'bg-orange-600 hover:bg-orange-700 text-white',
            icon: (
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
            ),
        },
        override: {
            confirmButton: 'bg-red-600 hover:bg-red-700 text-white',
            icon: (
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                </svg>
            ),
        },
    }

    const styles = variantStyles[variant]

    return (
        <>
            {/* Backdrop - clicking closes modal */}
            <div
                className="fixed inset-0 bg-black bg-opacity-50 z-40"
                onClick={onCancel}
                aria-hidden="true"
            />

            {/* Modal */}
            <div
                className="fixed inset-0 z-50 flex items-center justify-center p-4"
                role="dialog"
                aria-modal="true"
                aria-labelledby="modal-title"
                aria-describedby="modal-description"
                onKeyDown={handleKeyDown}
            >
                <div
                    className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className="flex items-start space-x-3 mb-4">
                        {styles.icon}
                        <div className="flex-1">
                            <h2 id="modal-title" className="text-lg font-semibold text-gray-900">
                                {title}
                            </h2>
                        </div>
                    </div>

                    {/* Message */}
                    <p id="modal-description" className="text-sm text-gray-700 mb-6">
                        {message}
                    </p>

                    {/* Actions */}
                    <div className="flex space-x-3 justify-end">
                        {/* SAFETY: Cancel button is focused by default and always visible */}
                        <button
                            ref={cancelButtonRef}
                            onClick={onCancel}
                            disabled={isLoading}
                            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                            type="button"
                        >
                            {cancelText}
                        </button>

                        {/* SAFETY: Confirm button requires explicit click, no keyboard shortcuts */}
                        <button
                            onClick={onConfirm}
                            disabled={isLoading}
                            className={`px-4 py-2 rounded font-medium disabled:opacity-50 disabled:cursor-not-allowed ${styles.confirmButton}`}
                            type="button"
                        >
                            {isLoading ? (
                                <span className="flex items-center space-x-2">
                                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                                        <circle
                                            className="opacity-25"
                                            cx="12"
                                            cy="12"
                                            r="10"
                                            stroke="currentColor"
                                            strokeWidth="4"
                                        />
                                        <path
                                            className="opacity-75"
                                            fill="currentColor"
                                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                        />
                                    </svg>
                                    <span>Processing...</span>
                                </span>
                            ) : (
                                confirmText
                            )}
                        </button>
                    </div>

                    {/* SAFETY: Explicit reminder for high-risk actions */}
                    {variant === 'override' && (
                        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-xs text-red-900">
                            <strong>⚠️ High-Risk Action:</strong> This action bypasses standard controls. Ensure
                            proper authorization and documentation.
                        </div>
                    )}
                </div>
            </div>
        </>
    )
}
