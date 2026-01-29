import Link from 'next/link'

export interface VersionNode {
    id: string
    versionNumber: number
    state: 'draft' | 'in_review' | 'approved' | 'rejected' | 'archived'
    parentVersionId: string | null
    createdAt: string
    source?: 'manual_edit' | 'rewrite' | 'initial' // Optional: may be missing from backend
    isLatest: boolean
    isApproved: boolean
}

interface VersionNodeProps {
    version: VersionNode
    blogId: string
    showConnector: boolean
}

function VersionNodeComponent({ version, blogId, showConnector }: VersionNodeProps) {
    // State-based styling (neutral colors, no correctness implied)
    const stateStyles = {
        approved: 'bg-green-50 border-green-300 text-green-900',
        rejected: 'bg-red-50 border-red-300 text-red-900',
        in_review: 'bg-yellow-50 border-yellow-300 text-yellow-900',
        draft: 'bg-gray-50 border-gray-300 text-gray-900',
        archived: 'bg-gray-100 border-gray-400 text-gray-600',
    }

    const stateIcons = {
        approved: '✓',
        rejected: '✗',
        in_review: '⏱',
        draft: '○',
        archived: '◌',
    }

    return (
        <div className="relative">
            {/* Connector Line */}
            {showConnector && (
                <div className="absolute left-4 top-12 bottom-0 w-0.5 bg-gray-300"></div>
            )}

            {/* Version Node */}
            <Link
                href={`/dashboard/blogs/${blogId}/versions/${version.id}`}
                className="block hover:bg-gray-50 rounded-lg p-3 transition-colors border border-transparent hover:border-gray-200"
            >
                <div className="flex items-start space-x-3">
                    {/* Status Indicator */}
                    <div
                        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center border-2 ${stateStyles[version.state]}`}
                    >
                        <span className="text-sm font-bold">{stateIcons[version.state]}</span>
                    </div>

                    {/* Version Info */}
                    <div className="flex-1 min-w-0">
                        {/* Version Number + Badges */}
                        <div className="flex items-center space-x-2 mb-1">
                            <span className="font-semibold text-gray-900">v{version.versionNumber}</span>
                            {version.isApproved && (
                                <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded font-medium">
                                    APPROVED
                                </span>
                            )}
                            {version.isLatest && !version.isApproved && (
                                <span className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded font-medium">
                                    LATEST
                                </span>
                            )}
                        </div>

                        {/* Metadata */}
                        <div className="text-xs text-gray-600 space-y-0.5">
                            <div>
                                <span className="font-medium">ID:</span> {version.id.substring(0, 8)}...
                            </div>
                            <div>
                                <span className="font-medium">Parent:</span>{' '}
                                {version.parentVersionId ? version.parentVersionId.substring(0, 8) + '...' : 'root'}
                            </div>
                            <div>
                                <span className="font-medium">Source:</span>{' '}
                                {version.source ? (
                                    <span className="capitalize">{version.source.replace('_', ' ')}</span>
                                ) : (
                                    <span className="text-gray-400 italic">Unknown source</span>
                                )}
                            </div>
                            <div>
                                <span className="font-medium">Created:</span>{' '}
                                {new Date(version.createdAt).toLocaleString()}
                            </div>
                            <div>
                                <span className="font-medium">Status:</span>{' '}
                                <span className="capitalize">{version.state.replace('_', ' ')}</span>
                            </div>
                            {version.parentVersionId && (
                                <div className="mt-2">
                                    <Link
                                        href={`/dashboard/blogs/${blogId}/versions/${version.id}/diff/${version.parentVersionId}`}
                                        className="text-blue-600 hover:text-blue-800 text-xs font-medium"
                                    >
                                        → View Diff from Parent
                                    </Link>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </Link>
        </div>
    )
}

interface VersionTimelineProps {
    versions: VersionNode[]
    blogId: string
}

export function VersionTimeline({ versions, blogId }: VersionTimelineProps) {
    // Sort versions by creation date (newest first)
    const sortedVersions = [...versions].sort(
        (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    )

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Version Timeline</h2>

            {/* Legend */}
            <div className="mb-4 p-3 bg-gray-50 rounded text-xs space-y-1">
                <div className="font-semibold text-gray-700 mb-2">Legend:</div>
                <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-full bg-green-50 border-2 border-green-300 flex items-center justify-center text-green-900">
                        ✓
                    </span>
                    <span className="text-gray-600">Approved</span>
                </div>
                <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-full bg-yellow-50 border-2 border-yellow-300 flex items-center justify-center text-yellow-900">
                        ⏱
                    </span>
                    <span className="text-gray-600">In Review</span>
                </div>
                <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-full bg-red-50 border-2 border-red-300 flex items-center justify-center text-red-900">
                        ✗
                    </span>
                    <span className="text-gray-600">Rejected</span>
                </div>
                <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-full bg-gray-50 border-2 border-gray-300 flex items-center justify-center text-gray-900">
                        ○
                    </span>
                    <span className="text-gray-600">Draft</span>
                </div>
            </div>

            {/* Timeline */}
            <div className="space-y-4">
                {sortedVersions.length === 0 ? (
                    <p className="text-gray-500 text-sm">No versions yet.</p>
                ) : (
                    sortedVersions.map((version, index) => (
                        <VersionNodeComponent
                            key={version.id}
                            version={version}
                            blogId={blogId}
                            showConnector={index < sortedVersions.length - 1}
                        />
                    ))
                )}
            </div>
        </div>
    )
}
