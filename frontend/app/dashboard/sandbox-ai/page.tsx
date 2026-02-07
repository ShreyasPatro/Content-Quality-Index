'use client'

import { useState } from 'react'
import { SandboxAIResponse, analyzeAISandbox } from '@/lib/api/sandbox'

// Placeholder for auth token
const MOCK_TOKEN = 'sandbox_token'

export default function AISandboxPage() {
    const [content, setContent] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<SandboxAIResponse | null>(null)
    const [error, setError] = useState<string | null>(null)

    const handleAnalyze = async () => {
        if (!content.trim()) return

        setLoading(true)
        setError(null)
        setResult(null)

        try {
            const data = await analyzeAISandbox(content, MOCK_TOKEN)
            setResult(data)
        } catch (err: any) {
            setError(err.message || 'Analysis failed')
        } finally {
            setLoading(false)
        }
    }

    // Helper to determine score color (High Score in AI Likeness = BAD)
    const getScoreColor = (score: number) => {
        if (score < 30) return 'text-green-600'
        if (score < 60) return 'text-yellow-600'
        return 'text-red-600'
    }

    const getScoreBg = (score: number) => {
        if (score < 30) return 'bg-green-500'
        if (score < 60) return 'bg-yellow-500'
        return 'bg-red-500'
    }

    return (
        <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Likeness Sandbox</h1>
            <p className="text-gray-600 mb-8">
                Test content against the Internal AI Rubric without saving to database.
                <br />
                <span className="text-sm italic text-gray-500">Note: Higher scores indicate higher probability of AI generation.</span>
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Input Section */}
                <div className="bg-white p-6 rounded-lg shadow h-fit">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Content to Analyze
                    </label>
                    <textarea
                        className="w-full h-96 p-4 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500 font-mono text-sm"
                        placeholder="# Paste your content here..."
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                    />
                    <div className="mt-4 flex justify-end">
                        <button
                            onClick={handleAnalyze}
                            disabled={loading || !content.trim()}
                            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                        >
                            {loading ? 'Analyzing...' : 'Check AI Likeness'}
                        </button>
                    </div>
                    {error && (
                        <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-md text-sm">
                            {error}
                        </div>
                    )}
                </div>

                {/* Results Section */}
                <div>
                    {result ? (
                        <div className="bg-white p-6 rounded-lg shadow space-y-6">
                            <div className="flex items-center justify-between border-b pb-4">
                                <h2 className="text-xl font-bold text-gray-900">Analysis Results</h2>
                                <div className="text-right">
                                    <span className={`block text-3xl font-bold ${getScoreColor(result.score)}`}>
                                        {result.score.toFixed(1)}
                                        <span className="text-lg text-gray-400 font-normal">/100</span>
                                    </span>
                                    <span className="text-xs text-gray-500">Rubric {result.raw_response.rubric_version}</span>
                                </div>
                            </div>

                            <div className="space-y-4">
                                {Object.entries(result.raw_response.subscores).map(([key, subscore]) => (
                                    <div key={key} className="border-b border-gray-100 last:border-0 pb-4 last:pb-0">
                                        <div className="flex justify-between items-center mb-1">
                                            <span className="font-medium text-gray-700 capitalize">
                                                {key.replace(/_/g, ' ')}
                                            </span>
                                            <span className="font-mono font-semibold text-gray-900">
                                                {subscore.score}/{subscore.max_score}
                                            </span>
                                        </div>
                                        {/* Progress Bar */}
                                        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                                            <div
                                                className={`h-2 rounded-full ${getScoreBg(subscore.percentage * 100)}`}
                                                style={{ width: `${Math.min(subscore.percentage * 100, 100)}%` }}
                                            ></div>
                                        </div>
                                        {/* Explanation */}
                                        <p className="text-sm text-gray-600 italic mb-2">
                                            {subscore.explanation}
                                        </p>
                                        {/* Evidence */}
                                        {subscore.evidence && subscore.evidence.length > 0 && (
                                            <div className="bg-gray-50 p-2 rounded text-xs text-gray-500 font-mono">
                                                <span className="font-semibold block mb-1">Evidence:</span>
                                                <ul className="list-disc pl-4 space-y-1">
                                                    {subscore.evidence.slice(0, 3).map((ev, idx) => (
                                                        <li key={idx} className="truncate">{ev}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center text-gray-400">
                            Results will appear here
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
