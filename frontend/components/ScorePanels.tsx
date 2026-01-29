interface ScorePanelsProps {
    versionId: string
}

// Mock data - replace with actual API call
async function getScores(versionId: string) {
    return {
        aiLikeness: {
            total: 45.2,
            rubricVersion: '1.0.0',
        },
        aeo: {
            total: 72.0,
            rubricVersion: '1.0.0',
        },
    }
}

export async function ScorePanels({ versionId }: ScorePanelsProps) {
    const scores = await getScores(versionId)

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* AI Likeness Panel */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Likeness Score</h3>
                <div className="flex items-baseline space-x-2">
                    <div className="text-4xl font-bold text-red-600">
                        {scores.aiLikeness.total.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-500">/ 100</div>
                </div>
                <div className="text-xs text-gray-500 mt-2">
                    Rubric v{scores.aiLikeness.rubricVersion}
                </div>
                <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                            className="bg-red-500 h-3 rounded-full transition-all"
                            style={{ width: `${scores.aiLikeness.total}%` }}
                        ></div>
                    </div>
                </div>
                <p className="text-sm text-gray-600 mt-3">
                    Lower is better. Scores above 50 indicate high AI-likeness.
                </p>
            </div>

            {/* AEO Score Panel */}
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">AEO Score</h3>
                <div className="flex items-baseline space-x-2">
                    <div className="text-4xl font-bold text-green-600">
                        {scores.aeo.total.toFixed(0)}
                    </div>
                    <div className="text-sm text-gray-500">/ 100</div>
                </div>
                <div className="text-xs text-gray-500 mt-2">
                    Rubric v{scores.aeo.rubricVersion}
                </div>
                <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                            className="bg-green-500 h-3 rounded-full transition-all"
                            style={{ width: `${scores.aeo.total}%` }}
                        ></div>
                    </div>
                </div>
                <p className="text-sm text-gray-600 mt-3">
                    Higher is better. Scores above 70 are considered good.
                </p>
            </div>
        </div>
    )
}
