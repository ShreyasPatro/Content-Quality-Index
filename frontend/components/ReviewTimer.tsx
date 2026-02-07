'use client'

import { useEffect, useState } from 'react'

interface ReviewTimerProps {
    reviewStartedAt: string | null
    minimumReviewDurationSeconds: number
    isDisabled?: boolean
}

export function ReviewTimer({
    reviewStartedAt,
    minimumReviewDurationSeconds,
    isDisabled = true,
}: ReviewTimerProps) {
    const [elapsedSeconds, setElapsedSeconds] = useState(0)
    const [canApprove, setCanApprove] = useState(false)

    useEffect(() => {
        if (!reviewStartedAt) {
            setElapsedSeconds(0)
            setCanApprove(false)
            return
        }

        const startTime = new Date(reviewStartedAt).getTime()

        const interval = setInterval(() => {
            const now = Date.now()
            const elapsed = Math.floor((now - startTime) / 1000)
            setElapsedSeconds(elapsed)
            setCanApprove(elapsed >= minimumReviewDurationSeconds)
        }, 1000)

        return () => clearInterval(interval)
    }, [reviewStartedAt, minimumReviewDurationSeconds])

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins}:${secs.toString().padStart(2, '0')}`
    }

    const remainingSeconds = Math.max(0, minimumReviewDurationSeconds - elapsedSeconds)
    const progress = Math.min(100, (elapsedSeconds / minimumReviewDurationSeconds) * 100)

    if (!reviewStartedAt) {
        return (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                    </svg>
                    <span>Review not started</span>
                </div>
            </div>
        )
    }

    return (
        <div className={`border rounded-lg p-4 ${canApprove ? 'bg-blue-50 border-blue-200' : 'bg-yellow-50 border-yellow-200'
            }`}>
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                    <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                    </svg>
                    <span className="text-sm font-medium text-gray-900">Review Timer</span>
                </div>
                <span className="text-lg font-mono font-bold text-gray-900">
                    {formatTime(elapsedSeconds)}
                </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                <div
                    className={`h-2 rounded-full transition-all ${canApprove ? 'bg-blue-500' : 'bg-yellow-500'
                        }`}
                    style={{ width: `${progress}%` }}
                ></div>
            </div>

            {/* Status Message */}
            <div className="text-xs text-gray-700">
                {canApprove ? (
                    <span className="font-medium">✓ Minimum review time met</span>
                ) : (
                    <span>
                        Minimum review time: {minimumReviewDurationSeconds}s (
                        {formatTime(remainingSeconds)} remaining)
                    </span>
                )}
            </div>

            {isDisabled && (
                <div className="mt-2 text-xs text-gray-500 italic">
                    (Timer is for demonstration only - approval actions disabled)
                </div>
            )}
        </div>
    )
}
