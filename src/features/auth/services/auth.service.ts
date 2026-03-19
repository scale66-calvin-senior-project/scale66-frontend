import { signInWithPassword, signOut, getCurrentUser as getSupabaseUser, supabase } from '@/lib/supabase';
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
    // Sign up user in Supabase Auth
    // The database trigger handle_new_user() will automatically create
    // a record in public.users table via the on_auth_user_created trigger
    // See: .cursor/rules/backend/database/supabase-tables.mdc
    
    console.log('[AUTH] Starting signup process:', {
      email: data.email,
      name: data.name,
      timestamp: new Date().toISOString(),
    });

    const { data: signupData, error } = await supabase.auth.signUp({
      email: data.email,
      password: data.password,
      options: {
        data: {
          name: data.name,
          full_name: data.name,
        },
        emailRedirectTo: `${typeof window !== 'undefined' ? window.location.origin : ''}/confirm-email`,
      },
    });

    if (error) {
      // Log comprehensive error details for debugging
      interface SupabaseError extends Error {
        status?: number;
        statusText?: string;
        code?: string;
        details?: string;
        hint?: string;
        error_description?: string;
        error_code?: string;
      }

      const supabaseError = error as SupabaseError;
      console.error('[AUTH] Supabase signup error - Full error object:', {
        error: error,
        errorType: error.constructor.name,
        message: error.message,
        status: supabaseError.status,
        statusText: supabaseError.statusText,
        code: supabaseError.code,
        details: supabaseError.details,
        hint: supabaseError.hint,
        errorDescription: supabaseError.error_description,
        errorCode: supabaseError.error_code,
        fullError: JSON.stringify(error, Object.getOwnPropertyNames(error), 2),
        timestamp: new Date().toISOString(),
        signupData: {
          email: data.email,
          name: data.name,
        },
      });

      // Also log the signup response data if available
      if (signupData?.user) {
        interface UserData {
          id: string;
          email?: string;
          created_at?: string;
          user_metadata?: Record<string, unknown>;
        }
        const userData = signupData.user as UserData;
        console.error('[AUTH] Signup response data (even with error):', {
          user: {
            id: userData.id,
            email: userData.email,
            created_at: userData.created_at,
            user_metadata: userData.user_metadata,
          },
          session: signupData.session ? 'Session exists' : 'No session',
        });
      }

      // Create a detailed error message with troubleshooting info
      const errorDetails = [
        error.message || 'Unknown error',
        supabaseError.hint ? `Hint: ${supabaseError.hint}` : '',
        supabaseError.details ? `Details: ${supabaseError.details}` : '',
        supabaseError.code ? `Code: ${supabaseError.code}` : '',
      ].filter(Boolean).join(' | ');

      // Check if this is a database trigger error
      const isDatabaseError = 
        error.message?.toLowerCase().includes('database error') ||
        error.message?.toLowerCase().includes('saving new user') ||
        supabaseError.code === 'unexpected_failure';

      if (isDatabaseError) {
        const troubleshootingMessage = 
          'This error usually means the database trigger is not set up correctly. ' +
          'Please run the SQL script in frontend/SUPABASE_TRIGGER_FIX.sql in your Supabase SQL Editor.';
        
        console.error('[AUTH] Database trigger error detected. Troubleshooting:', {
          message: troubleshootingMessage,
          sqlScript: 'frontend/SUPABASE_TRIGGER_FIX.sql',
        });

        throw new Error(`${errorDetails}\n\n${troubleshootingMessage}`);
      }

      throw new Error(`Failed to create account: ${errorDetails}`);
    }

    if (!signupData.user) {
      console.error('[AUTH] No user returned from signup:', {
        signupData,
        timestamp: new Date().toISOString(),
      });
      throw new Error('No user returned from sign up');
    }

    console.log('[AUTH] Signup successful:', {
      userId: signupData.user.id,
      email: signupData.user.email,
      timestamp: new Date().toISOString(),
    });

    // The user record in public.users should be created automatically by the trigger
    // We don't need to manually insert into the users table
    // The trigger function handle_new_user() with SECURITY DEFINER should bypass RLS
    return {
      id: signupData.user.id,
      email: signupData.user.email || '',
      name: data.name,
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

