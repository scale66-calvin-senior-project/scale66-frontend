'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { supabase } from '@/lib/supabase';
import type { User } from '@/features/auth/types';
import { authService } from '@/features/auth/services/auth.service';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isSubscribed: boolean;
  isLoading: boolean;
  refreshUser: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

/**
 * AuthContext
 * Manages authentication state and subscription status
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUserWithSubscription = async (authUserId: string): Promise<User | null> => {
    try {
      // Get user data from public.users table (includes subscription_tier)
      const { data, error } = await supabase
        .from('users')
        .select('id, email, subscription_tier, stripe_customer_id, onboarding_completed')
        .eq('id', authUserId)
        .single();

      if (error) {
        // If user doesn't exist in users table yet, that's okay - they might be new
        // Return a basic user object with default values
        if (error.code === 'PGRST116') {
          console.log('User not found in users table yet, using default values');
          return {
            id: authUserId,
            email: '',
            subscription_tier: 'free',
          };
        }
        console.error('Error fetching user data:', error);
        return null;
      }

      return {
        id: data.id,
        email: data.email,
        subscription_tier: data.subscription_tier || 'free',
        stripe_customer_id: data.stripe_customer_id,
        onboarding_completed: data.onboarding_completed,
      };
    } catch (error) {
      console.error('Error fetching user with subscription:', error);
      return null;
    }
  };

  const loadUser = useCallback(async (skipLoadingState = false) => {
    if (!skipLoadingState) {
      setIsLoading(true);
    }
    try {
      const authUser = await authService.getCurrentUser();
      
      if (authUser) {
        // Fetch full user data including subscription
        const fullUser = await fetchUserWithSubscription(authUser.id);
        // If fetch failed but we have auth user, create basic user object
        setUser(fullUser || {
          id: authUser.id,
          email: authUser.email,
          subscription_tier: 'free',
        });
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Error loading user:', error);
      setUser(null);
    } finally {
      // Always set loading to false, even on error
      setIsLoading(false);
    }
  }, []);

  const refreshUser = async () => {
    await loadUser();
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  useEffect(() => {
    let mounted = true;

    const setBasicUser = (sessionUser: { id: string; email?: string }) => {
      const basicUser: User = {
        id: sessionUser.id,
        email: sessionUser.email || '',
        subscription_tier: 'free',
      };
      setUser(basicUser);
      setIsLoading(false);
      loadUser(true).catch(console.error);
    };

    // onAuthStateChange is the single source of truth for auth state.
    // INITIAL_SESSION fires once Supabase has fully initialized — including
    // completing any background token refresh. This is the right place to
    // gate rendering, unlike getSession() which can return null mid-refresh.
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (!mounted) return;

      if (event === 'INITIAL_SESSION') {
        if (session?.user) {
          setBasicUser(session.user);
        } else {
          // No session — user is not logged in (Supabase completes any token
          // refresh before firing INITIAL_SESSION, so null here is definitive).
          setUser(null);
          setIsLoading(false);
        }
      } else if (event === 'TOKEN_REFRESHED') {
        // Proactive refresh mid-session — update user silently.
        if (session?.user) {
          setBasicUser(session.user);
        } else {
          setUser(null);
          setIsLoading(false);
        }
      } else if (event === 'SIGNED_IN') {
        // Set a basic user immediately so AppLayout unblocks at once,
        // then load full user data (subscription tier etc.) in the background.
        if (session?.user) {
          setBasicUser(session.user);
        }
      } else if (event === 'SIGNED_OUT') {
        setUser(null);
        setIsLoading(false);
      }
    });

    // Safety timeout: unblock if INITIAL_SESSION never fires (e.g. Supabase
    // client fails to initialize entirely).
    const timeoutId = setTimeout(() => {
      if (mounted) {
        setIsLoading(false);
      }
    }, 5000);

    return () => {
      mounted = false;
      clearTimeout(timeoutId);
      subscription.unsubscribe();
    };
  }, [loadUser]);

  const isSubscribed = user?.subscription_tier === 'starter' || user?.subscription_tier === 'growth' || user?.subscription_tier === 'agency';

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isSubscribed,
        isLoading,
        refreshUser,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuthContext must be used within AuthProvider');
  return context;
};
