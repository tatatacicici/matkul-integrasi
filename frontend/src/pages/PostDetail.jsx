import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, User, MessageCircle, Send, Trash2, Edit2, X, Check } from 'lucide-react';
import { postService, commentService } from '../services/api';
import { useAuth } from '../context/AuthContext';

const PostDetail = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [commentText, setCommentText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [editingCommentId, setEditingCommentId] = useState(null);
  const [editingCommentText, setEditingCommentText] = useState('');

  useEffect(() => { fetchPost(); }, [id]);

  const fetchPost = async () => {
    setLoading(true);
    try {
      const response = await postService.getPost(id);
      setPost(response.data);
    } catch (error) {
      console.error('Failed to fetch post:', error);
    } finally { setLoading(false); }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    setSubmitting(true);
    try {
      await commentService.createComment({ comment: commentText, post_id: parseInt(id) });
      setCommentText('');
      fetchPost();
    } catch (error) {
      alert('Failed to add comment. Make sure you are logged in.');
    } finally { setSubmitting(false); }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm('Delete this comment?')) return;
    try { await commentService.deleteComment(commentId); fetchPost(); }
    catch { alert('Failed to delete. You can only delete your own comments.'); }
  };

  const handleEditComment = async (commentId) => {
    if (!editingCommentText.trim()) return;
    try {
      await commentService.updateComment(commentId, { comment: editingCommentText });
      setEditingCommentId(null); setEditingCommentText(''); fetchPost();
    } catch { alert('Failed to edit comment.'); }
  };

  if (loading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600"></div>
    </div>
  );

  if (!post) return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Post Not Found</h2>
      <Link to="/" className="text-blue-600 hover:text-blue-700 font-medium">← Back to Blog</Link>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <Link to="/" className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors font-medium text-sm">
              <ArrowLeft size={18} /> Back to Blog
            </Link>
          </div>
        </div>
      </nav>

      <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <header className="mb-10">
          <div className="flex items-center gap-3 text-sm text-gray-500 mb-4">
            <div className="flex items-center gap-1.5 bg-gray-100 px-3 py-1 rounded-full">
              <User size={14} /><span>{post.author?.full_name || 'Anonymous'}</span>
            </div>
            <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${post.status === 'published' ? 'bg-green-50 text-green-700 ring-1 ring-green-600/20' : 'bg-gray-50 text-gray-600 ring-1 ring-gray-500/10'}`}>{post.status}</span>
          </div>
          <h1 id="post-title" className="text-4xl md:text-5xl font-extrabold text-gray-900 tracking-tight leading-tight">{post.title}</h1>
        </header>

        <div id="post-content" className="prose prose-lg max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">{post.content}</div>

        <section className="mt-16 border-t border-gray-200 pt-10">
          <h2 id="comments-heading" className="text-2xl font-bold text-gray-900 flex items-center gap-2 mb-8">
            <MessageCircle size={24} /> Comments ({post.comments?.length || 0})
          </h2>

          {user ? (
            <form id="comment-form" onSubmit={handleAddComment} className="mb-8 bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-500 text-white flex items-center justify-center text-sm font-semibold flex-shrink-0">
                  {user.full_name?.[0]?.toUpperCase() || 'U'}
                </div>
                <div className="flex-1">
                  <textarea id="comment-input" value={commentText} onChange={(e) => setCommentText(e.target.value)}
                    placeholder="Write a comment..." className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none text-sm min-h-[80px]"
                    required maxLength={250} />
                  <div className="flex justify-between items-center mt-3">
                    <span className="text-xs text-gray-400">{commentText.length}/250</span>
                    <button id="comment-submit" type="submit" disabled={submitting || !commentText.trim()}
                      className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all">
                      <Send size={14} /> {submitting ? 'Posting...' : 'Post Comment'}
                    </button>
                  </div>
                </div>
              </div>
            </form>
          ) : (
            <div className="mb-8 bg-gray-50 rounded-2xl border border-gray-100 p-6 text-center">
              <p className="text-gray-500 text-sm"><Link to="/login" className="text-blue-600 font-medium">Sign in</Link> to leave a comment.</p>
            </div>
          )}

          <div id="comments-list" className="space-y-4">
            {post.comments?.length === 0 ? (
              <p className="text-gray-400 text-center py-8 text-sm">No comments yet. Be the first!</p>
            ) : (
              post.comments?.map((c) => (
                <div key={c.id} className="bg-white rounded-xl border border-gray-100 p-5 shadow-sm hover:shadow-md transition-shadow" data-comment-id={c.id}>
                  <div className="flex items-start gap-3">
                    <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-400 to-purple-400 text-white flex items-center justify-center text-xs font-semibold flex-shrink-0">
                      {c.author?.full_name?.[0]?.toUpperCase() || '?'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-gray-900 text-sm">{c.author?.full_name || 'Anonymous'}</span>
                        {user && c.author?.id === user.id && (
                          <div className="flex items-center gap-1">
                            {editingCommentId === c.id ? (
                              <>
                                <button onClick={() => handleEditComment(c.id)} className="p-1 text-green-500 hover:text-green-600"><Check size={14} /></button>
                                <button onClick={() => { setEditingCommentId(null); setEditingCommentText(''); }} className="p-1 text-gray-400 hover:text-gray-600"><X size={14} /></button>
                              </>
                            ) : (
                              <>
                                <button onClick={() => { setEditingCommentId(c.id); setEditingCommentText(c.comment); }} className="p-1 text-gray-400 hover:text-blue-600"><Edit2 size={14} /></button>
                                <button onClick={() => handleDeleteComment(c.id)} className="p-1 text-gray-400 hover:text-red-600"><Trash2 size={14} /></button>
                              </>
                            )}
                          </div>
                        )}
                      </div>
                      {editingCommentId === c.id ? (
                        <textarea value={editingCommentText} onChange={(e) => setEditingCommentText(e.target.value)}
                          className="mt-2 w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" maxLength={250} />
                      ) : (
                        <p className="mt-1 text-gray-600 text-sm leading-relaxed">{c.comment}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </article>

      <footer className="bg-white border-t border-gray-200 mt-12 py-12">
        <div className="max-w-4xl mx-auto px-4 text-center text-gray-500 text-sm">
          &copy; {new Date().getFullYear()} IntegrasiBlog. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

export default PostDetail;
