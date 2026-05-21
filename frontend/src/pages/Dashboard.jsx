import { useState, useEffect } from 'react';
import { FileText, Plus, Edit2, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { postService } from '../services/api';
import Layout from '../components/Layout';

function Dashboard() {
  const { user } = useAuth();
  
  const [posts, setPosts] = useState([]);
  const [loadingPosts, setLoadingPosts] = useState(true);
  const [meta, setMeta] = useState(null);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    setLoadingPosts(true);
    try {
      const response = await postService.getPosts(1, 5); // Fetch latest 5 posts
      setPosts(response.data.data);
      setMeta(response.data.meta);
    } catch (error) {
      console.error("Failed to fetch posts:", error);
    } finally {
      setLoadingPosts(false);
    }
  };

  const getStatusColor = (status) => {
    switch(status?.toLowerCase()) {
      case 'published': return 'text-green-700 bg-green-50 ring-green-600/20';
      case 'draft': return 'text-gray-600 bg-gray-50 ring-gray-500/10';
      default: return 'text-blue-700 bg-blue-50 ring-blue-600/20';
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-end">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Welcome back, {user?.full_name || 'User'}</h2>
            <p className="text-gray-500 mt-1">Here is the overview of your API project.</p>
          </div>
          <button className="hidden sm:flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors shadow-sm">
            <Plus size={18} /> New Post
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { title: 'Total Posts', value: meta?.total || '-', trend: '0%', color: 'blue' },
            { title: 'Pages', value: meta?.total_pages || '-', trend: '0%', color: 'indigo' },
            { title: 'Current Page', value: meta?.page || '-', trend: '0%', color: 'green' },
          ].map((stat, i) => (
            <div key={i} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
              <h3 className="text-gray-500 text-sm font-medium">{stat.title}</h3>
              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-3xl font-bold text-gray-900">{stat.value}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Data Table Area */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden mt-8">
          <div className="px-6 py-5 border-b border-gray-100 flex justify-between items-center">
            <h3 className="font-semibold text-gray-900">Recent Posts</h3>
            <button className="text-sm text-blue-600 font-medium hover:text-blue-700">View All</button>
          </div>
          
          {loadingPosts ? (
            <div className="p-12 flex justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : posts.length === 0 ? (
            <div className="p-6 flex flex-col items-center justify-center text-center text-gray-500 min-h-[300px]">
              <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
                <FileText className="text-gray-400" size={32} />
              </div>
              <p className="font-medium text-gray-900 mb-1">No posts found</p>
              <p className="text-sm">Create a new post to see it here.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-gray-500 bg-gray-50 uppercase border-b border-gray-100">
                  <tr>
                    <th className="px-6 py-4 font-medium">Title</th>
                    <th className="px-6 py-4 font-medium">Author</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {posts.map((post) => (
                    <tr key={post.id} className="hover:bg-gray-50/50 transition-colors">
                      <td className="px-6 py-4 font-medium text-gray-900">
                        {post.title}
                      </td>
                      <td className="px-6 py-4 text-gray-500">
                        {post.author?.full_name || 'Unknown'}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${getStatusColor(post.status)}`}>
                          {post.status || 'Draft'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex justify-end gap-2">
                          <button className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors" title="Edit">
                            <Edit2 size={16} />
                          </button>
                          <button className="p-1.5 text-gray-400 hover:text-red-600 transition-colors" title="Delete">
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

export default Dashboard;
