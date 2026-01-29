export default function DiffLoading() {
    return (
        <div className="animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-6"></div>
            <div className="bg-white rounded-lg shadow p-6">
                <div className="h-64 bg-gray-200 rounded"></div>
            </div>
        </div>
    )
}
