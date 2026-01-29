export default function VersionDetailLoading() {
    return (
        <div className="animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-6"></div>
            <div className="grid grid-cols-3 gap-6">
                <div className="col-span-2 h-96 bg-gray-200 rounded"></div>
                <div className="space-y-4">
                    <div className="h-48 bg-gray-200 rounded"></div>
                    <div className="h-48 bg-gray-200 rounded"></div>
                </div>
            </div>
        </div>
    )
}
