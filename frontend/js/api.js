const API_BASE_URL = 'http://localhost:5000/api';

// 统一处理API请求的函数
async function fetchAPI(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    // 添加 Authorization header
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers
    };

    const config = {
        ...options,
        headers,
        mode: 'cors',
        credentials: 'include'
    };

    console.log('Fetch Config:', {
        url: `${API_BASE_URL}${endpoint}`,
        ...config
    });

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        
        console.log('Response status:', response.status);
        console.log('Response headers:', [...response.headers.entries()]);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({
                message: `HTTP error! status: ${response.status}`
            }));
            throw new Error(errorData.message);
        }

        const data = await response.json();
        console.log('Response data:', data);
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