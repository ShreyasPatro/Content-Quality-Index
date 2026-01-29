import Link from 'next/link'
import { DiffViewer } from '@/components/DiffViewer'

// Mock data - replace with actual API calls
async function getVersion(versionId: string) {
    return {
        id: versionId,
        versionNumber: 3,
        state: 'in_review',
        content: '# Sample Content v3\n\nThis is the updated blog post content.\n\nNew paragraph added here.\n\nAnother change.',
        createdAt: '2026-01-29T10:00:00Z',
        blogId: '1',
        blogTitle: 'Sample Blog Post',
        parentVersionId: 'v2-uuid',
    }
}

async function getParentVersion(parentVersionId: string) {
    return {
        id: parentVersionId,
        versionNumber: 2,
        content: '# Sample Content v2\n\nThis is the blog post content.\n\nOriginal paragraph.\n\nAnother change.',
        createdAt: '2026-01-28T10:00:00Z',
    }
}

export default async function VersionDiffPage({
    params,
}: {
    params: { blogId: string; versionId: string; compareId: string }
}) {
    const currentVersion = await getVersion(params.versionId)
    const parentVersion = await getParentVersion(params.compareId)

    return (
        <div>
            {/* Breadcrumb */}
            <nav className="mb-4 text-sm text-gray-600">
                <Link href="/dashboard/blogs" className="hover:text-gray-900">
                    Blogs
                </Link>
                <span className="mx-2">/</span>
                <Link href={`/dashboard/blogs/${params.blogId}`} className="hover:text-gray-900">
                    {currentVersion.blogTitle}
                </Link>
                <span className="mx-2">/</span>
                <Link
                    href={`/dashboard/blogs/${params.blogId}/versions/${params.versionId}`}
                    className="hover:text-gray-900"
                >
                    Version {currentVersion.versionNumber}
                </Link>
                <span className="mx-2">/</span>
                <span className="text-gray-900">Diff</span>
            </nav>

            {/* Header */}
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Version Comparison</h1>
                <p className="text-gray-600">
                    Comparing v{parentVersion.versionNumber} → v{currentVersion.versionNumber}
                </p>
            </div>

            {/* Diff Viewer */}
            <DiffViewer
                previousContent={parentVersion.content}
                currentContent={currentVersion.content}
                previousVersionNumber={parentVersion.versionNumber}
                currentVersionNumber={currentVersion.versionNumber}
                previousVersionId={parentVersion.id}
                currentVersionId={currentVersion.id}
            />
        </div>
    )
}
