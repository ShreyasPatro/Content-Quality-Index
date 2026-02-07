'use client'

import { useState } from 'react'

/**
 * PasteOnlyEditor
 * 
 * REGULATORY CONSTRAINT: This editor ONLY accepts content via clipboard paste.
 * All keyboard input is blocked to ensure content originates externally.
 * 
 * AUDIT TRAIL: Content source is provably clipboard, not typed.
 */

interface PasteOnlyEditorProps {
    value: string
    onChange: (value: string) => void
    disabled?: boolean
    placeholder?: string
    minLength?: number
}

export function PasteOnlyEditor({
    value,
    onChange,
    disabled = false,
    placeholder = 'Paste your blog content here (typing is disabled)',
    minLength = 100,
}: PasteOnlyEditorProps) {
    const [showTypingWarning, setShowTypingWarning] = useState(false)
    const [lastPasteTime, setLastPasteTime] = useState<number | null>(null)

    // SECURITY: Block ALL keyboard input except navigation
    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        const allowedNavigationKeys = [
            'ArrowUp',
            'ArrowDown',
            'ArrowLeft',
            'ArrowRight',
            'PageUp',
            'PageDown',
            'Home',
            'End',
            'Tab',
        ]

        const isCtrlA = (e.ctrlKey || e.metaKey) && e.key === 'a'
        const isCtrlC = (e.ctrlKey || e.metaKey) && e.key === 'c'
        const isCtrlV = (e.ctrlKey || e.metaKey) && e.key === 'v'
        const isCtrlX = (e.ctrlKey || e.metaKey) && e.key === 'x'

        // Allow: navigation, select all, copy, paste
        if (
            allowedNavigationKeys.includes(e.key) ||
            isCtrlA ||
            isCtrlC ||
            isCtrlV ||
            isCtrlX
        ) {
            return
        }

        // Block everything else
        e.preventDefault()
        e.stopPropagation()

        // Show warning
        setShowTypingWarning(true)
        setTimeout(() => setShowTypingWarning(false), 3000)
    }

    // SECURITY: Block beforeinput (IME, autocomplete, dictation)
    const handleBeforeInput = (e: React.FormEvent<HTMLTextAreaElement>) => {
        e.preventDefault()
    }

    // SECURITY: Block drag and drop
    const handleDrop = (e: React.DragEvent<HTMLTextAreaElement>) => {
        e.preventDefault()
    }

    // ALLOWED: Clipboard paste only
    const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
        e.preventDefault()
        const pastedText = e.clipboardData.getData('text/plain')
        onChange(pastedText)
        setLastPasteTime(Date.now())
    }

    const characterCount = value.length
    const isValid = characterCount >= minLength

    return (
        <div className="space-y-2">
            {/* Warning Banner */}
            {showTypingWarning && (
                <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-3 flex items-start space-x-2">
                    <svg
                        className="h-5 w-5 text-orange-600 dark:text-orange-400 mt-0.5 flex-shrink-0"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                    </svg>
                    <div className="flex-1">
                        <p className="text-sm font-medium text-orange-900 dark:text-orange-200">
                            Typing is disabled
                        </p>
                        <p className="text-xs text-orange-700 dark:text-orange-300 mt-1">
                            Please paste the full blog content using Ctrl+V or right-click → Paste
                        </p>
                    </div>
                </div>
            )}

            {/* Editor */}
            <div className="relative">
                <textarea
                    value={value}
                    onChange={() => { }} // No-op: onChange only via paste
                    onKeyDown={handleKeyDown}
                    onBeforeInput={handleBeforeInput}
                    onDrop={handleDrop}
                    onPaste={handlePaste}
                    disabled={disabled}
                    placeholder={placeholder}
                    className={`w-full min-h-[400px] p-4 border-2 rounded-lg font-mono text-sm resize-y focus:outline-none focus:ring-2 focus:ring-blue-500 ${disabled
                            ? 'bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600 cursor-not-allowed'
                            : value
                                ? 'bg-white dark:bg-gray-900 border-gray-300 dark:border-gray-600'
                                : 'bg-gray-50 dark:bg-gray-900 border-dashed border-gray-400 dark:border-gray-600'
                        } text-gray-900 dark:text-gray-100`}
                    spellCheck={false}
                    autoComplete="off"
                    autoCorrect="off"
                    autoCapitalize="off"
                />

                {/* Paste Indicator */}
                {lastPasteTime && Date.now() - lastPasteTime < 2000 && (
                    <div className="absolute top-2 right-2 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 px-3 py-1 rounded-full text-xs font-medium flex items-center space-x-1">
                        <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                            <path
                                fillRule="evenodd"
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                clipRule="evenodd"
                            />
                        </svg>
                        <span>Pasted</span>
                    </div>
                )}
            </div>

            {/* Character Count */}
            <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                    <span
                        className={`font-medium ${isValid
                                ? 'text-green-600 dark:text-green-400'
                                : 'text-gray-500 dark:text-gray-400'
                            }`}
                    >
                        {characterCount.toLocaleString()} characters
                    </span>
                    {minLength > 0 && !isValid && (
                        <span className="text-gray-500 dark:text-gray-400">
                            (minimum: {minLength.toLocaleString()})
                        </span>
                    )}
                </div>

                {/* Paste Instructions */}
                {!value && (
                    <div className="text-gray-500 dark:text-gray-400 flex items-center space-x-1">
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                            />
                        </svg>
                        <span className="text-xs">Paste-only</span>
                    </div>
                )}
            </div>
        </div>
    )
}
