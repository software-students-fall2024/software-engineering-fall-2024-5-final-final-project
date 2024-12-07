const API_BASE_URL = 'http://localhost:5000/api';

// 统一处理API请求的函数
async function fetchAPI(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    const defaultHeaders = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };

    try{
        console.log('Sending request to:', `${API_BASE_URL}${endpoint}`);
        console.log('Request options:', options);

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Something went wrong');
        }

        return response.json();
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
        getAll: (page = 1, limit = 10) => 
            fetchAPI(`/posts?page=${page}&limit=${limit}`),

        getOne: (id) => 
            fetchAPI(`/posts/${id}`),

        create: (title, content, tags) => 
            fetchAPI('/posts', {
                method: 'POST',
                body: JSON.stringify({ title, content, tags })
            }),

        getUserPosts: () => 
            fetchAPI('/posts/my-posts')
    }
}; 