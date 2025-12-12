'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import styles from '../auth-page.module.css';

/**
 * Email Confirmation Page
 * 
 * This page is shown when user clicks the email verification link
 * Opens in a new tab/window from the email
 * Verifies the email and signals the original tab via localStorage
 */
export default function ConfirmEmailPage() {
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [message, setMessage] = useState('Verifying your email...');

  useEffect(() => {
    const handleEmailVerification = async () => {
      try {
        // Check URL for verification tokens (Supabase redirects with hash fragments)
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        const accessToken = hashParams.get('access_token');
        const type = hashParams.get('type');

        if (accessToken && type === 'email') {
          // Supabase client with detectSessionInUrl: true should automatically process this
          // Wait a moment for Supabase to process the session
          await new Promise(resolve => setTimeout(resolve, 500));
          
          const { data: sessionData, error } = await supabase.auth.getSession();
          
          if (sessionData?.session && !error) {
            // Email verified successfully
            setStatus('success');
            setMessage('Email verified successfully! You can close this window.');
            
            // Signal the original tab that verification is complete
            // Use localStorage event to communicate across tabs
            const event = new StorageEvent('storage', {
              key: 'email-verified',
              newValue: 'true',
              storageArea: localStorage,
            });
            window.dispatchEvent(event);
            
            // Also set in localStorage for polling
            localStorage.setItem('email-verified', 'true');
            localStorage.setItem('email-verified-timestamp', Date.now().toString());
            
            // Clear the hash from URL
            window.history.replaceState(null, '', window.location.pathname);
          } else {
            throw new Error('Failed to verify email');
          }
        } else {
          // No tokens in URL - check if already verified
          const { data: sessionData } = await supabase.auth.getSession();
          if (sessionData?.session) {
            setStatus('success');
            setMessage('Email already verified! You can close this window.');
            localStorage.setItem('email-verified', 'true');
          } else {
            throw new Error('No verification tokens found');
          }
        }
      } catch (error) {
        console.error('Email verification error:', error);
        setStatus('error');
        setMessage('Failed to verify email. Please try clicking the link again or contact support.');
      }
    };

    handleEmailVerification();
  }, []);

  return (
    <div className={styles.authPage}>
      <div className={styles.authContainer}>
        {status === 'verifying' && (
          <>
            <h1 className={styles.authTitle}>Verifying Email...</h1>
            <p className={styles.authSubtitle}>{message}</p>
          </>
        )}
        {status === 'success' && (
          <>
            <h1 className={styles.authTitle}>Email Verified!</h1>
            <p className={styles.authSubtitle}>{message}</p>
            <div style={{ marginTop: '32px', textAlign: 'center' }}>
              <p style={{ fontSize: '14px', color: 'rgba(81, 81, 81, 0.75)' }}>
                Return to the original window to continue with onboarding.
              </p>
            </div>
          </>
        )}
        {status === 'error' && (
          <>
            <h1 className={styles.authTitle}>Verification Failed</h1>
            <p className={styles.authSubtitle}>{message}</p>
            <div style={{ marginTop: '32px', textAlign: 'center' }}>
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

