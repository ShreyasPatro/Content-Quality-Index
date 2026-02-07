'use client'

import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { getUserFromToken, logout } from '@/lib/auth'

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const [userEmail, setUserEmail] = useState<string>('Loading...')

    useEffect(() => {
        const user = getUserFromToken()
        if (user && user.email) {
            setUserEmail(user.email)
        } else {
            // Optional: Redirect to login if token is invalid/missing?
            // For now, just show 'Guest' or similar
            setUserEmail('Guest')
        }
    }, [])

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            {/* Navigation Header */}
            <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center space-x-8">
                            <Link href="/dashboard" className="flex items-center space-x-3">
                                <div className="text-xl font-bold text-gray-900 dark:text-white">
                                    Content Evaluation Index
                                </div>
                                <div className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs font-semibold rounded">
                                    IQOL
                                </div>
                            </Link>
                            <nav className="flex space-x-4">
                                <Link
                                    href="/dashboard/blogs"
                                    className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                                >
                                    Blogs
                                </Link>
                                <Link
                                    href="/dashboard/new-blog"
                                    className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                                >
                                    New Blog
                                </Link>
                                <Link
                                    href="/dashboard/settings"
                                    className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium"
                                >
                                    Settings
                                </Link>
                                <Link
                                    href="/dashboard/sandbox"
                                    className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium border border-blue-200 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-800"
                                >
                                    AEO Sandbox
                                </Link>
                                <Link
                                    href="/dashboard/sandbox-ai"
                                    className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white px-3 py-2 rounded-md text-sm font-medium border border-purple-200 bg-purple-50 dark:bg-purple-900/20 dark:border-purple-800 ml-2"
                                >
                                    AI Sandbox
                                </Link>
                            </nav>
                        </div>
                        <div className="flex items-center space-x-4">
                            {/* Auth Info */}
                            <div className="text-sm text-gray-600 dark:text-gray-300 flex items-center space-x-4">
                                <span>
                                    User: <span className="font-medium text-gray-900 dark:text-white">{userEmail}</span>
                                </span>
                                <button
                                    onClick={logout}
                                    className="text-xs text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 font-medium"
                                >
                                    Logout
                                </button>
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
