import Link from 'next/link'

// Mock data - replace with actual API calls
async function getBlogs() {
    // Placeholder: await fetch(`${process.env.API_URL}/blogs`)
    return [
        {
            id: '1',
            title: 'Sample Blog Post 1',
            latestVersion: 3,
            approvedVersion: 2,
            status: 'in_review',
            updatedAt: '2026-01-29T10:00:00Z',
        },
        {
            id: '2',
            title: 'Sample Blog Post 2',
            latestVersion: 1,
            approvedVersion: 1,
            status: 'approved',
            updatedAt: '2026-01-28T15:30:00Z',
        },
    ]
}

export default async function BlogsPage() {
    const blogs = await getBlogs()

    return (
        <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-6">Blogs</h1>

            <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Title
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Latest Version
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Approved Version
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Status
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Updated
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {blogs.map((blog) => (
                            <tr key={blog.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <Link
                                        href={`/dashboard/blogs/${blog.id}`}
                                        className="text-blue-600 hover:text-blue-800 font-medium"
                                    >
                                        {blog.title}
                                    </Link>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    v{blog.latestVersion}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {blog.approvedVersion ? `v${blog.approvedVersion}` : '—'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${blog.status === 'approved'
                                            ? 'bg-green-100 text-green-800'
                                            : 'bg-yellow-100 text-yellow-800'
                                        }`}>
                                        {blog.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {new Date(blog.updatedAt).toLocaleDateString()}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
