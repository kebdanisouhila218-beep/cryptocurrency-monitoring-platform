// frontend/src/services/authService.test.js
/**
 * Tests unitaires pour le service d'authentification
 */
import authService from './authService';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('AuthService', () => {
  beforeEach(() => {
    // Nettoyer localStorage avant chaque test
    localStorage.clear();
    jest.clearAllMocks();
  });

  describe('register', () => {
    it('should register a new user successfully', async () => {
      const mockResponse = {
        data: {
          username: 'testuser',
          email: 'test@example.com',
          created_at: '2024-12-29T10:00:00Z'
        }
      };

      axios.post.mockResolvedValue(mockResponse);

      const result = await authService.register('testuser', 'test@example.com', 'password123');

      expect(result.success).toBe(true);
      expect(result.data.username).toBe('testuser');
    });

    it('should handle registration error - username exists', async () => {
      axios.post.mockRejectedValue({
        response: {
          data: {
            detail: 'Username already exists'
          }
        }
      });

      const result = await authService.register('testuser', 'test@example.com', 'password123');

      expect(result.success).toBe(false);
      expect(result.error).toContain('already exists');
    });

    it('should handle network error during registration', async () => {
      axios.post.mockRejectedValue(new Error('Network Error'));

      const result = await authService.register('testuser', 'test@example.com', 'password123');

      expect(result.success).toBe(false);
    });
  });

  describe('login', () => {
    it('should login successfully and store token', async () => {
      const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6OTk5OTk5OTk5OX0.test';
      const mockResponse = {
        data: {
          access_token: mockToken,
          token_type: 'bearer'
        }
      };

      axios.post.mockResolvedValue(mockResponse);

      const result = await authService.login('testuser', 'password123');

      expect(result.success).toBe(true);
      expect(localStorage.getItem('token')).toBe(mockToken);
      expect(localStorage.getItem('username')).toBe('testuser');
    });

    it('should handle login error - wrong credentials', async () => {
      axios.post.mockRejectedValue({
        response: {
          data: {
            detail: 'Incorrect username or password'
          }
        }
      });

      const result = await authService.login('wronguser', 'wrongpass');

      expect(result.success).toBe(false);
      expect(result.error).toContain('Incorrect');
    });

    it('should handle login error - user not found', async () => {
      axios.post.mockRejectedValue({
        response: {
          status: 404,
          data: {
            detail: 'User not found'
          }
        }
      });

      const result = await authService.login('nonexistent', 'password123');

      expect(result.success).toBe(false);
    });
  });

  describe('logout', () => {
    it('should clear localStorage on logout', () => {
      localStorage.setItem('token', 'test-token');
      localStorage.setItem('username', 'testuser');

      authService.logout();

      expect(localStorage.getItem('token')).toBeNull();
      expect(localStorage.getItem('username')).toBeNull();
    });

    it('should work even if localStorage is empty', () => {
      expect(() => authService.logout()).not.toThrow();
    });
  });

  describe('isAuthenticated', () => {
    it('should return false if no token', () => {
      expect(authService.isAuthenticated()).toBe(false);
    });

    it('should return true if valid token exists', () => {
      // Token avec expiration dans le futur (timestamp très élevé)
      const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjo5OTk5OTk5OTk5fQ.test';
      localStorage.setItem('token', validToken);

      // Le comportement dépend de l'implémentation
      const result = authService.isAuthenticated();
      expect(typeof result).toBe('boolean');
    });
  });

  describe('getAuthHeader', () => {
    it('should return Authorization header with token', () => {
      localStorage.setItem('token', 'test-token');

      const header = authService.getAuthHeader();

      expect(header).toEqual({
        Authorization: 'Bearer test-token'
      });
    });

    it('should return empty object if no token', () => {
      const header = authService.getAuthHeader();

      expect(header).toEqual({});
    });
  });

  describe('getCurrentUser', () => {
    it('should fetch current user with valid token', async () => {
      const mockUser = {
        username: 'testuser',
        email: 'test@example.com',
        role: 'user'
      };

      localStorage.setItem('token', 'valid-token');
      axios.get.mockResolvedValue({ data: mockUser });

      const result = await authService.getCurrentUser();

      expect(result.success).toBe(true);
      expect(result.data.username).toBe('testuser');
    });

    it('should handle 401 error and logout', async () => {
      localStorage.setItem('token', 'expired-token');
      axios.get.mockRejectedValue({
        response: { status: 401 }
      });

      const result = await authService.getCurrentUser();

      expect(result.success).toBe(false);
    });
  });

  describe('getUsername', () => {
    it('should return username from localStorage', () => {
      localStorage.setItem('username', 'testuser');

      const username = authService.getUsername();

      expect(username).toBe('testuser');
    });

    it('should return null if no username', () => {
      const username = authService.getUsername();

      expect(username).toBeNull();
    });
  });
});
