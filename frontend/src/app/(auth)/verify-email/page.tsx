'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import styles from '../auth-page.module.css';

/**
 * Verify Email Page
 * 
 * Shown after signup to instruct users to check their email
 * Polls for email verification status and redirects to onboarding when verified
 * The email link opens in a new tab showing the confirmation page
 */
export default function VerifyEmailPage() {
  const router = useRouter();
  const [email, setEmail] = useState<string>('');
  const [isVerified, setIsVerified] = useState(false);

  useEffect(() => {
    // Get user email if available (from unverified session)
    const getUserEmail = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (user?.email) {
        setEmail(user.email);
      } else {
        // Try to get from session
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.user?.email) {
          setEmail(session.user.email);
        }
      }
    };

    getUserEmail();

    // Check if already verified on mount
    const checkInitialStatus = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user) {
        setIsVerified(true);
        setTimeout(() => {
          router.push('/welcome');
        }, 1000);
        return;
      }
    };

    checkInitialStatus();

    // Listen for storage events from the confirmation tab
    const handleStorageChange = async (e: StorageEvent) => {
      if (e.key === 'email-verified' && e.newValue === 'true') {
        // Email was verified in another tab
        // Verify we have a session
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.user) {
          setIsVerified(true);
          // Clear the localStorage flag
          localStorage.removeItem('email-verified');
          localStorage.removeItem('email-verified-timestamp');
          // Redirect to onboarding
          setTimeout(() => {
            router.push('/welcome');
          }, 1000);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Also poll for verification status (in case storage event doesn't fire)
    const pollInterval = setInterval(async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user) {
        // Check if this is a new verification (not just an existing session)
        const verifiedTimestamp = localStorage.getItem('email-verified-timestamp');
        if (verifiedTimestamp) {
          setIsVerified(true);
          localStorage.removeItem('email-verified');
          localStorage.removeItem('email-verified-timestamp');
          clearInterval(pollInterval);
          setTimeout(() => {
            router.push('/welcome');
          }, 1000);
        }
      }
    }, 2000); // Poll every 2 seconds

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(pollInterval);
    };
  }, [router]);

  return (
    <div className={styles.authPage}>
      <div className={styles.authContainer}>
        {isVerified ? (
          <>
            <h1 className={styles.authTitle}>Email Verified!</h1>
            <p className={styles.authSubtitle}>
              Your email has been verified successfully. Redirecting to onboarding...
            </p>
          </>
        ) : (
          <>
            <h1 className={styles.authTitle}>Check Your Email</h1>
            <p className={styles.authSubtitle}>
              {email 
                ? `We've sent a verification link to ${email}. Please check your inbox and click the link to verify your account.`
                : "We've sent a verification link to your email. Please check your inbox and click the link to verify your account."}
            </p>
            <div style={{ marginTop: '32px', textAlign: 'center' }}>
              <p style={{ fontSize: '14px', color: 'rgba(81, 81, 81, 0.75)', marginBottom: '16px' }}>
                Didn't receive the email? Check your spam folder or try signing up again.
              </p>
              <a href="/signup" className={styles.authLink}>
                Back to Sign Up
              </a>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

