'use client'

import { useState } from 'react'
import { ReviewTimer } from './ReviewTimer'
import { OverrideNotice } from './OverrideNotice'

interface ApprovalPanelProps {
    versionId: string
    versionNumber: number
    currentState: 'draft' | 'in_review' | 'approved' | 'rejected' | 'archived'
    reviewStartedAt: string | null
    reviewerEmail?: string
    isDisabled?: boolean
}

export function ApprovalPanel({
    versionId,
    versionNumber,
    currentState,
    reviewStartedAt,
    reviewerEmail = 'reviewer@example.com',
    isDisabled = true,
}: ApprovalPanelProps) {
    const [showOverride, setShowOverride] = useState(false)
    const [approvalNotes, setApprovalNotes] = useState('')
    const [rejectionNotes, setRejectionNotes] = useState('')

    const minimumReviewDuration = 300 // 5 minutes in seconds

    const canStartReview = currentState === 'draft'
    const canApproveOrReject = currentState === 'in_review'

    return (
        <div className="bg-white border-2 border-gray-300 rounded-lg p-6 space-y-6">
            {/* Header */}
            <div className="border-b border-gray-200 pb-4">
                <h2 className="text-xl font-bold text-gray-900 mb-2">Approval Panel</h2>
                <div className="flex items-center justify-between text-sm">
                    <div>
                        <span className="text-gray-600">Version:</span>{' '}
                        <span className="font-semibold text-gray-900">v{versionNumber}</span>
                    </div>
                    <div>
                        <span className="text-gray-600">Status:</span>{' '}
                        <span className="font-semibold text-gray-900 capitalize">
                            {currentState.replace('_', ' ')}
                        </span>
                    </div>
                </div>
            </div>

            {/* Reviewer Identity */}
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                        <svg className="w-6 h-6 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                            <path
                                fillRule="evenodd"
                                d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                                clipRule="evenodd"
                            />
                        </svg>
                    </div>
                    <div>
                        <div className="text-sm font-medium text-gray-900">Reviewer</div>
                        <div className="text-xs text-gray-600">{reviewerEmail}</div>
                    </div>
                </div>
            </div>

            {/* Review Timer */}
            {currentState === 'in_review' && (
                <ReviewTimer
                    reviewStartedAt={reviewStartedAt}
                    minimumReviewDurationSeconds={minimumReviewDuration}
                    isDisabled={isDisabled}
                />
            )}

            {/* Start Review Button */}
            {canStartReview && (
                <div className="space-y-3">
                    <button
                        disabled
                        className="w-full px-6 py-3 bg-gray-200 text-gray-400 rounded-lg font-semibold cursor-not-allowed opacity-60"
                    >
                        🔒 Start Review (Disabled)
                    </button>
                    <p className="text-xs text-gray-500 text-center italic">
                        Review workflow is disabled in this demo
                    </p>
                </div>
            )}

            {/* Approval Actions */}
            {canApproveOrReject && (
                <div className="space-y-4">
                    {/* Approval Notes */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Approval Notes (Required)
                        </label>
                        <textarea
                            disabled
                            value={approvalNotes}
                            onChange={(e) => setApprovalNotes(e.target.value)}
                            placeholder="Document your review decision and rationale..."
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-50 text-gray-400 cursor-not-allowed"
                            rows={4}
                        />
                    </div>

                    {/* Approve Button */}
                    <button
                        disabled
                        className="w-full px-6 py-3 bg-green-200 text-green-400 rounded-lg font-semibold cursor-not-allowed opacity-60 flex items-center justify-center space-x-2"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>🔒 Approve Version (Disabled)</span>
                    </button>

                    {/* Reject Section */}
                    <details className="border border-gray-200 rounded-lg">
                        <summary className="px-4 py-3 cursor-pointer hover:bg-gray-50 font-medium text-sm text-gray-700">
                            Reject with Feedback
                        </summary>
                        <div className="px-4 pb-4 space-y-3">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Rejection Reason (Required)
                                </label>
                                <textarea
                                    disabled
                                    value={rejectionNotes}
                                    onChange={(e) => setRejectionNotes(e.target.value)}
                                    placeholder="Explain why this version is being rejected..."
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-50 text-gray-400 cursor-not-allowed"
                                    rows={4}
                                />
                            </div>
                            <button
                                disabled
                                className="w-full px-6 py-3 bg-orange-200 text-orange-400 rounded-lg font-semibold cursor-not-allowed opacity-60"
                            >
                                🔒 Reject Version (Disabled)
                            </button>
                        </div>
                    </details>

                    {/* Override Path Toggle */}
                    <div className="border-t border-gray-200 pt-4">
                        <button
                            onClick={() => setShowOverride(!showOverride)}
                            className="text-sm text-red-600 hover:text-red-800 font-medium"
                        >
                            {showOverride ? '▼' : '▶'} Show Override Path (High Risk)
                        </button>
                    </div>

                    {showOverride && (
                        <div className="mt-4">
                            <OverrideNotice isDisabled={isDisabled} />
                        </div>
                    )}
                </div>
            )}

            {/* Already Approved/Rejected State */}
            {(currentState === 'approved' || currentState === 'rejected') && (
                <div className={`p-4 rounded-lg ${currentState === 'approved'
                        ? 'bg-green-50 border border-green-200'
                        : 'bg-red-50 border border-red-200'
                    }`}>
                    <div className="flex items-center space-x-2">
                        {currentState === 'approved' ? (
                            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        ) : (
                            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        )}
                        <span className={`font-semibold ${currentState === 'approved' ? 'text-green-900' : 'text-red-900'
                            }`}>
                            This version has been {currentState}
                        </span>
                    </div>
                    <p className="text-xs text-gray-600 mt-2">
                        No further approval actions are possible.
                    </p>
                </div>
            )}

            {/* Footer Disclaimer */}
            <div className="border-t border-gray-200 pt-4">
                <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-xs text-yellow-900">
                    <p className="font-semibold mb-1">⚠️ Demo Mode Notice</p>
                    <p>
                        This approval panel is displayed in <strong>DISABLED MODE</strong> for layout validation
                        and cognitive load testing. All approval actions are locked and no backend calls will be made.
                    </p>
                </div>
            </div>
        </div>
    )
}
