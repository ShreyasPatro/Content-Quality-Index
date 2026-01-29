'use client'

import { useState } from 'react'

interface ExplanationItem {
    pillar: string
    reason: string
    evidence: string[]
}

interface ScoreExplanationProps {
    explanations: ExplanationItem[]
    scoreType: 'ai_likeness' | 'aeo'
}

export function ScoreExplanation({ explanations, scoreType }: ScoreExplanationProps) {
    const [expandedIndex, setExpandedIndex] = useState<number | null>(null)

    const toggleExpand = (index: number) => {
        setExpandedIndex(expandedIndex === index ? null : index)
    }

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {scoreType === 'ai_likeness' ? 'AI Likeness' : 'AEO'} Score Explanations
            </h3>

            {explanations.length === 0 ? (
                <p className="text-gray-500 text-sm">No explanations available.</p>
            ) : (
                <div className="space-y-3">
                    {explanations.map((item, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg">
                            {/* Header (Collapsible) */}
                            <button
                                onClick={() => toggleExpand(index)}
                                className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                            >
                                <div className="flex items-center space-x-3">
                                    <span className="text-sm font-medium text-gray-900">{item.pillar}</span>
                                </div>
                                <svg
                                    className={`w-5 h-5 text-gray-500 transition-transform ${expandedIndex === index ? 'rotate-180' : ''
                                        }`}
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M19 9l-7 7-7-7"
                                    />
                                </svg>
                            </button>

                            {/* Expanded Content */}
                            {expandedIndex === index && (
                                <div className="px-4 pb-4 border-t border-gray-200">
                                    <div className="mt-3">
                                        <p className="text-sm text-gray-700 mb-3">
                                            <span className="font-medium">Reason:</span> {item.reason}
                                        </p>

                                        {item.evidence.length > 0 && (
                                            <div>
                                                <p className="text-sm font-medium text-gray-700 mb-2">Evidence:</p>
                                                <ul className="space-y-1">
                                                    {item.evidence.map((evidence, evidenceIndex) => (
                                                        <li
                                                            key={evidenceIndex}
                                                            className="text-xs text-gray-600 pl-4 border-l-2 border-gray-300"
                                                        >
                                                            {evidence}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Disclaimer */}
            <div className="mt-4 p-3 bg-gray-50 rounded text-xs text-gray-600">
                <p>
                    <strong>Note:</strong> These explanations describe how scores were calculated. They do not
                    constitute recommendations or approval guidance.
                </p>
            </div>
        </div>
    )
}
