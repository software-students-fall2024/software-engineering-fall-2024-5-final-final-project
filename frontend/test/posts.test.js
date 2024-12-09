import { jest } from '@jest/globals';

// Mock the api module
const mockApi = {
    posts: {
        getAll: jest.fn(),
        getOne: jest.fn(),
        create: jest.fn(),
        update: jest.fn(),
        delete: jest.fn(),
        comment: jest.fn()
    }
};


// Mock global api variable
global.api = mockApi;

// Mock DOM elements
document.body.innerHTML = `
    <div id="posts-container"></div>
    <div id="post-detail"></div>
    <div id="comments-list"></div>
    <textarea id="comment-content"></textarea>
    <div id="error-message"></div>
`;

// Mock window.location
const mockLocation = {
    href: '',
    search: '?id=123'
};
Object.defineProperty(window, 'location', {
    value: mockLocation,
    writable: true
});

// Mock showError function
global.showError = jest.fn();

// Import the functions after setting up mocks
import {
    loadPosts,
    loadPostDetail,
    editPost,
    deletePost,
    addComment
} from '../js/posts';

describe('Posts Module', () => {
    beforeEach(() => {
        // Clear all mocks before each test
        jest.clearAllMocks();
        mockLocation.href = '';
        document.getElementById('posts-container').innerHTML = '';
        document.getElementById('post-detail').innerHTML = '';
        document.getElementById('comments-list').innerHTML = '';
        document.getElementById('comment-content').value = '';
    });

    describe('loadPosts', () => {
        it('should load and display posts successfully', async () => {
            const mockPosts = {
                data: [{
                    _id: '1',
                    title: 'Test Post',
                    content: 'Test Content',
                    tags: ['test'],
                    created_at: '2024-03-15'
                }]
            };
            mockApi.posts.getAll.mockResolvedValue(mockPosts);

            await loadPosts();

            expect(mockApi.posts.getAll).toHaveBeenCalled();
            expect(document.getElementById('posts-container').innerHTML)
                .toContain('Test Post');
        });

        it('should handle errors when loading posts', async () => {
            mockApi.posts.getAll.mockRejectedValue(new Error('Failed to load posts'));

            await loadPosts();

            expect(showError).toHaveBeenCalledWith('Failed to load posts');
        });
    });



    describe('loadPostDetail', () => {
        it('should load and display post detail successfully', async () => {
            const mockPost = {
                data: {
                    _id: '123',
                    title: 'Test Post',
                    content: 'Test Content',
                    author_username: 'testuser',
                    tags: ['test'],
                    created_at: '2024-03-15',
                    comments: []
                }
            };
            mockApi.posts.getOne.mockResolvedValue(mockPost);

            await loadPostDetail();

            expect(mockApi.posts.getOne).toHaveBeenCalledWith('123');
            expect(document.getElementById('post-detail').innerHTML)
                .toContain('Test Post');
        });

        it('should handle missing post ID', async () => {
            mockLocation.search = '';
            
            await loadPostDetail();

            expect(showError).toHaveBeenCalledWith('Post ID not found');
            expect(mockApi.posts.getOne).not.toHaveBeenCalled();
        });
    });

    describe('addComment', () => {
        it('should add comment successfully', async () => {
            const mockPost = {
                data: {
                    _id: '123',
                    comments: [{
                        author_username: 'user1',
                        content: 'New comment',
                        created_at: '2024-03-15'
                    }]
                }
            };
            
            document.getElementById('comment-content').value = 'New comment';
            mockApi.posts.comment.mockResolvedValue({});
            mockApi.posts.getOne.mockResolvedValue(mockPost);

            await addComment('123');

            expect(mockApi.posts.comment).toHaveBeenCalledWith('123', 'New comment');
            expect(document.getElementById('comment-content').value).toBe('');
            expect(document.getElementById('comments-list').innerHTML)
                .toContain('New comment');
        });

        it('should handle empty comment content', async () => {
            document.getElementById('comment-content').value = '';

            await addComment('123');

            expect(showError).toHaveBeenCalledWith('Comment cannot be empty');
            expect(mockApi.posts.comment).not.toHaveBeenCalled();
        });
    });

    describe('editPost', () => {
        it('should redirect to edit page', () => {
            editPost('123');
            expect(mockLocation.href).toBe('./edit-post.html?id=123');
        });
    });



    describe('deletePost', () => {
        it('should delete post and redirect', async () => {
            mockApi.posts.delete.mockResolvedValue({});
            global.confirm = jest.fn(() => true);

            await deletePost('123');

            expect(mockApi.posts.delete).toHaveBeenCalledWith('123');
            expect(mockLocation.href).toBe('../index.html');
        });

        it('should not delete when user cancels', async () => {
            global.confirm = jest.fn(() => false);

            await deletePost('123');

            expect(mockApi.posts.delete).not.toHaveBeenCalled();
        });
    });
});
