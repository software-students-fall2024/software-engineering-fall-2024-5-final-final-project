const auth = require('../js/auth.js');

describe('Auth Functions', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="error-message" class="error-message"></div>
    `;
    // 重置所有模拟
    jest.clearAllMocks();
  });

  describe('showError', () => {
    test('displays error message', () => {
      const message = 'Test error message';
      auth.showError(message);
      
      const errorDiv = document.getElementById('error-message');
      expect(errorDiv.textContent).toBe(message);
      expect(errorDiv.style.display).toBe('block');
    });
  });

  describe('checkAuth', () => {
    test('redirects to login page when no token exists', () => {
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: jest.fn(() => null),
        },
        writable: true
      });

      const mockLocation = { href: '' };
      Object.defineProperty(window, 'location', {
        value: mockLocation,
        writable: true
      });

      auth.checkAuth();
      expect(window.location.href).toBe('./pages/login.html');
    });

    test('does not redirect when token exists', () => {
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: jest.fn(() => 'valid-token'),
        },
        writable: true
      });

      const mockLocation = { href: '/index.html' };
      Object.defineProperty(window, 'location', {
        value: mockLocation,
        writable: true
      });

      auth.checkAuth();
      expect(window.location.href).toBe('/index.html');
    });
  });

  describe('handleLogin', () => {
    test('successful login saves token and redirects', async () => {
      const mockEvent = {
        preventDefault: jest.fn()
      };

      document.body.innerHTML = `
        <div id="error-message" class="error-message"></div>
        <input id="email" value="test@example.com" />
        <input id="password" value="password123" />
      `;

      const mockResponse = {
        data: {
          access_token: 'test-token',
          user: { id: 1, username: 'testuser' }
        }
      };

      global.api = {
        auth: {
          login: jest.fn().mockResolvedValue(mockResponse)
        }
      };

      Object.defineProperty(window, 'localStorage', {
        value: {
          setItem: jest.fn(),
        },
        writable: true
      });

      const mockLocation = { href: '' };
      Object.defineProperty(window, 'location', {
        value: mockLocation,
        writable: true
      });

      await auth.handleLogin(mockEvent);

      expect(mockEvent.preventDefault).toHaveBeenCalled();
      expect(localStorage.setItem).toHaveBeenCalledWith('token', 'test-token');
      expect(localStorage.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockResponse.data.user));
      expect(window.location.href).toBe('/index.html');
    });

    test('handles login error', async () => {
      const mockEvent = {
        preventDefault: jest.fn()
      };

      document.body.innerHTML = `
        <div id="error-message" class="error-message"></div>
        <input id="email" value="test@example.com" />
        <input id="password" value="wrong-password" />
      `;

      const mockError = new Error('Invalid credentials');
      global.api = {
        auth: {
          login: jest.fn().mockRejectedValue(mockError)
        }
      };

      await auth.handleLogin(mockEvent);

      expect(mockEvent.preventDefault).toHaveBeenCalled();
      const errorDiv = document.getElementById('error-message');
      expect(errorDiv.textContent).toBe('Invalid credentials');
      expect(errorDiv.style.display).toBe('block');
    });
  });

  describe('logout', () => {
    test('clears localStorage and redirects to login page', () => {
      Object.defineProperty(window, 'localStorage', {
        value: {
          removeItem: jest.fn(),
        },
        writable: true
      });

      const mockLocation = { href: '' };
      Object.defineProperty(window, 'location', {
        value: mockLocation,
        writable: true
      });

      auth.logout();

      expect(localStorage.removeItem).toHaveBeenCalledWith('token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('user');
      expect(window.location.href).toBe('./pages/login.html');
    });
  });

  describe('handleRegister', () => {
    test('successful registration redirects to login page', async () => {
      const mockEvent = {
        preventDefault: jest.fn()
      };

      document.body.innerHTML = `
        <div id="error-message" class="error-message"></div>
        <input id="username" value="testuser" />
        <input id="email" value="test@example.com" />
        <input id="password" value="password123" />
      `;

      const mockResponse = {
        message: 'Registration successful'
      };

      global.api = {
        auth: {
          register: jest.fn().mockResolvedValue(mockResponse)
        }
      };

      const mockLocation = { href: '' };
      Object.defineProperty(window, 'location', {
        value: mockLocation,
        writable: true
      });

      await auth.handleRegister(mockEvent);

      expect(mockEvent.preventDefault).toHaveBeenCalled();
      expect(window.location.href).toBe('./login.html');
    });

    test('handles registration error', async () => {
      const mockEvent = {
        preventDefault: jest.fn()
      };

      document.body.innerHTML = `
        <div id="error-message" class="error-message"></div>
        <input id="username" value="testuser" />
        <input id="email" value="test@example.com" />
        <input id="password" value="password123" />
      `;

      const mockError = new Error('Email already exists');
      global.api = {
        auth: {
          register: jest.fn().mockRejectedValue(mockError)
        }
      };

      await auth.handleRegister(mockEvent);

      expect(mockEvent.preventDefault).toHaveBeenCalled();
      const errorDiv = document.getElementById('error-message');
      expect(errorDiv.textContent).toBe('Email already exists');
      expect(errorDiv.style.display).toBe('block');
    });
  });
});
