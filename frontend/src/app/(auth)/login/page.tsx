'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/features/auth';
import { LoginForm } from '@/features/auth';
import { getPostLoginRedirectPath } from '@/utils/auth-redirect';
import { supabase } from '@/lib/supabase';
import styles from '../auth-page.module.css';

/**
 * Login Page
 * 
 * User login page with email/password authentication
 * Checks for existing session and redirects if logged in
 * Redirects based on onboarding and subscription status after login
 */
export default function LoginPage() {
  const router = useRouter();
  const { refreshUser } = useAuth();

  useEffect(() => {
    // Check if user already has a session
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user) {
        // User is already logged in - redirect based on their status
        const { data: userData } = await supabase
          .from('users')
          .select('id, email, subscription_tier, onboarding_completed')
          .eq('id', session.user.id)
          .single();
        
        if (userData) {
          const redirectPath = getPostLoginRedirectPath({
            id: userData.id,
            email: userData.email,
            subscription_tier: userData.subscription_tier as 'free' | 'starter' | 'growth' | 'agency' | undefined,
            onboarding_completed: userData.onboarding_completed || false,
          });
          router.push(redirectPath);
        } else {
          router.push('/dashboard');
        }
      }
    };

    checkSession();
  }, [router]);

  const handleSuccess = async () => {
    // Refresh user data to ensure auth context is updated
    await refreshUser();
    
    // Fetch user data directly from Supabase to get onboarding_completed and subscription_tier
    try {
      const { data: { user: authUser } } = await supabase.auth.getUser();
      if (authUser) {
        // Get full user data from public.users table
        const { data: userData } = await supabase
          .from('users')
          .select('id, email, subscription_tier, onboarding_completed')
          .eq('id', authUser.id)
          .single();
        
        if (userData) {
          const redirectPath = getPostLoginRedirectPath({
            id: userData.id,
            email: userData.email,
            subscription_tier: userData.subscription_tier as 'free' | 'starter' | 'growth' | 'agency' | undefined,
            onboarding_completed: userData.onboarding_completed || false,
          });
          router.push(redirectPath);
          return;
        }
      }
    } catch (error) {
      console.error('Error fetching user data for redirect:', error);
    }
    
    // Fallback: if we can't get user data, go to dashboard
    router.push('/dashboard');
  };

  return (
    <div className={styles.authPage}>
      <div className={styles.authContainer}>
        <h1 className={styles.authTitle}>Welcome Back</h1>
        <p className={styles.authSubtitle}>Sign in to continue to Scale66</p>
        <LoginForm onSuccess={handleSuccess} />
        <div className={styles.authFooter}>
          <p className={styles.authFooterText}>
            Don&apos;t have an account?{' '}
            <a href="/signup" className={styles.authLink}>
              Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
