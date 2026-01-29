'use client'

import { useState } from 'react'

interface DiffViewerProps {
    previousContent: string
    currentContent: string
    previousVersionNumber: number
    currentVersionNumber: number
    previousVersionId?: string
    currentVersionId?: string
}

interface DiffLine {
    type: 'unchanged' | 'added' | 'removed' | 'modified'
    previousLineNumber: number | null
    currentLineNumber: number | null
    content: string
}

function computeLineDiff(previous: string, current: string): DiffLine[] {
    const previousLines = previous.split('\n')
    const currentLines = current.split('\n')
    const diff: DiffLine[] = []

    let prevIndex = 0
    let currIndex = 0

    // Simple line-by-line diff (can be enhanced with proper diff algorithm)
    while (prevIndex < previousLines.length || currIndex < currentLines.length) {
        const prevLine = previousLines[prevIndex]
        const currLine = currentLines[currIndex]

        if (prevLine === currLine) {
            // Unchanged line
            diff.push({
                type: 'unchanged',
                previousLineNumber: prevIndex + 1,
                currentLineNumber: currIndex + 1,
                content: prevLine || '',
            })
            prevIndex++
            currIndex++
        } else if (prevIndex >= previousLines.length) {
            // Added line (only in current)
            diff.push({
                type: 'added',
                previousLineNumber: null,
                currentLineNumber: currIndex + 1,
                content: currLine || '',
            })
            currIndex++
        } else if (currIndex >= currentLines.length) {
            // Removed line (only in previous)
            diff.push({
                type: 'removed',
                previousLineNumber: prevIndex + 1,
                currentLineNumber: null,
                content: prevLine || '',
            })
            prevIndex++
        } else {
            // Modified line (different content)
            diff.push({
                type: 'removed',
                previousLineNumber: prevIndex + 1,
                currentLineNumber: null,
                content: prevLine,
            })
            diff.push({
                type: 'added',
                previousLineNumber: null,
                currentLineNumber: currIndex + 1,
                content: currLine,
            })
            prevIndex++
            currIndex++
        }
    }

    return diff
}

export function DiffViewer({
    previousContent,
    currentContent,
    previousVersionNumber,
    currentVersionNumber,
    previousVersionId,
    currentVersionId,
}: DiffViewerProps) {
    const [isCollapsed, setIsCollapsed] = useState(true)
    const diffLines = computeLineDiff(previousContent, currentContent)

    // Count changes
    const addedCount = diffLines.filter((l) => l.type === 'added').length
    const removedCount = diffLines.filter((l) => l.type === 'removed').length
    const totalChanges = addedCount + removedCount

    // Collapse if more than 100 lines changed
    const shouldCollapse = totalChanges > 100

    // Neutral styling (no green/red judgment)
    const lineStyles = {
        unchanged: 'bg-white text-gray-700',
        added: 'bg-blue-50 text-blue-900 border-l-4 border-blue-400',
        removed: 'bg-orange-50 text-orange-900 border-l-4 border-orange-400',
        modified: 'bg-purple-50 text-purple-900 border-l-4 border-purple-400',
    }

    return (
        <div className="bg-white rounded-lg shadow">
            {/* Header */}
            <div className="border-b border-gray-200 p-4">
                <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">Version Comparison</h3>
                    {shouldCollapse && (
                        <button
                            onClick={() => setIsCollapsed(!isCollapsed)}
                            className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded text-gray-700"
                        >
                            {isCollapsed ? `Show ${totalChanges} changes` : 'Collapse'}
                        </button>
                    )}
                </div>

                {/* Explicit Version Labels */}
                <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-600">From:</span>
                        <span className="px-2 py-1 bg-gray-100 rounded text-gray-900">
                            Version {previousVersionNumber}
                        </span>
                        {previousVersionId && (
                            <span className="text-xs text-gray-500">{previousVersionId.substring(0, 8)}...</span>
                        )}
                    </div>
                    <span className="text-gray-400">→</span>
                    <div className="flex items-center space-x-2">
                        <span className="font-medium text-gray-600">To:</span>
                        <span className="px-2 py-1 bg-gray-100 rounded text-gray-900">
                            Version {currentVersionNumber}
                        </span>
                        {currentVersionId && (
                            <span className="text-xs text-gray-500">{currentVersionId.substring(0, 8)}...</span>
                        )}
                    </div>
                </div>

                {/* Change Summary (Neutral Language) */}
                <div className="mt-3 text-sm text-gray-600">
                    <span className="font-medium">Changes:</span>{' '}
                    <span className="text-blue-700">{addedCount} additions</span>
                    {', '}
                    <span className="text-orange-700">{removedCount} deletions</span>
                </div>
            </div>

            {/* Legend */}
            <div className="border-b border-gray-200 p-3 bg-gray-50">
                <div className="text-xs text-gray-600 space-y-1">
                    <div className="font-semibold mb-2">Legend:</div>
                    <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 bg-blue-50 border-l-4 border-blue-400"></div>
                            <span>Added line</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 bg-orange-50 border-l-4 border-orange-400"></div>
                            <span>Removed line</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 bg-white"></div>
                            <span>Unchanged</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Diff Content */}
            {shouldCollapse && isCollapsed ? (
                <div className="p-8 text-center text-gray-500">
                    <p className="mb-2">Large diff collapsed ({totalChanges} changes)</p>
                    <button
                        onClick={() => setIsCollapsed(false)}
                        className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded text-gray-700"
                    >
                        Expand Diff
                    </button>
                </div>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full text-sm font-mono">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 w-16">
                                    Prev #
                                </th>
                                <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 w-16">
                                    Curr #
                                </th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Content</th>
                            </tr>
                        </thead>
                        <tbody>
                            {diffLines.map((line, index) => (
                                <tr key={index} className={`border-b border-gray-100 ${lineStyles[line.type]}`}>
                                    <td className="px-2 py-1 text-xs text-gray-500 text-right">
                                        {line.previousLineNumber || ''}
                                    </td>
                                    <td className="px-2 py-1 text-xs text-gray-500 text-right">
                                        {line.currentLineNumber || ''}
                                    </td>
                                    <td className="px-4 py-1 whitespace-pre-wrap break-words">
                                        {line.type === 'added' && (
                                            <span className="inline-block w-4 text-blue-600 mr-2">+</span>
                                        )}
                                        {line.type === 'removed' && (
                                            <span className="inline-block w-4 text-orange-600 mr-2">-</span>
                                        )}
                                        {line.type === 'unchanged' && (
                                            <span className="inline-block w-4 text-gray-400 mr-2"> </span>
                                        )}
                                        {line.content}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Footer Notice */}
            <div className="border-t border-gray-200 p-3 bg-gray-50 text-xs text-gray-600">
                <p>
                    <strong>Note:</strong> This diff shows content changes only. No approval or quality
                    judgment is implied by the visualization.
                </p>
            </div>
        </div>
    )
}
