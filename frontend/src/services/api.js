import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

// Request interceptor to add token if it exists
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle common errors like 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token might be expired or invalid
      localStorage.removeItem('token');
      // Redirect to login only if not already on login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: (email, password) => {
    // The FastAPI backend expects { email, password } as JSON, not FormData
    return api.post('/auth/login', {
      email: email,
      password: password
    });
  },
  register: (data) => api.post('/users/', data),
  getMe: () => api.get('/users/me'),
};

export const postService = {
  getPosts: (page = 1, pageSize = 10) => api.get(`/posts/?page=${page}&page_size=${pageSize}`),
  getPost: (id) => api.get(`/posts/${id}`),
  createPost: (data) => api.post('/posts/', data),
  updatePost: (id, data) => api.patch(`/posts/${id}`, data),
  deletePost: (id) => api.delete(`/posts/${id}`),
};

export const commentService = {
  getComments: (postId, page = 1, pageSize = 10) => api.get(`/comments/?post_id=${postId}&page=${page}&page_size=${pageSize}`),
  createComment: (data) => api.post('/comments/', data),
  updateComment: (id, data) => api.patch(`/comments/${id}`, data),
  deleteComment: (id) => api.delete(`/comments/${id}`),
};

export default api;
