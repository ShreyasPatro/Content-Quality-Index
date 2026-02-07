import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'Content Evaluation Index - IQOL',
    description: 'Internal dashboard for content evaluation and review',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <head>
                <script
                    dangerouslySetInnerHTML={{
                        __html: `
                            (function() {
                                const darkMode = localStorage.getItem('darkMode') === 'true';
                                if (darkMode) {
                                    document.documentElement.classList.add('dark');
                                }
                            })();
                        `,
                    }}
                />
            </head>
            <body style={{
                fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
            }}>
                {children}
            </body>
        </html>
    )
}
