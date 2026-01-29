export default function DashboardPage() {
    return (
        <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>

            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Overview</h2>
                <p className="text-gray-600 mb-4">
                    Welcome to the Content Evaluation Dashboard. This is a read-only interface for viewing blog content, versions, and evaluation scores.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                    <div className="bg-blue-50 rounded-lg p-4">
                        <div className="text-2xl font-bold text-blue-900">--</div>
                        <div className="text-sm text-blue-700">Total Blogs</div>
                    </div>
                    <div className="bg-green-50 rounded-lg p-4">
                        <div className="text-2xl font-bold text-green-900">--</div>
                        <div className="text-sm text-green-700">Approved Versions</div>
                    </div>
                    <div className="bg-yellow-50 rounded-lg p-4">
                        <div className="text-2xl font-bold text-yellow-900">--</div>
                        <div className="text-sm text-yellow-700">In Review</div>
                    </div>
                </div>
            </div>
        </div>
    )
}
