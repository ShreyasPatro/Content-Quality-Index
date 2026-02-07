'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function SettingsPage() {
    const router = useRouter()
    const [darkMode, setDarkMode] = useState(false)
    const [mounted, setMounted] = useState(false)

    // Load dark mode preference on mount
    useEffect(() => {
        setMounted(true)
        const savedMode = localStorage.getItem('darkMode') === 'true'
        setDarkMode(savedMode)
        if (savedMode) {
            document.documentElement.classList.add('dark')
        }
    }, [])

    const handleToggle = () => {
        const newMode = !darkMode
        setDarkMode(newMode)

        // Save preference
        localStorage.setItem('darkMode', String(newMode))

        // Apply dark mode
        if (newMode) {
            document.documentElement.classList.add('dark')
        } else {
            document.documentElement.classList.remove('dark')
        }
    }

    const handleSignOut = () => {
        // Clear tokens
        localStorage.removeItem('token')
        // Clear cookie by setting expiry to past
        document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT; SameSite=Lax'

        // Redirect to login
        router.push('/login')
        router.refresh() // Force refresh to update middleware state logic if needed
    }

    // Prevent hydration mismatch
    if (!mounted) {
        return null
    }

    return (
        <div>
            {/* Breadcrumb */}
            <nav className="mb-4 text-sm text-gray-600 dark:text-gray-400">
                <Link href="/dashboard/blogs" className="hover:text-gray-900 dark:hover:text-white">
                    Dashboard
                </Link>
                <span className="mx-2">/</span>
                <span className="text-gray-900 dark:text-white">Settings</span>
            </nav>

            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Settings</h1>
                <p className="text-gray-600 dark:text-gray-400">Customize your dashboard experience</p>
            </div>

            {/* Settings Sections */}
            <div className="max-w-3xl space-y-6">

                {/* Account Section (Sign Out) */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750">
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Account</h2>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Manage your session</p>
                    </div>
                    <div className="p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="text-base font-medium text-gray-900 dark:text-white">Sign Out</h3>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                    End your session and return to the login screen
                                </p>
                            </div>
                            <button
                                onClick={handleSignOut}
                                className="px-4 py-2 border border-red-300 dark:border-red-700 text-red-700 dark:text-red-400 bg-white dark:bg-red-900/10 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                            >
                                Sign Out
                            </button>
                        </div>
                    </div>
                </div>

                {/* Appearance Section */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750">
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Appearance</h2>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Customize the look and feel of your dashboard</p>
                    </div>

                    <div className="p-6">
                        {/* Dark Mode Toggle */}
                        <div className="flex items-center justify-between">
                            <div className="flex-1">
                                <h3 className="text-base font-medium text-gray-900 dark:text-white">Dark Mode</h3>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                    Switch between light and dark themes
                                </p>
                            </div>

                            {/* Cool Toggle Switch */}
                            <button
                                onClick={handleToggle}
                                className={`relative inline-flex h-8 w-16 items-center rounded-full transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${darkMode ? 'bg-blue-600' : 'bg-gray-300'
                                    }`}
                                role="switch"
                                aria-checked={darkMode}
                                aria-label="Toggle dark mode"
                            >
                                <span
                                    className={`inline-block h-6 w-6 transform rounded-full bg-white shadow-lg transition-transform duration-300 ${darkMode ? 'translate-x-9' : 'translate-x-1'
                                        }`}
                                >
                                    <span className="flex items-center justify-center h-full w-full">
                                        {darkMode ? (
                                            <svg className="h-4 w-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                                            </svg>
                                        ) : (
                                            <svg className="h-4 w-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                                            </svg>
                                        )}
                                    </span>
                                </span>
                            </button>
                        </div>
                    </div>
                </div>

                {/* About Section */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750">
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">About</h2>
                    </div>
                    <div className="p-6 space-y-4">
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Application</h3>
                            <p className="mt-1 text-base text-gray-900 dark:text-white">Content Evaluation Index</p>
                        </div>
                        <div>
                            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">Version</h3>
                            <p className="mt-1 text-base text-gray-900 dark:text-white">1.0.0</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
