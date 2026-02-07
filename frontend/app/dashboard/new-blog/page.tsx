'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { PasteOnlyEditor } from '@/components/PasteOnlyEditor'
import { EvaluationResults } from '@/components/EvaluationResults'
import { createBlog, createVersion, triggerEvaluation } from '@/lib/api/blogs'

/**
 * New Blog Ingestion Page
 * 
 * REGULATORY FLOW:
 * 1. User manually names blog (required, immutable)
 * 2. User pastes content (typing blocked)
 * 3. User explicitly triggers evaluation
 * 4. System creates immutable version
 * 5. System runs locked evaluation pipeline
 * 
 * FORBIDDEN:
 * - Auto-naming blogs
 * - Typing in editor
 * - Auto-evaluation
 * - Optimistic UI updates
 */

const MIN_CONTENT_LENGTH = 100

export default function NewBlogPage() {
    const router = useRouter()

    // Mock mode for testing without backend
    const [mockMode, setMockMode] = useState(false) // Set to true for testing without backend

    // Blog creation state
    const [blogName, setBlogName] = useState('')
    const [blogId, setBlogId] = useState<string | null>(null)
    const [versionId, setVersionId] = useState<string | null>(null)
    const [isCreatingBlog, setIsCreatingBlog] = useState(false)

    // Content state
    const [content, setContent] = useState('')

    // Evaluation state
    const [isEvaluating, setIsEvaluating] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [showResults, setShowResults] = useState(false)

    // STEP 1: Create blog (human-named, immutable)
    const handleCreateBlog = async () => {
        if (!blogName.trim()) {
            setError('Blog name is required')
            return
        }

        setIsCreatingBlog(true)
        setError(null)

        try {
            if (mockMode) {
                // MOCK MODE: Simulate blog creation
                await new Promise(resolve => setTimeout(resolve, 500))
                setBlogId('mock-blog-id-' + Date.now())
            } else {
                // REAL MODE: Call backend API
                const token = localStorage.getItem('token')
                if (!token) throw new Error('Not authenticated')
                const response = await createBlog(blogName.trim(), token)
                setBlogId(response.id)
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create blog')
        } finally {
            setIsCreatingBlog(false)
        }
    }

    // STEP 3: Run evaluation (explicit user action)
    const handleRunEvaluation = async () => {
        if (!blogId || !content) return

        setIsEvaluating(true)
        setError(null)

        try {
            if (mockMode) {
                // MOCK MODE: Simulate evaluation
                console.log('MOCK MODE: Simulating evaluation...')
                console.log('Blog ID:', blogId)
                console.log('Content length:', content.length)

                await new Promise(resolve => setTimeout(resolve, 1500))

                // Show results instead of alert
                setShowResults(true)
                setIsEvaluating(false)
            } else {
                // REAL MODE: Call backend API
                const token = localStorage.getItem('token')
                if (!token) throw new Error('Not authenticated')

                let currentVersionId = versionId

                if (!currentVersionId) {
                    console.log('Creating version for blog:', blogId)
                    const versionResponse = await createVersion(blogId, content, token)
                    console.log('Version created:', versionResponse)
                    currentVersionId = versionResponse.id
                    setVersionId(currentVersionId)
                } else {
                    console.log('Using existing version:', currentVersionId)
                }

                if (!currentVersionId) throw new Error('Failed to get version ID')

                const evalResponse = await triggerEvaluation(blogId, currentVersionId, token)
                console.log('Evaluation triggered:', evalResponse)

                router.push(`/dashboard/blogs/${blogId}/versions/${currentVersionId}`)
            }
        } catch (err) {
            console.error('Evaluation error:', err)
            const errorMessage = err instanceof Error ? err.message : 'Failed to run evaluation'

            if (errorMessage.includes('401') || errorMessage.toLowerCase().includes('credentials')) {
                setError('Session expired. The server rejected your login token. Please Sign Out (in Settings) and Log In again.')
            } else {
                setError(`${errorMessage}\n\nNote: Make sure the backend server is running on ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}`)
            }
            setIsEvaluating(false)
        }
    }

    const isBlogCreated = blogId !== null
    const canRunEvaluation = isBlogCreated && content.length >= MIN_CONTENT_LENGTH

    // Mock evaluation data
    const mockEvaluationData = {
        versionId: 'mock-version-' + Date.now(),
        versionNumber: 1,
        source: 'human_paste',
        createdAt: new Date().toISOString(),
        contentLength: content.length,
        aiLikeness: {
            total: 23,
            breakdown: [
                { category: 'Vocabulary Diversity', score: 7, maxScore: 10 },
                { category: 'Sentence Structure', score: 6, maxScore: 10 },
                { category: 'Transition Quality', score: 5, maxScore: 10 },
                { category: 'Formatting Patterns', score: 5, maxScore: 10 },
            ],
            explanations: [
                { reason: 'Good vocabulary variation detected', evidence: [] },
                { reason: 'Natural sentence flow with varied structures', evidence: [] },
                { reason: 'Some repetitive transition patterns observed', evidence: [] },
            ],
        },
        aeo: {
            total: 68,
            maxTotal: 100,
            pillars: [
                { name: 'Directness', score: 12, maxScore: 15, description: 'Clear, concise answers' },
                { name: 'Structure', score: 10, maxScore: 15, description: 'Logical organization' },
                { name: 'Entities', score: 8, maxScore: 15, description: 'Named entities and specifics' },
                { name: 'Completeness', score: 11, maxScore: 15, description: 'Comprehensive coverage' },
                { name: 'Citability', score: 9, maxScore: 15, description: 'Quotable statements' },
                { name: 'Freshness', score: 10, maxScore: 15, description: 'Current information' },
                { name: 'Trustworthiness', score: 8, maxScore: 10, description: 'Credibility signals' },
            ],
        },
    }

    return (
        <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                    New Blog Submission
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                    Submit blog content for evaluation. Content must be pasted (typing is disabled).
                </p>
            </div>

            {/* Mock Mode Banner */}
            {mockMode && (
                <div className="mb-6 bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-400 dark:border-yellow-600 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                        <svg className="h-6 w-6 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div className="flex-1">
                            <p className="text-sm font-semibold text-yellow-900 dark:text-yellow-200">
                                🧪 MOCK MODE ACTIVE - Testing Without Backend
                            </p>
                            <p className="text-xs text-yellow-800 dark:text-yellow-300 mt-1">
                                This mode simulates the blog creation and evaluation flow to test the paste-only editor enforcement. No data is saved. To use real backend, set mockMode=false in the code.
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                    <div className="flex items-start space-x-2">
                        <svg
                            className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                        <div>
                            <p className="text-sm font-medium text-red-900 dark:text-red-200">Error</p>
                            <p className="text-sm text-red-700 dark:text-red-300 mt-1">{error}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* STEP 1: Blog Name (Required, Immutable) */}
            <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-start justify-between mb-4">
                    <div>
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                            Step 1: Name Your Blog
                        </h2>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            Blog name is required and cannot be changed after creation
                        </p>
                    </div>
                    {isBlogCreated && (
                        <span className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 text-xs font-semibold rounded-full">
                            Created
                        </span>
                    )}
                </div>

                <div className="flex space-x-3">
                    <input
                        type="text"
                        value={blogName}
                        onChange={(e) => setBlogName(e.target.value)}
                        disabled={isBlogCreated || isCreatingBlog}
                        placeholder="Enter blog name..."
                        className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:cursor-not-allowed bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                        maxLength={100}
                    />
                    <button
                        onClick={handleCreateBlog}
                        disabled={!blogName.trim() || isBlogCreated || isCreatingBlog}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {isCreatingBlog ? 'Creating...' : 'Create Blog'}
                    </button>
                </div>

                {isBlogCreated && (
                    <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded text-sm text-blue-900 dark:text-blue-200">
                        <strong>Blog ID:</strong> {blogId}
                    </div>
                )}
            </div>

            {/* STEP 2: Paste Content (Paste-Only) */}
            <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="mb-4">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Step 2: Paste Blog Content
                    </h2>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Paste your blog content. Typing is disabled to ensure content originates externally.
                    </p>
                </div>

                <PasteOnlyEditor
                    value={content}
                    onChange={setContent}
                    disabled={isEvaluating}
                    minLength={MIN_CONTENT_LENGTH}
                />
            </div>

            {/* STEP 3: Run Evaluation (Explicit Action) */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="mb-4">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Step 3: Run Evaluation
                    </h2>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Trigger the locked evaluation pipeline (AI Likeness + AEO scoring)
                    </p>
                </div>

                <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                        {!isBlogCreated && '⚠️ Create blog first'}
                        {isBlogCreated && content.length < MIN_CONTENT_LENGTH && (
                            <>⚠️ Content too short (minimum {MIN_CONTENT_LENGTH} characters)</>
                        )}
                        {canRunEvaluation && !isEvaluating && '✓ Ready to evaluate'}
                        {isEvaluating && '⏳ Evaluation in progress...'}
                    </div>

                    <button
                        onClick={handleRunEvaluation}
                        disabled={!canRunEvaluation || isEvaluating}
                        className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
                    >
                        {isEvaluating ? (
                            <>
                                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                                    <circle
                                        className="opacity-25"
                                        cx="12"
                                        cy="12"
                                        r="10"
                                        stroke="currentColor"
                                        strokeWidth="4"
                                    />
                                    <path
                                        className="opacity-75"
                                        fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                    />
                                </svg>
                                <span>Evaluating...</span>
                            </>
                        ) : (
                            <span>Run Evaluation</span>
                        )}
                    </button>
                </div>

                {/* Audit Notice */}
                <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded text-xs text-gray-600 dark:text-gray-400">
                    <strong>Audit Trail:</strong> This action creates an immutable version with source
                    'human_paste' and triggers deterministic scoring. No approval or rewrite logic is
                    executed.
                </div>
            </div>

            {/* STEP 4: Evaluation Results (After Completion) */}
            {showResults && mockMode && (
                <div className="mt-8">
                    <div className="mb-4 flex items-center justify-between">
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                            Evaluation Results
                        </h2>
                        <button
                            onClick={() => {
                                setShowResults(false)
                                setContent('')
                                setBlogId(null)
                                setBlogName('')
                            }}
                            className="px-4 py-2 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-lg transition-colors"
                        >
                            Start New Submission
                        </button>
                    </div>
                    <EvaluationResults {...mockEvaluationData} />
                </div>
            )}
        </div>
    )
}
