'use client'

interface OverrideNoticeProps {
    isDisabled?: boolean
}

export function OverrideNotice({ isDisabled = true }: OverrideNoticeProps) {
    return (
        <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
            <div className="flex items-start space-x-3">
                <svg
                    className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                </svg>
                <div className="flex-1">
                    <h4 className="text-sm font-bold text-red-900 mb-2">Override Path (High Risk)</h4>
                    <p className="text-xs text-red-800 mb-3">
                        This path allows approval despite unmet criteria. Use only in exceptional circumstances
                        with documented justification.
                    </p>

                    <div className="space-y-2">
                        <div className="text-xs text-red-900">
                            <span className="font-semibold">Required for override:</span>
                            <ul className="list-disc list-inside ml-2 mt-1 space-y-1">
                                <li>Senior reviewer authorization</li>
                                <li>Written risk acceptance</li>
                                <li>Documented business justification</li>
                                <li>Explicit acknowledgment of bypassed controls</li>
                            </ul>
                        </div>

                        {/* Override Button (Disabled) */}
                        <button
                            disabled
                            className="w-full px-4 py-3 bg-red-200 text-red-400 rounded font-semibold text-sm cursor-not-allowed opacity-60"
                        >
                            🔒 Request Override (Disabled)
                        </button>

                        {isDisabled && (
                            <p className="text-xs text-red-700 italic text-center">
                                Override functionality is disabled in this demo
                            </p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
