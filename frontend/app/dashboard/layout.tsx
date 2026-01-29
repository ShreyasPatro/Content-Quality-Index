import Link from 'next/link'

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="min-h-screen bg-gray-50">
            {/* Navigation Header */}
            <header className="bg-white border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center space-x-8">
                            <Link href="/dashboard" className="text-xl font-bold text-gray-900">
                                Content Evaluation Dashboard
                            </Link>
                            <nav className="flex space-x-4">
                                <Link
                                    href="/dashboard/blogs"
                                    className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                                >
                                    Blogs
                                </Link>
                            </nav>
                        </div>
                        <div className="flex items-center space-x-4">
                            {/* Auth Placeholder */}
                            <div className="text-sm text-gray-600">
                                User: <span className="font-medium">reviewer@example.com</span>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {children}
            </main>
        </div>
    )
}
