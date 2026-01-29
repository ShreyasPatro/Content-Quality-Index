'use client'

interface PillarScore {
    name: string
    score: number
    maxScore: number
    description: string
}

interface ScoreBreakdownProps {
    pillars: PillarScore[]
    totalScore: number
    maxTotalScore: number
    rubricVersion: string
    scoreType: 'ai_likeness' | 'aeo'
}

export function ScoreBreakdown({
    pillars,
    totalScore,
    maxTotalScore,
    rubricVersion,
    scoreType,
}: ScoreBreakdownProps) {
    // Neutral color (no green/red)
    const barColor = scoreType === 'ai_likeness' ? 'bg-blue-500' : 'bg-purple-500'
    const barBgColor = 'bg-gray-200'

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                    {scoreType === 'ai_likeness' ? 'AI Likeness' : 'AEO'} Score Breakdown
                </h3>
                <span className="text-xs text-gray-500">Rubric v{rubricVersion}</span>
            </div>

            {/* Total Score */}
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-baseline space-x-2">
                    <span className="text-3xl font-bold text-gray-900">{totalScore.toFixed(1)}</span>
                    <span className="text-lg text-gray-500">/ {maxTotalScore}</span>
                </div>
                <p className="text-xs text-gray-600 mt-1">
                    Total score (sum of all pillars below)
                </p>
            </div>

            {/* Pillar Breakdown */}
            <div className="space-y-4">
                {pillars.map((pillar) => {
                    const percentage = (pillar.score / pillar.maxScore) * 100

                    return (
                        <div key={pillar.name}>
                            <div className="flex items-center justify-between mb-1">
                                <span className="text-sm font-medium text-gray-700">{pillar.name}</span>
                                <span className="text-sm font-medium text-gray-900">
                                    {pillar.score.toFixed(1)} / {pillar.maxScore}
                                </span>
                            </div>

                            {/* Progress Bar (Neutral) */}
                            <div className={`w-full ${barBgColor} rounded-full h-3 mb-1`}>
                                <div
                                    className={`${barColor} h-3 rounded-full transition-all`}
                                    style={{ width: `${percentage}%` }}
                                ></div>
                            </div>

                            {/* Description */}
                            <p className="text-xs text-gray-600">{pillar.description}</p>
                        </div>
                    )
                })}
            </div>

            {/* Disclaimer */}
            <div className="mt-6 p-3 bg-gray-50 rounded text-xs text-gray-600">
                <p className="font-semibold mb-1">Important:</p>
                <p>
                    This breakdown shows component scores only. No quality judgment, approval readiness, or
                    recommendation is implied by these values.
                </p>
            </div>
        </div>
    )
}
