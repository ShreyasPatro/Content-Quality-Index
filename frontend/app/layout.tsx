import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'Content Evaluation Dashboard',
    description: 'Internal dashboard for content evaluation and review',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body style={{
                fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
            }}>
                {children}
            </body>
        </html>
    )
}
