/** @type {import('next').NextConfig} */
const nextConfig = {
    experimental: {
        serverActions: {
            allowedOrigins: [],
        },
    },
    env: {
        API_URL: process.env.API_URL || 'http://localhost:8000',
    },
}

module.exports = nextConfig
