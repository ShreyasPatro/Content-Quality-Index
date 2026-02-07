export default function NewBlogLoading() {
    return (
        <div className="max-w-4xl mx-auto">
            {/* Header Skeleton */}
            <div className="mb-8">
                <div className="h-9 w-64 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
                <div className="h-5 w-96 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            </div>

            {/* Blog Name Section Skeleton */}
            <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="h-6 w-48 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-4" />
                <div className="flex space-x-3">
                    <div className="flex-1 h-10 bg-gray-100 dark:bg-gray-700 rounded animate-pulse" />
                    <div className="h-10 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
                </div>
            </div>

            {/* Content Section Skeleton */}
            <div className="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="h-6 w-56 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-4" />
                <div className="h-96 bg-gray-100 dark:bg-gray-700 rounded animate-pulse" />
            </div>

            {/* Evaluation Section Skeleton */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="h-6 w-48 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-4" />
                <div className="flex items-center justify-between">
                    <div className="h-5 w-64 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
                    <div className="h-12 w-40 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
                </div>
            </div>
        </div>
    )
}
