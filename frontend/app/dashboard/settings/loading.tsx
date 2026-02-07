export default function SettingsLoading() {
    return (
        <div>
            {/* Breadcrumb Skeleton */}
            <div className="mb-4 h-5 w-48 bg-gray-200 rounded animate-pulse" />

            {/* Header Skeleton */}
            <div className="mb-8">
                <div className="h-9 w-32 bg-gray-200 rounded animate-pulse mb-2" />
                <div className="h-5 w-64 bg-gray-200 rounded animate-pulse" />
            </div>

            {/* Settings Cards Skeleton */}
            <div className="max-w-3xl space-y-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                        <div className="h-6 w-32 bg-gray-200 rounded animate-pulse" />
                    </div>
                    <div className="p-6">
                        <div className="h-20 bg-gray-100 rounded animate-pulse" />
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                        <div className="h-6 w-24 bg-gray-200 rounded animate-pulse" />
                    </div>
                    <div className="p-6 space-y-4">
                        <div className="h-16 bg-gray-100 rounded animate-pulse" />
                        <div className="h-16 bg-gray-100 rounded animate-pulse" />
                    </div>
                </div>
            </div>
        </div>
    )
}
