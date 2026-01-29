'use client'

import { useState } from 'react'
import Link from 'next/link'

export interface RewriteEntry {
    id: string
    sourceVersionId: string
    sourceVersionNumber: number
    targetVersionId: string
    targetVersionNumber: number
    triggerType: 'ai_likeness' | 'aeo' | 'manual'
    triggerSignals: {
        aiLikenessScore?: number
        aeoScore?: number
        specificDeficits?: string[]
    }
    rewritePrompt: string
    timestamp: string
    status: 'completed' | 'failed' | 'pending'
}

interface RewriteEntryComponentProps {
    entry: RewriteEntry
    blogId: string
}

function RewriteEntryComponent({ entry, blogId }: RewriteEntryComponentProps) {
    const [isExpanded, setIsExpanded] = useState(false)

    const triggerTypeLabels = {
        ai_likeness: 'AI Likeness Threshold',
        aeo: 'AEO Score Deficit',
        manual: 'Manual Trigger',
    }

    const statusStyles = {
        completed: 'bg-blue-50 text-blue-800 border-blue-200',
        failed: 'bg-red-50 text-red-800 border-red-200',
        pending: 'bg-yellow-50 text-yellow-800 border-yellow-200',
    }

    return (
        <div className="border border-gray-200 rounded-lg">
            {/* Header */}
            <div className="p-4 bg-gray-50 border-b border-gray-200">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                        <span className="text-sm font-semibold text-gray-900">Rewrite #{entry.id.substring(0, 8)}</span>
                        <span className={`px-2 py-1 text-xs rounded border ${statusStyles[entry.status]}`}>
                            {entry.status}
                        </span>
                    </div>
                    <span className="text-xs text-gray-500">
                        {new Date(entry.timestamp).toLocaleString()}
                    </span>
                </div>

                {/* Version Flow */}
                <div className="flex items-center space-x-2 text-sm">
                    <Link
                        href={`/dashboard/blogs/${blogId}/versions/${entry.sourceVersionId}`}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                        v{entry.sourceVersionNumber}
                    </Link>
                    <span className="text-gray-400">→</span>
                    <Link
                        href={`/dashboard/blogs/${blogId}/versions/${entry.targetVersionId}`}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                        v{entry.targetVersionNumber}
                    </Link>
                </div>
            </div>

            {/* Trigger Information */}
            <div className="p-4 border-b border-gray-200">
                <div className="text-sm mb-2">
                    <span className="font-medium text-gray-700">Trigger:</span>{' '}
                    <span className="text-gray-900">{triggerTypeLabels[entry.triggerType]}</span>
                </div>

                {/* Trigger Signals */}
                <div className="space-y-1 text-xs text-gray-600">
                    {entry.triggerSignals.aiLikenessScore !== undefined && (
                        <div>
                            <span className="font-medium">AI Likeness Score:</span> {entry.triggerSignals.aiLikenessScore.toFixed(1)}
                        </div>
                    )}
                    {entry.triggerSignals.aeoScore !== undefined && (
                        <div>
                            <span className="font-medium">AEO Score:</span> {entry.triggerSignals.aeoScore.toFixed(1)}
                        </div>
                    )}
                    {entry.triggerSignals.specificDeficits && entry.triggerSignals.specificDeficits.length > 0 && (
                        <div>
                            <span className="font-medium">Specific Deficits:</span>
                            <ul className="list-disc list-inside ml-4 mt-1">
                                {entry.triggerSignals.specificDeficits.map((deficit, index) => (
                                    <li key={index}>{deficit}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </div>

            {/* Rewrite Prompt (Collapsible) */}
            <div>
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                    <span className="text-sm font-medium text-gray-900">Rewrite Prompt (Verbatim)</span>
                    <svg
                        className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </button>

                {isExpanded && (
                    <div className="px-4 pb-4 border-t border-gray-200">
                        <div className="mt-3 bg-gray-50 rounded p-3">
                            <pre className="whitespace-pre-wrap text-xs text-gray-700 font-mono">
                                {entry.rewritePrompt}
                            </pre>
                        </div>

                        {/* Copy Button */}
                        <button
                            onClick={() => navigator.clipboard.writeText(entry.rewritePrompt)}
                            className="mt-2 px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded text-gray-700"
                        >
                            Copy Prompt
                        </button>

                        {/* Advisory Notice */}
                        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
                            <strong>Advisory:</strong> This prompt was used to generate v{entry.targetVersionNumber}.
                            It does not constitute a recommendation or approval guidance.
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

interface RewriteHistoryProps {
    entries: RewriteEntry[]
    blogId: string
}

export function RewriteHistory({ entries, blogId }: RewriteHistoryProps) {
    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Rewrite History</h2>

            {/* Explanation */}
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-900">
                <p className="font-semibold mb-1">What is this?</p>
                <p>
                    This panel shows all automated rewrite operations that have been performed on this blog.
                    Each entry displays the triggering conditions and the exact prompt used to generate the rewrite.
                </p>
            </div>

            {/* Entries */}
            {entries.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                    <p className="text-sm">No rewrite operations yet.</p>
                    <p className="text-xs mt-1">Rewrites will appear here when triggered by score thresholds.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {entries.map((entry) => (
                        <RewriteEntryComponent key={entry.id} entry={entry} blogId={blogId} />
                    ))}
                </div>
            )}

            {/* Footer Disclaimer */}
            <div className="mt-6 p-3 bg-gray-50 rounded text-xs text-gray-600">
                <p className="font-semibold mb-1">Important Notes:</p>
                <ul className="list-disc list-inside space-y-1">
                    <li>Rewrite prompts are deterministic and based on scoring deficits</li>
                    <li>No AI judgment or creativity is applied beyond executing the prompt</li>
                    <li>All rewrites are advisory and require human review before approval</li>
                    <li>This panel is read-only; no rewrite execution is possible from this interface</li>
                </ul>
            </div>
        </div>
    )
}
