/**
 * Auth Types
 * 
 * TODO: Define authentication interfaces
 */

export interface User {
  // TODO: Define user interface
  id: string;
  email: string;
  name?: string;
}

export interface LoginCredentials {
  // TODO: Define login credentials
  email: string;
  password: string;
}

export interface SignupData {
  // TODO: Define signup data
  email: string;
  password: string;
  name?: string;
}

export interface AuthState {
  // TODO: Define auth state
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

