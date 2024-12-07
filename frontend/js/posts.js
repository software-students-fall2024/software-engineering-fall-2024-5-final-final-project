// 加载文章列表
async function loadPosts() {
    try {
        const response = await api.posts.getAll();
        const postsContainer = document.getElementById('posts-container');
        postsContainer.innerHTML = response.data.map(post => `
            <div class="post-card">
                <h2>${post.title}</h2>
                <p>${post.content.substring(0, 200)}...</p>
                <div class="post-meta">
                    <span class="tags">${post.tags.join(', ')}</span>
                    <span class="date">${new Date(post.created_at).toLocaleDateString()}</span>
                </div>
                <a href="/pages/post-detail.html?id=${post._id}" class="read-more">Read More</a>
            </div>
        `).join('');
    } catch (error) {
        showError(error.message);
    }
}

// 加载单篇文章详情
async function loadPostDetail() {
    const urlParams = new URLSearchParams(window.location.search);
    const postId = urlParams.get('id');

    try {
        const response = await api.posts.getOne(postId);
        const post = response.data;
        document.getElementById('post-detail').innerHTML = `
            <h1>${post.title}</h1>
            <div class="post-meta">
                <span class="tags">${post.tags.join(', ')}</span>
                <span class="date">${new Date(post.created_at).toLocaleDateString()}</span>
            </div>
            <div class="post-content">${post.content}</div>
        `;
    } catch (error) {
        showError(error.message);
    }
}

// 创建新文章
async function createPost(event) {
    event.preventDefault();
    const title = document.getElementById('title').value;
    const content = document.getElementById('content').value;
    const tags = document.getElementById('tags').value.split(',').map(tag => tag.trim());

    try {
        await api.posts.create(title, content, tags);
        window.location.href = '/index.html';
    } catch (error) {
        showError(error.message);
    }
} 