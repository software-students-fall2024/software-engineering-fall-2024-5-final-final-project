const posts = require('../js/posts.js');
const auth = require('../js/auth.js');

describe('Posts Functions', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="posts-container"></div>
      <div id="error-message"></div>
    `;
    global.api = {
      posts: {
        getAll: jest.fn(),
        create: jest.fn(),
        update: jest.fn(),
        delete: jest.fn()
      }
    };
    global.showError = auth.showError;
    
    // 修改 window.location 模拟方式
    delete window.location;
    window.location = {
      href: '',
      assign: jest.fn(),
      replace: jest.fn()
    };
    
    jest.clearAllMocks();
  });

  describe('loadPosts', () => {
    test('successfully loads and displays posts', async () => {
      const mockPosts = [
        { 
          _id: '1', 
          title: 'Post 1', 
          content: 'Content 1',
          tags: ['tag1'],
          created_at: new Date().toISOString()
        },
        { 
          _id: '2', 
          title: 'Post 2', 
          content: 'Content 2',
          tags: ['tag2'],
          created_at: new Date().toISOString()
        }
      ];

      global.api.posts.getAll.mockResolvedValue({ data: mockPosts });

      await posts.loadPosts();

      const container = document.getElementById('posts-container');
      expect(container.innerHTML).toContain('Post 1');
      expect(container.innerHTML).toContain('Post 2');
    });

    test('handles error when loading posts', async () => {
      const mockError = new Error('Failed to load posts');
      global.api.posts.getAll.mockRejectedValue(mockError);

      await posts.loadPosts();

      const errorDiv = document.getElementById('error-message');
      expect(errorDiv.textContent).toBe('Failed to load posts');
    });
  });

  describe('createPost', () => {
    test('successfully creates a new post', async () => {
      const mockPost = {
        title: 'New Post',
        content: 'New Content',
        tags: ['test']
      };

      global.api.posts.create.mockResolvedValue({ data: mockPost });

      const mockEvent = {
        preventDefault: jest.fn()
      };

      document.body.innerHTML += `
        <form id="post-form">
          <input id="title" value="New Post" />
          <textarea id="content">New Content</textarea>
          <input id="tags" value="test" />
        </form>
      `;

      await posts.createPost(mockEvent);

      expect(mockEvent.preventDefault).toHaveBeenCalled();
      expect(global.api.posts.create).toHaveBeenCalledWith(
        'New Post',
        'New Content',
        ['test']
      );
      // 验证 href 的设置而不是 assign 方法的调用
      expect(window.location.href).toBe('/index.html');
    });
  });
});
