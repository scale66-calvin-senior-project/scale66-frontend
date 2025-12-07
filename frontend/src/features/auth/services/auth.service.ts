import { signInWithPassword, signUp, signOut, getCurrentUser as getSupabaseUser } from '@/lib/supabase';
import type { LoginCredentials, SignupData, User } from '../types';

/**
 * Auth Service
 * 
 * Handles authentication using Supabase
 */

export const authService = {
  async login(credentials: LoginCredentials): Promise<User> {
    const result = await signInWithPassword(credentials.email, credentials.password);
    
    if (!result.user) {
      throw new Error('No user returned from sign in');
    }

    return {
      id: result.user.id,
      email: result.user.email || '',
      name: result.user.user_metadata?.name || result.user.user_metadata?.full_name,
    };
  },

  async signup(data: SignupData): Promise<User> {
    const result = await signUp(data.email, data.password);
    
    if (!result.user) {
      throw new Error('No user returned from sign up');
    }

    return {
      id: result.user.id,
      email: result.user.email || '',
      name: data.name || result.user.user_metadata?.name || result.user.user_metadata?.full_name,
    };
  },

  async logout(): Promise<void> {
    await signOut();
  },

  async getCurrentUser(): Promise<User | null> {
    const user = await getSupabaseUser();
    
    if (!user) {
      return null;
    }

    return {
      id: user.id,
      email: user.email || '',
      name: user.user_metadata?.name || user.user_metadata?.full_name,
    };
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

