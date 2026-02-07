'use client'

import { useState } from 'react'
import { AEOScoreResult, analyzeAEOSandbox } from '@/lib/api/sandbox'

// Placeholder for auth token - in real app this comes from context/hook
const MOCK_TOKEN = 'sandbox_token'

export default function AEOSandboxPage() {
    const [content, setContent] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<AEOScoreResult | null>(null)
    const [error, setError] = useState<string | null>(null)

    const handleAnalyze = async () => {
        if (!content.trim()) return

        setLoading(true)
        setError(null)
        setResult(null)

        try {
            // In a real app, use useAuth() to get the token
            // Here we assume the backend handles auth or allows the sandbox endpoint
            const data = await analyzeAEOSandbox(content, MOCK_TOKEN)
            setResult(data.aeo)
        } catch (err: any) {
            setError(err.message || 'Analysis failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">AEO Sandbox</h1>
            <p className="text-gray-600 mb-8">
                Test content against the AEO Rubric without saving to the database.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Input Section */}
                <div className="bg-white p-6 rounded-lg shadow h-fit">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Content to Analyze
                    </label>
                    <textarea
                        className="w-full h-96 p-4 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                        placeholder="# Paste your markdown content here..."
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                    />
                    <div className="mt-4 flex justify-end">
                        <button
                            onClick={handleAnalyze}
                            disabled={loading || !content.trim()}
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                        >
                            {loading ? 'Analyzing...' : 'Analyze Score'}
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
                                    <span className="block text-3xl font-bold text-blue-600">
                                        {result.total_score}
                                        <span className="text-lg text-gray-400 font-normal">/100</span>
                                    </span>
                                    <span className="text-xs text-gray-500">Rubric {result.rubric_version}</span>
                                </div>
                            </div>

                            <div className="space-y-4">
                                {Object.entries(result.pillars).map(([key, pillar]) => (
                                    <div key={key} className="border-b border-gray-100 last:border-0 pb-4 last:pb-0">
                                        <div className="flex justify-between items-center mb-1">
                                            <span className="font-medium text-gray-700 capitalize">
                                                {key.replace('aeo_', '').replace('_', ' ')}
                                            </span>
                                            <span className="font-mono font-semibold text-gray-900">
                                                {pillar.score}/{pillar.max_score}
                                            </span>
                                        </div>
                                        {/* Progress Bar */}
                                        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                                            <div
                                                className={`h-2 rounded-full ${pillar.score === pillar.max_score ? 'bg-green-500' : 'bg-blue-500'
                                                    }`}
                                                style={{ width: `${(pillar.score / pillar.max_score) * 100}%` }}
                                            ></div>
                                        </div>
                                        {/* Reasons */}
                                        <ul className="text-sm text-gray-600 space-y-1 mt-2">
                                            {pillar.reason.map((reason, idx) => (
                                                <li key={idx} className="flex items-start">
                                                    <span className="mr-2 text-blue-400">•</span>
                                                    {reason}
                                                </li>
                                            ))}
                                        </ul>
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
