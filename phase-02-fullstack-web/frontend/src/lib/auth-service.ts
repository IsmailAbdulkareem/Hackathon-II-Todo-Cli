/**
 * Simple authentication service that connects directly to FastAPI backend
 */

const AUTH_TOKEN_KEY = 'auth_token';
const USER_ID_KEY = 'user_id';

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
}

export interface SignUpData {
  email: string;
  password: string;
}

export interface SignInData {
  email: string;
  password: string;
}

class AuthService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  /**
   * Register a new user
   */
  async signUp(data: SignUpData): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/api/auth/sign-up`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('Sign-up error:', error);
      throw new Error(error.detail || `Registration failed (${response.status})`);
    }

    const authData: AuthResponse = await response.json();

    // Store token and user ID
    this.setToken(authData.access_token);
    this.setUserId(authData.user_id);

    return authData;
  }

  /**
   * Sign in an existing user
   */
  async signIn(data: SignInData): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/api/auth/sign-in`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const authData: AuthResponse = await response.json();

    // Store token and user ID
    this.setToken(authData.access_token);
    this.setUserId(authData.user_id);

    return authData;
  }

  /**
   * Sign out the current user
   */
  signOut(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(AUTH_TOKEN_KEY);
      localStorage.removeItem(USER_ID_KEY);
    }
  }

  /**
   * Get the current JWT token
   */
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(AUTH_TOKEN_KEY);
    }
    return null;
  }

  /**
   * Get the current user ID
   */
  getUserId(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(USER_ID_KEY);
    }
    return null;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }

  /**
   * Set the JWT token
   */
  private setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(AUTH_TOKEN_KEY, token);
    }
  }

  /**
   * Set the user ID
   */
  private setUserId(userId: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(USER_ID_KEY, userId);
    }
  }
}

// Export singleton instance
export const authService = new AuthService();
