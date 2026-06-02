import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BookOpen, User, ArrowRight, LogOut } from 'lucide-react';
import { postService } from '../services/api';
import { useAuth } from '../context/AuthContext';

const PublicBlog = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      // Fetch public posts (no auth required based on backend router)
      const response = await postService.getPosts(1, 20);
      // Only show published posts on the public blog
      const publishedPosts = response.data.data.filter(p => p.status === 'published');
      setPosts(publishedPosts);
    } catch (error) {
      console.error("Failed to fetch public posts:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Navbar */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <BookOpen className="text-blue-600" size={28} />
              <span className="font-bold text-xl tracking-tight text-gray-900">IntegrasiBlog.</span>
            </div>
            <div className="flex items-center">
              {!user ? (
                <Link 
                  to="/login" 
                  className="text-sm font-medium text-gray-700 hover:text-blue-600 mr-4 transition-colors"
                >
                  Sign In
                </Link>
              ) : (
                <button 
                  onClick={handleLogout}
                  className="flex items-center gap-1 text-sm font-medium text-red-600 hover:text-red-700 mr-4 transition-colors"
                >
                  <LogOut size={16} /> Logout
                </button>
              )}
              <Link 
                to="/dashboard"
                className="bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-blue-700 transition-all shadow-sm hover:shadow"
              >
                Dashboard
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 tracking-tight mb-4">
            Insights and <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Stories</span>
          </h1>
          <p className="text-lg text-gray-500 max-w-2xl mx-auto">
            Discover the latest articles, tutorials, and updates from our community of writers and developers.
          </p>
        </div>
      </div>

      {/* Blog Feed */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-end mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Latest Articles</h2>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="animate-pulse bg-white p-6 rounded-2xl border border-gray-100">
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-20 bg-gray-200 rounded w-full mb-4"></div>
              </div>
            ))}
          </div>
        ) : posts.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-3xl border border-gray-100">
            <BookOpen className="mx-auto h-12 w-12 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900">No articles yet</h3>
            <p className="text-gray-500 mt-1">Check back later for new content.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {posts.map((post) => (
              <article 
                key={post.id} 
                className="bg-white rounded-3xl border border-gray-100 overflow-hidden hover:shadow-xl transition-shadow duration-300 flex flex-col h-full group"
              >
                <div className="p-8 flex flex-col flex-1">
                  <div className="flex items-center gap-4 text-xs font-medium text-gray-500 mb-4">
                    <div className="flex items-center gap-1.5 bg-gray-50 px-2.5 py-1 rounded-full">
                      <User size={14} />
                      <span>{post.author?.full_name || 'Anonymous'}</span>
                    </div>
                  </div>
                  
                  <h3 className="text-2xl font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors line-clamp-2">
                    {post.title}
                  </h3>
                  
                  <p className="text-gray-600 mb-6 line-clamp-3 leading-relaxed flex-1">
                    {post.content}
                  </p>
                  
                  <div className="mt-auto pt-6 border-t border-gray-100 flex items-center justify-between">
                    <Link to={`/post/${post.id}`} className="text-blue-600 font-semibold text-sm flex items-center gap-1 group-hover:gap-2 transition-all">
                      Read more <ArrowRight size={16} />
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12 py-12">
        <div className="max-w-5xl mx-auto px-4 text-center text-gray-500 text-sm">
          &copy; {new Date().getFullYear()} IntegrasiBlog. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

export default PublicBlog;
