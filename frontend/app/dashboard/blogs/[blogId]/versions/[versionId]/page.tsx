import Link from 'next/link'
import { ScoreTrendChart } from '@/components/ScoreTrendChart'
import { ScoreBreakdown } from '@/components/ScoreBreakdown'
import { ScoreExplanation } from '@/components/ScoreExplanation'
import { ApprovalPanel } from '@/components/ApprovalPanel'

// Mock data - replace with actual API calls
async function getVersion(versionId: string) {
    return {
        id: versionId,
        versionNumber: 3,
        state: 'in_review' as 'draft' | 'in_review' | 'approved' | 'rejected' | 'archived',
        content: '# Sample Content v3\n\nThis is the updated blog post content.\n\nNew paragraph added here.\n\nAnother change.',
        createdAt: '2026-01-29T10:00:00Z',
        reviewStartedAt: '2026-01-29T22:45:00Z', // Started 4 minutes ago for demo
        blogId: '1',
        blogTitle: 'Sample Blog Post',
        parentVersionId: 'v2-uuid',
    }
}

async function getScores(versionId: string) {
    return {
        aiLikeness: {
            total: 45.2,
            rubricVersion: '1.0.0',
            pillars: [
                { name: 'Repetitive Phrases', score: 12.5, maxScore: 25, description: 'Frequency of repeated sentence structures' },
                { name: 'Unnatural Flow', score: 18.3, maxScore: 25, description: 'Awkward transitions and pacing' },
                { name: 'Generic Language', score: 14.4, maxScore: 25, description: 'Use of clichés and filler words' },
                { name: 'Lack of Voice', score: 0, maxScore: 25, description: 'Absence of personal style' },
            ],
            explanations: [
                {
                    pillar: 'Repetitive Phrases',
                    reason: 'Multiple instances of similar sentence structures detected',
                    evidence: [
                        'Phrase "it is important to" appears 3 times',
                        'Sentence structure "X is Y because Z" repeated 4 times',
                    ],
                },
                {
                    pillar: 'Unnatural Flow',
                    reason: 'Transitions between paragraphs lack cohesion',
                    evidence: [
                        'Abrupt topic shift at paragraph 3',
                        'No connecting phrases between sections',
                    ],
                },
            ],
        },
        aeo: {
            total: 72.0,
            rubricVersion: '1.0.0',
            pillars: [
                { name: 'Answerability', score: 18, maxScore: 25, description: 'Direct answer in first 120 words' },
                { name: 'Structure', score: 14, maxScore: 15, description: 'Extractable headings and lists' },
                { name: 'Specificity', score: 16, maxScore: 20, description: 'Concrete examples and data' },
                { name: 'Trust', score: 10, maxScore: 15, description: 'Citations and author expertise' },
                { name: 'Coverage', score: 8, maxScore: 10, description: 'Comprehensive topic coverage' },
                { name: 'Freshness', score: 3, maxScore: 10, description: 'Recent information and updates' },
                { name: 'Readability', score: 3, maxScore: 5, description: 'Clear language and formatting' },
            ],
            explanations: [
                {
                    pillar: 'Answerability',
                    reason: 'Direct answer provided early but could be more concise',
                    evidence: [
                        'Answer starts at word 45 (within 120-word limit)',
                        'Answer is 2 sentences long',
                    ],
                },
                {
                    pillar: 'Freshness',
                    reason: 'Content references outdated information',
                    evidence: [
                        'Most recent citation is from 2024',
                        'No mention of 2025-2026 developments',
                    ],
                },
            ],
        },
    }
}

async function getScoreHistory(blogId: string) {
    return {
        aiLikeness: [
            { versionNumber: 1, score: 52.3, timestamp: '2026-01-20T10:00:00Z' },
            { versionNumber: 2, score: 48.7, timestamp: '2026-01-25T14:30:00Z' },
            { versionNumber: 3, score: 45.2, timestamp: '2026-01-29T10:00:00Z' },
        ],
        aeo: [
            { versionNumber: 1, score: 65.0, timestamp: '2026-01-20T10:00:00Z' },
            { versionNumber: 2, score: 68.5, timestamp: '2026-01-25T14:30:00Z' },
            { versionNumber: 3, score: 72.0, timestamp: '2026-01-29T10:00:00Z' },
        ],
    }
}

export default async function VersionDetailPage({
    params,
}: {
    params: { blogId: string; versionId: string }
}) {
    const version = await getVersion(params.versionId)
    const scores = await getScores(params.versionId)
    const history = await getScoreHistory(params.blogId)

    return (
        <div>
            {/* Breadcrumb */}
            <nav className="mb-4 text-sm text-gray-600">
                <Link href="/dashboard/blogs" className="hover:text-gray-900">
                    Blogs
                </Link>
                <span className="mx-2">/</span>
                <Link href={`/dashboard/blogs/${params.blogId}`} className="hover:text-gray-900">
                    {version.blogTitle}
                </Link>
                <span className="mx-2">/</span>
                <span className="text-gray-900">Version {version.versionNumber}</span>
            </nav>

            {/* Header */}
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    {version.blogTitle} - Version {version.versionNumber}
                </h1>
                <div className="flex gap-4 items-center">
                    <span
                        className={
                            version.state === 'approved'
                                ? 'px-3 py-1 rounded-md text-sm font-medium bg-green-100 text-green-800'
                                : version.state === 'in_review'
                                    ? 'px-3 py-1 rounded-md text-sm font-medium bg-yellow-100 text-yellow-800'
                                    : 'px-3 py-1 rounded-md text-sm font-medium bg-gray-100 text-gray-800'
                        }
                    >
                        {version.state.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="text-sm text-gray-600">
                        Created: {new Date(version.createdAt).toLocaleString()}
                    </span>
                </div>
            </div>

            {/* Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Content */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Content */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">Content</h2>
                        <div className="prose max-w-none">
                            <pre className="whitespace-pre-wrap text-sm text-gray-700">{version.content}</pre>
                        </div>
                    </div>

                    {/* Score Trends */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <ScoreTrendChart
                            data={history.aiLikeness}
                            title="AI Likeness Trend"
                            scoreType="ai_likeness"
                        />
                        <ScoreTrendChart data={history.aeo} title="AEO Score Trend" scoreType="aeo" />
                    </div>

                    {/* Score Explanations */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <ScoreExplanation
                            explanations={scores.aiLikeness.explanations}
                            scoreType="ai_likeness"
                        />
                        <ScoreExplanation explanations={scores.aeo.explanations} scoreType="aeo" />
                    </div>

                    {/* Approval Panel */}
                    <ApprovalPanel
                        versionId={version.id}
                        versionNumber={version.versionNumber}
                        currentState={version.state}
                        reviewStartedAt={version.reviewStartedAt}
                        isDisabled={true}
                    />
                </div>

                {/* Sidebar - Score Breakdowns */}
                <div className="lg:col-span-1 space-y-6">
                    <ScoreBreakdown
                        pillars={scores.aiLikeness.pillars}
                        totalScore={scores.aiLikeness.total}
                        maxTotalScore={100}
                        rubricVersion={scores.aiLikeness.rubricVersion}
                        scoreType="ai_likeness"
                    />
                    <ScoreBreakdown
                        pillars={scores.aeo.pillars}
                        totalScore={scores.aeo.total}
                        maxTotalScore={100}
                        rubricVersion={scores.aeo.rubricVersion}
                        scoreType="aeo"
                    />
                </div>
            </div>
        </div>
    )
}
