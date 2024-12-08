const API_BASE_URL = 'http://localhost:5000/api';

// 统一处理API请求的函数
async function fetchAPI(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    // 添加 Authorization header
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Something went wrong');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// API函数
const api = {
    // 认证相关
    auth: {
        login: (email, password) => 
            fetchAPI('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            }),

        register: (username, email, password) => 
            fetchAPI('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            })
    },

    // 文章相关
    posts: {
        getAll: () => 
            fetchAPI('/posts'),

        getOne: (id) => 
            fetchAPI(`/posts/${id}`),

        create: (title, content, tags) => 
            fetchAPI('/posts', {
                method: 'POST',
                body: JSON.stringify({ title, content, tags })
            }),

        getUserPosts: () => 
            fetchAPI('/posts/my-posts'),

        delete: (id) => 
            fetchAPI(`/posts/${id}`, {
                method: 'DELETE'
            }),
        
        update: (id, title, content, tags) =>
            fetchAPI(`/posts/${id}`, {
                method: 'PUT',
                body: JSON.stringify({ title, content, tags })
            })
    }
}; 