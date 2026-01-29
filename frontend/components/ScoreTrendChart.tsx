'use client'

import { useState } from 'react'

interface ScoreData {
    versionNumber: number
    score: number
    timestamp: string
}

interface ScoreTrendChartProps {
    data: ScoreData[]
    title: string
    scoreType: 'ai_likeness' | 'aeo'
}

export function ScoreTrendChart({ data, title, scoreType }: ScoreTrendChartProps) {
    // Neutral color (no green/red judgment)
    const lineColor = scoreType === 'ai_likeness' ? '#3B82F6' : '#8B5CF6' // Blue or Purple

    // Calculate chart dimensions
    const maxScore = 100
    const minScore = 0
    const chartHeight = 200
    const chartWidth = 400

    // Generate SVG path for line chart
    const generatePath = () => {
        if (data.length === 0) return ''

        const xStep = chartWidth / Math.max(data.length - 1, 1)
        const yScale = chartHeight / (maxScore - minScore)

        const points = data.map((point, index) => {
            const x = index * xStep
            const y = chartHeight - (point.score - minScore) * yScale
            return `${x},${y}`
        })

        return `M ${points.join(' L ')}`
    }

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>

            {data.length === 0 ? (
                <p className="text-gray-500 text-sm">No historical data available.</p>
            ) : (
                <div>
                    {/* Chart */}
                    <div className="mb-4">
                        <svg
                            viewBox={`0 0 ${chartWidth} ${chartHeight}`}
                            className="w-full h-48"
                            style={{ maxWidth: '100%' }}
                        >
                            {/* Grid lines */}
                            {[0, 25, 50, 75, 100].map((value) => {
                                const y = chartHeight - ((value - minScore) / (maxScore - minScore)) * chartHeight
                                return (
                                    <g key={value}>
                                        <line
                                            x1="0"
                                            y1={y}
                                            x2={chartWidth}
                                            y2={y}
                                            stroke="#E5E7EB"
                                            strokeWidth="1"
                                        />
                                        <text x="-5" y={y + 4} fontSize="10" fill="#9CA3AF" textAnchor="end">
                                            {value}
                                        </text>
                                    </g>
                                )
                            })}

                            {/* Line */}
                            <path d={generatePath()} fill="none" stroke={lineColor} strokeWidth="2" />

                            {/* Data points */}
                            {data.map((point, index) => {
                                const xStep = chartWidth / Math.max(data.length - 1, 1)
                                const yScale = chartHeight / (maxScore - minScore)
                                const x = index * xStep
                                const y = chartHeight - (point.score - minScore) * yScale

                                return (
                                    <circle key={index} cx={x} cy={y} r="4" fill={lineColor} />
                                )
                            })}
                        </svg>
                    </div>

                    {/* Legend */}
                    <div className="flex items-center justify-between text-xs text-gray-600">
                        <div>
                            {data.map((point, index) => (
                                <span key={index} className="mr-4">
                                    v{point.versionNumber}: <span className="font-medium">{point.score.toFixed(1)}</span>
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* Disclaimer */}
                    <p className="text-xs text-gray-500 mt-4 italic">
                        Note: This chart shows historical trends only. No thresholds or approval readiness is implied.
                    </p>
                </div>
            )}
        </div>
    )
}
