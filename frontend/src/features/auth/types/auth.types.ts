/**
 * Auth Types
 * 
 * TODO: Define authentication interfaces
 */

export interface User {
  id: string;
  email: string;
  name?: string;
  subscription_tier?: 'free' | 'pro' | 'premium';
  stripe_customer_id?: string;
  onboarding_completed?: boolean;
}

export interface LoginCredentials {
  // TODO: Define login credentials
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  password: string;
  name: string;
}

export interface AuthState {
  // TODO: Define auth state
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

