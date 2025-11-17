import type { LoginCredentials, SignupData, User } from '../types';

/**
 * Auth Service
 * 
 * TODO: Implement authentication API calls
 * - Login
 * - Signup
 * - Logout
 * - OAuth (Google, Apple)
 * - Token refresh
 * - Password reset
 */

export const authService = {
  async login(credentials: LoginCredentials): Promise<User> {
    // TODO: Implement login
    throw new Error('Not implemented');
  },

  async signup(data: SignupData): Promise<User> {
    // TODO: Implement signup
    throw new Error('Not implemented');
  },

  async logout(): Promise<void> {
    // TODO: Implement logout
    throw new Error('Not implemented');
  },

  async getCurrentUser(): Promise<User | null> {
    // TODO: Implement get current user
    throw new Error('Not implemented');
  },

  async loginWithGoogle(): Promise<User> {
    // TODO: Implement Google OAuth
    throw new Error('Not implemented');
  },

  async loginWithApple(): Promise<User> {
    // TODO: Implement Apple OAuth
    throw new Error('Not implemented');
  },
};

