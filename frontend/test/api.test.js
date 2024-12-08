const { api } = require('../js/api.js');

describe('API Functions', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn()
      },
      writable: true
    });
    jest.clearAllMocks();
  });

  describe('fetchAPI', () => {
    test('adds authorization header when token exists', async () => {
      const token = 'test-token';
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: jest.fn(() => token),
        },
        writable: true
      });

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'test' }),
      });

      await api.posts.getAll();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': `Bearer ${token}`
          })
        })
      );
    });

    test('handles API error response', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ message: 'API Error' }),
      });

      await expect(api.posts.getAll()).rejects.toThrow('API Error');
    });

    test('handles network error', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network Error'));

      await expect(api.posts.getAll()).rejects.toThrow('Network Error');
    });

    test('handles network error with custom message', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Failed to fetch'));
      
      await expect(api.posts.getAll()).rejects.toThrow('Failed to fetch');
    });

    test('handles empty response', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: null })
      });

      const result = await api.posts.getAll();
      expect(result.data).toBeNull();
    });

    test('handles missing token', async () => {
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: jest.fn(() => null)
        },
        writable: true
      });

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'test' })
      });

      await api.posts.getAll();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.not.objectContaining({
          headers: expect.objectContaining({
            'Authorization': expect.any(String)
          })
        })
      );
    });
  });

  describe('posts API', () => {
    test('creates a new post', async () => {
      const mockPost = {
        title: 'Test Post',
        content: 'Test Content',
        tags: ['test']
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockPost }),
      });

      const result = await api.posts.create(
        mockPost.title,
        mockPost.content,
        mockPost.tags
      );

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/posts'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(mockPost)
        })
      );
      expect(result.data).toEqual(mockPost);
    });

    test('gets a single post', async () => {
      const mockPost = {
        id: '123',
        title: 'Test Post'
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockPost }),
      });

      const result = await api.posts.getOne('123');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/posts/123'),
        expect.any(Object)
      );
      expect(result.data).toEqual(mockPost);
    });

    test('updates a post', async () => {
      const mockUpdate = {
        title: 'Updated Title',
        content: 'Updated Content',
        tags: ['updated']
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockUpdate }),
      });

      await api.posts.update(
        '123',
        mockUpdate.title,
        mockUpdate.content,
        mockUpdate.tags
      );

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/posts/123'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(mockUpdate)
        })
      );
    });

    test('deletes a post', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Post deleted' }),
      });

      await api.posts.delete('123');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/posts/123'),
        expect.objectContaining({
          method: 'DELETE'
        })
      );
    });
  });

  describe('auth API', () => {
    test('registers a new user', async () => {
      const mockUser = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123'
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockUser }),
      });

      const result = await api.auth.register(
        mockUser.username,
        mockUser.email,
        mockUser.password
      );

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/register'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(mockUser)
        })
      );
      expect(result.data).toEqual(mockUser);
    });
  });

  describe('comments API', () => {
    test('creates a new comment', async () => {
      const mockComment = {
        content: 'Test comment'
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: mockComment }),
      });

      await api.posts.comment('123', mockComment.content);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/posts/123'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ content: mockComment.content })
        })
      );
    });
  });
});
