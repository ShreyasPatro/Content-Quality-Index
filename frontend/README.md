# Next.js 14 Dashboard - READ-ONLY Scaffold

## Overview
This is a read-only Next.js 14 dashboard scaffold using App Router. It displays blog content, versions, and evaluation scores without any mutation capabilities.

## Features
- ✅ App Router (Next.js 14)
- ✅ Server Components by default
- ✅ TypeScript
- ✅ Tailwind CSS
- ✅ Loading states (`loading.tsx`)
- ✅ Error boundaries (`error.tsx`)
- ✅ Layout-based navigation
- ✅ Mock data (replace with API calls)

## Routes
- `/dashboard` - Dashboard home
- `/dashboard/blogs` - Blogs list
- `/dashboard/blogs/[blogId]` - Blog detail with version timeline
- `/dashboard/blogs/[blogId]/versions/[versionId]` - Version detail with scores

## Constraints (READ-ONLY)
- ❌ No buttons that mutate data
- ❌ No forms
- ❌ No approval UI
- ❌ No optimistic UI
- ✅ All components are Server Components (except error boundaries)

## Getting Started

### Install Dependencies
```bash
cd frontend
npm install
```

### Run Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

### Build for Production
```bash
npm run build
npm start
```

## Project Structure
```
frontend/
├── app/
│   ├── layout.tsx                    # Root layout
│   ├── page.tsx                      # Redirect to dashboard
│   ├── globals.css                   # Global styles
│   └── dashboard/
│       ├── layout.tsx                # Dashboard layout with nav
│       ├── page.tsx                  # Dashboard home
│       ├── loading.tsx               # Loading state
│       ├── error.tsx                 # Error boundary
│       └── blogs/
│           ├── page.tsx              # Blogs list
│           ├── loading.tsx           # Loading state
│           └── [blogId]/
│               ├── page.tsx          # Blog detail
│               ├── loading.tsx       # Loading state
│               └── versions/
│                   └── [versionId]/
│                       ├── page.tsx  # Version detail
│                       └── loading.tsx
├── components/
│   ├── VersionTimeline.tsx           # Git-style timeline
│   └── ScorePanels.tsx               # Score visualization
├── lib/                              # Utility functions
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

## Next Steps
1. Replace mock data with actual API calls
2. Add authentication (NextAuth.js)
3. Add diff viewer component
4. Add rewrite history component
5. Implement approval workflow (separate routes)

## Environment Variables
Create a `.env.local` file:
```
API_URL=http://localhost:8000
```

## Notes
- All pages are Server Components (fetch data on server)
- No client-side state for approval status
- Mock data is used for demonstration
- Replace `// Placeholder:` comments with actual API calls
