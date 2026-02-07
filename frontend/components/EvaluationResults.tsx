'use client'

/**
 * EvaluationResults Component
 * 
 * Displays evaluation scores after blog version evaluation completes.
 * Shows AI Likeness and AEO scores with breakdowns and explanations.
 * 
 * REGULATORY: Scores are informational only, no approval implied.
 */

interface AILikenessScore {
    total: number
    breakdown: Array<{
        category: string
        score: number
        maxScore: number
    }>
    explanations: Array<{
        reason: string
        evidence: string[]
    }>
}

interface AEOScore {
    total: number
    maxTotal: number
    pillars: Array<{
        name: string
        score: number
        maxScore: number
        description: string
    }>
}

interface EvaluationResultsProps {
    versionId: string
    versionNumber: number
    source: string
    createdAt: string
    contentLength: number
    aiLikeness: AILikenessScore
    aeo: AEOScore
}

export function EvaluationResults({
    versionId,
    versionNumber,
    source,
    createdAt,
    contentLength,
    aiLikeness,
    aeo,
}: EvaluationResultsProps) {
    return (
        <div className="space-y-6">
            {/* Version Header */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                    Version Information
                </h2>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Version ID</p>
                        <p className="text-sm font-mono text-gray-900 dark:text-white">{versionId}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Version Number</p>
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">v{versionNumber}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Source</p>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200">
                            {source}
                        </span>
                    </div>
                    <div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Content Length</p>
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">
                            {contentLength.toLocaleString()} characters
                        </p>
                    </div>
                </div>
            </div>

            {/* AI Likeness Score */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                        AI Likeness Score
                    </h2>
                    <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                        {aiLikeness.total}%
                    </div>
                </div>

                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Deterministic rubric-based assessment of AI-generated content indicators
                </p>

                {/* Breakdown */}
                <div className="space-y-3">
                    {aiLikeness.breakdown.map((item, idx) => (
                        <div key={idx}>
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                    {item.category}
                                </span>
                                <span className="text-sm text-gray-600 dark:text-gray-400">
                                    {item.score} / {item.maxScore}
                                </span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div
                                    className="bg-blue-600 dark:bg-blue-500 h-2 rounded-full transition-all"
                                    style={{ width: `${(item.score / item.maxScore) * 100}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>

                {/* Explanations */}
                {aiLikeness.explanations.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                            Key Findings
                        </h3>
                        <ul className="space-y-2">
                            {aiLikeness.explanations.map((exp, idx) => (
                                <li key={idx} className="text-sm text-gray-600 dark:text-gray-400">
                                    • {exp.reason}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            {/* AEO Score */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                        AEO Score
                    </h2>
                    <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                        {aeo.total} / {aeo.maxTotal}
                    </div>
                </div>

                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Answer Engine Optimization - 7 Pillar Assessment
                </p>

                {/* Pillars */}
                <div className="space-y-4">
                    {aeo.pillars.map((pillar, idx) => (
                        <div key={idx} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                                <div>
                                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                                        {pillar.name}
                                    </h3>
                                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                                        {pillar.description}
                                    </p>
                                </div>
                                <span className="text-lg font-bold text-purple-600 dark:text-purple-400">
                                    {pillar.score}/{pillar.maxScore}
                                </span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div
                                    className="bg-purple-600 dark:bg-purple-500 h-2 rounded-full transition-all"
                                    style={{ width: `${(pillar.score / pillar.maxScore) * 100}%` }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Disclaimer */}
            <div className="bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <p className="text-xs text-gray-600 dark:text-gray-400">
                    <strong>Note:</strong> Scores are informational only and do not imply approval or rejection.
                    All scoring is deterministic and reproducible. No hidden logic or adaptive scoring is applied.
                </p>
            </div>
        </div>
    )
}
