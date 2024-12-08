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
                <a href="./pages/post-detail.html?id=${post._id}" class="read-more">Read More</a>
            </div>
        `).join('');
    } catch (error) {
        showError(error.message);
    }
}

async function loadPostDetail() {
    const urlParams = new URLSearchParams(window.location.search);
    const postId = urlParams.get('id');
    
    console.log('Post ID:', postId);

    if (!postId) {
        showError('Post ID not found');
        return;
    }

    try {
        const response = await api.posts.getOne(postId);
        const post = response.data;
        console.log('Post data:', post);
        
        document.getElementById('post-detail').innerHTML = `
            <h1 class="post-title">${post.title}</h1>
            <div class="post-meta">
                <span class="tags">Tags: ${post.tags.join(', ')}</span>
                <span class="date">Published: ${new Date(post.created_at).toLocaleDateString()}</span>
            </div>
            <div class="post-content">${post.content}</div>
            <div class="post-actions">
                <button class="edit-btn" onclick="editPost('${post._id}')">Edit Post</button>
                <button class="delete-btn" onclick="deletePost('${post._id}')">Delete Post</button>
            </div>
            <a href="../index.html" class="back-button">Back to Posts</a>
        `;
    } catch (error) {
        console.error('Error loading post:', error);
        showError(error.message);
    }
}

function editPost(postId) {
    window.location.href = `./edit-post.html?id=${postId}`;
}

async function deletePost(postId) {
    if (!confirm('Are you sure you want to delete this post?')) {
        return;
    }

    try {
        await api.posts.delete(postId);
        alert('Post deleted successfully');
        window.location.href = '../index.html';
    } catch (error) {
        console.error('Error deleting post:', error);
        showError(error.message);
    }
}

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