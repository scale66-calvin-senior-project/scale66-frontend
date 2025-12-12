'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { SignupForm } from '@/features/auth';
import { supabase } from '@/lib/supabase';
import { getPostLoginRedirectPath } from '@/utils/auth-redirect';
import styles from '../auth-page.module.css';

/**
 * Signup Page
 * 
 * User registration page with email/password signup
 * Checks for existing session and redirects if logged in
 * Redirects to verify-email on success
 */
export default function SignupPage() {
  const router = useRouter();

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
            subscription_tier: userData.subscription_tier as 'free' | 'pro' | 'premium' | undefined,
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

  const handleSuccess = () => {
    router.push('/verify-email');
  };

  return (
    <div className={styles.authPage}>
      <div className={styles.authContainer}>
        <h1 className={styles.authTitle}>Get Started</h1>
        <p className={styles.authSubtitle}>
          Create your account to start creating amazing content
        </p>
        <SignupForm onSuccess={handleSuccess} />
        <div className={styles.authFooter}>
          <p className={styles.authFooterText}>
            Already have an account?{' '}
            <a href="/login" className={styles.authLink}>
              Sign in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
