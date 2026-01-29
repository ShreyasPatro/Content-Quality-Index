import Link from 'next/link'
import { VersionTimeline } from '@/components/VersionTimeline'
import { ScorePanels } from '@/components/ScorePanels'
import { RewriteHistory } from '@/components/RewriteHistory'

// Mock data - replace with actual API calls
async function getBlog(blogId: string) {
    // Placeholder: await fetch(`${process.env.API_URL}/blogs/${blogId}`)
    return {
        id: blogId,
        title: 'Sample Blog Post',
        createdAt: '2026-01-20T10:00:00Z',
        updatedAt: '2026-01-29T10:00:00Z',
    }
}

async function getVersions(blogId: string) {
    // Placeholder: await fetch(`${process.env.API_URL}/blogs/${blogId}/versions`)
    return [
        {
            id: 'v1-uuid',
            versionNumber: 1,
            state: 'approved' as const,
            parentVersionId: null,
            createdAt: '2026-01-20T10:00:00Z',
            source: 'initial' as const,
            isLatest: false,
            isApproved: true,
        },
        {
            id: 'v2-uuid',
            versionNumber: 2,
            state: 'rejected' as const,
            parentVersionId: 'v1-uuid',
            createdAt: '2026-01-25T14:30:00Z',
            source: 'rewrite' as const,
            isLatest: false,
            isApproved: false,
        },
        {
            id: 'v3-uuid',
            versionNumber: 3,
            state: 'in_review' as const,
            parentVersionId: 'v2-uuid',
            createdAt: '2026-01-29T10:00:00Z',
            source: 'manual_edit' as const,
            isLatest: true,
            isApproved: false,
        },
    ]
}

async function getRewriteHistory(blogId: string) {
    // Placeholder: await fetch(`${process.env.API_URL}/blogs/${blogId}/rewrites`)
    return [
        {
            id: 'rewrite-1',
            sourceVersionId: 'v1-uuid',
            sourceVersionNumber: 1,
            targetVersionId: 'v2-uuid',
            targetVersionNumber: 2,
            triggerType: 'aeo' as const,
            triggerSignals: {
                aeoScore: 65.0,
                specificDeficits: [
                    'Answerability: 12/25 (below threshold of 15)',
                    'Freshness: 2/10 (below threshold of 5)',
                ],
            },
            rewritePrompt: `You are a content rewrite engine. Your task is to improve the following content based on specific, deterministic instructions.

INSTRUCTIONS:
1. Move the direct answer to the main question into the first 120 words
2. Add a "Last Updated" section with current date
3. Include at least 2 citations from 2025 or later

ORIGINAL CONTENT:
[Content would be here...]

OUTPUT:
Provide only the rewritten content. Do not add commentary or explanations.`,
            timestamp: '2026-01-25T14:30:00Z',
            status: 'completed' as const,
        },
    ]
}

export default async function BlogDetailPage({
    params,
}: {
    params: { blogId: string }
}) {
    const blog = await getBlog(params.blogId)
    const versions = await getVersions(params.blogId)
    const rewriteHistory = await getRewriteHistory(params.blogId)

    const latestVersion = versions.find(v => v.isLatest)
    const approvedVersion = versions.find(v => v.isApproved)

    return (
        <div>
            {/* Breadcrumb */}
            <nav className="mb-4 text-sm text-gray-600">
                <Link href="/dashboard/blogs" className="hover:text-gray-900">Blogs</Link>
                <span className="mx-2">/</span>
                <span className="text-gray-900">{blog.title}</span>
            </nav>

            {/* Header */}
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{blog.title}</h1>
                <div className="flex gap-4">
                    {approvedVersion && (
                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-md text-sm font-medium">
                            ✓ Approved: v{approvedVersion.versionNumber}
                        </span>
                    )}
                    {latestVersion && (
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-md text-sm font-medium">
                            Latest: v{latestVersion.versionNumber}
                        </span>
                    )}
                </div>
            </div>

            {/* Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Timeline */}
                <div className="lg:col-span-1">
                    <VersionTimeline versions={versions} blogId={params.blogId} />
                </div>

                {/* Scores and Details */}
                <div className="lg:col-span-2 space-y-6">
                    {latestVersion && (
                        <ScorePanels versionId={latestVersion.id} />
                    )}

                    <RewriteHistory entries={rewriteHistory} blogId={params.blogId} />
                </div>
            </div>
        </div>
    )
}
