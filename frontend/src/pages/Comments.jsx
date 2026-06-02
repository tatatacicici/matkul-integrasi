import React, { useState, useEffect } from 'react';
import { MessageSquare, Edit2, Trash2, X, Check } from 'lucide-react';
import Layout from '../components/Layout';
import { commentService } from '../services/api';
import { useAuth } from '../context/AuthContext';

const Comments = () => {
  const { user } = useAuth();
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');

  useEffect(() => { fetchComments(); }, []);

  const fetchComments = async () => {
    setLoading(true);
    try {
      const response = await commentService.getComments(null, 1, 50);
      setComments(response.data.data);
    } catch (error) {
      console.error('Failed to fetch comments:', error);
    } finally { setLoading(false); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this comment?')) return;
    try { await commentService.deleteComment(id); fetchComments(); }
    catch { alert('Failed to delete. You can only delete your own comments.'); }
  };

  const handleEdit = async (id) => {
    if (!editText.trim()) return;
    try {
      await commentService.updateComment(id, { comment: editText });
      setEditingId(null); setEditText(''); fetchComments();
    } catch { alert('Failed to edit comment.'); }
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 id="comments-page-heading" className="text-2xl font-bold text-gray-900">Manage Comments</h2>
          <p className="text-gray-500 mt-1">View and manage all comments across posts.</p>
        </div>

        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 flex justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : comments.length === 0 ? (
            <div className="p-6 flex flex-col items-center justify-center text-center text-gray-500 min-h-[300px]">
              <div className="w-16 h-16 bg-gray-50 rounded-full flex items-center justify-center mb-4">
                <MessageSquare className="text-gray-400" size={32} />
              </div>
              <p className="font-medium text-gray-900 mb-1">No comments found</p>
              <p className="text-sm">Comments will appear here when users comment on posts.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table id="comments-table" className="w-full text-sm text-left">
                <thead className="text-xs text-gray-500 bg-gray-50 uppercase border-b border-gray-100">
                  <tr>
                    <th className="px-6 py-4 font-medium">Comment</th>
                    <th className="px-6 py-4 font-medium">Author</th>
                    <th className="px-6 py-4 font-medium">Post ID</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {comments.map((c) => (
                    <tr key={c.id} className="hover:bg-gray-50/50 transition-colors" data-comment-id={c.id}>
                      <td className="px-6 py-4 text-gray-900 max-w-xs">
                        {editingId === c.id ? (
                          <textarea value={editText} onChange={(e) => setEditText(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none" maxLength={250} />
                        ) : (
                          <span className="line-clamp-2">{c.comment}</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-gray-500">{c.author?.full_name || 'Unknown'}</td>
                      <td className="px-6 py-4 text-gray-500">#{c.post_id}</td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex justify-end gap-2">
                          {editingId === c.id ? (
                            <>
                              <button onClick={() => handleEdit(c.id)} className="p-1.5 text-green-500 hover:text-green-600" title="Save"><Check size={16} /></button>
                              <button onClick={() => { setEditingId(null); setEditText(''); }} className="p-1.5 text-gray-400 hover:text-gray-600" title="Cancel"><X size={16} /></button>
                            </>
                          ) : (
                            <>
                              <button onClick={() => { setEditingId(c.id); setEditText(c.comment); }} className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors" title="Edit"><Edit2 size={16} /></button>
                              <button onClick={() => handleDelete(c.id)} className="p-1.5 text-gray-400 hover:text-red-600 transition-colors" title="Delete"><Trash2 size={16} /></button>
                            </>
                          )}
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
};

export default Comments;
