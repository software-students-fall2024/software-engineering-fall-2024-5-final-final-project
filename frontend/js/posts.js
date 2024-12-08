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
        <a href="../index.html" class="back-button">Back to Posts</a>
            <div class="post-header">
                <h3 class="post-title">${post.title}</h3>
                <h4 class="author">By ${post.author_username}</h4>
            </div>
            <div class="post-meta">
                <span class="tags">Tags: ${post.tags.join(', ')}</span>
                <span class="date">Published: ${new Date(post.created_at).toLocaleDateString()}</span>
            </div>
            <div class="post-content">${post.content}</div>
            <div class="post-actions">
                <button class="edit-btn" onclick="editPost('${post._id}')">Edit Post</button>
                <button class="delete-btn" onclick="deletePost('${post._id}')">Delete Post</button>
            </div>
            <div class="comments">
                <h5>Comments</h5>
                <div class="comment-form">
                    <textarea id="comment-content" placeholder="Write a comment..."></textarea>
                    <button onclick="addComment('${post._id}')" class="comment-btn">Submit Comment</button>
                </div>
                <div id="comments-list" class="comments-list">
                    ${renderComments(post.comments)}
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading post:', error);
        showError(error.message);
    }
}

function renderComments(comments) {
    if (!comments || comments.length === 0) {
        return '<p>No comments yet</p>';
    }
    
    return comments.map(comment => `
        <div class="comment">
            <div class="comment-header">
                <strong class="comment-author">${comment.author_username || 'Anonymous'}</strong>
                <small class="comment-date">Posted on ${new Date(comment.created_at).toLocaleDateString()}</small>
            </div>
            <p class="comment-content">${comment.content}</p>
        </div>
    `).join('');
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

async function addComment(postId) {
    const contentElement = document.getElementById('comment-content');
    const content = contentElement.value;
    
    if (!content.trim()) {
        showError('Comment cannot be empty');
        return;
    }

    try {
        await api.posts.comment(postId, content);
        
        contentElement.value = '';
        
        const response = await api.posts.getOne(postId);
        const post = response.data;
        
        const commentsListElement = document.getElementById('comments-list');
        commentsListElement.innerHTML = renderComments(post.comments);
        
    } catch (error) {
        showError(error.message);
    }
}
