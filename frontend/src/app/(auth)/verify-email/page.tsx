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
    // Check if already verified on mount
    const checkInitialStatus = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      
      // If we have a session, the user is verified
      if (session?.user) {
        setIsVerified(true);
        return;
      }

      // Get user email if available (from unverified session)
      const { data: { user } } = await supabase.auth.getUser();
      if (user?.email) {
        setEmail(user.email);
      } else if (session?.user?.email) {
        setEmail(session.user.email);
      }
    };

    checkInitialStatus();

    // Listen for storage events from the confirmation tab
    const handleStorageChange = async (e: StorageEvent) => {
      if (e.key === 'email-verified' && e.newValue === 'true') {
        // Email was verified in another tab
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session?.user) {
          // Clear the localStorage flag
          localStorage.removeItem('email-verified');
          localStorage.removeItem('email-verified-timestamp');
          setIsVerified(true);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Also poll for verification status (in case storage event doesn't fire)
    const pollInterval = setInterval(async () => {
      const { data: { session } } = await supabase.auth.getSession();
      
      // If we have a session, the user is verified
      if (session?.user) {
        const verifiedTimestamp = localStorage.getItem('email-verified-timestamp');
        if (verifiedTimestamp) {
          localStorage.removeItem('email-verified');
          localStorage.removeItem('email-verified-timestamp');
        }
        clearInterval(pollInterval);
        setIsVerified(true);
      }
    }, 1000); // Poll every 1 second

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(pollInterval);
    };
  }, []);

  // Show verified message if email is verified
  if (isVerified) {
    return (
      <div className={styles.authPage}>
        <div className={styles.authContainer}>
          <h1 className={styles.authTitle}>Email Verified!</h1>
          <p className={styles.authSubtitle}>
            Your email has been successfully verified. You can close this window and return to the app.
          </p>
          <div style={{ marginTop: '32px', textAlign: 'center' }}>
            <button
              onClick={() => router.push('/welcome')}
              className={styles.authLink}
              style={{
                display: 'inline-block',
                padding: '12px 24px',
                backgroundColor: '#000',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                textDecoration: 'none',
              }}
            >
              Continue to Onboarding
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.authPage}>
      <div className={styles.authContainer}>
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
      </div>
    </div>
  );
}

