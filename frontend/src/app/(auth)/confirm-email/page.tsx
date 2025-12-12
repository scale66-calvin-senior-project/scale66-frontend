'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import styles from '../auth-page.module.css';

/**
 * Email Confirmation Page
 * 
 * This page is shown when user clicks the email verification link
 * Opens in a new tab/window from the email
 * Verifies the email and signals the original tab via localStorage
 * If opened in the same tab, redirects directly to welcome page
 */
export default function ConfirmEmailPage() {
  const router = useRouter();
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [message, setMessage] = useState('Verifying your email...');
  const [hasRedirected, setHasRedirected] = useState(false);

  useEffect(() => {
    const handleEmailVerification = async () => {
      try {
        // Check URL for verification tokens (Supabase redirects with hash fragments)
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        const accessToken = hashParams.get('access_token');
        const type = hashParams.get('type');

        // If we have tokens in the URL, Supabase should process them automatically
        // Wait for Supabase to process the session (with multiple retries)
        let sessionData = null;
        let attempts = 0;
        const maxAttempts = 8; // Give it enough time

        while (attempts < maxAttempts && !sessionData) {
          await new Promise(resolve => setTimeout(resolve, 300));
          
          const { data: session } = await supabase.auth.getSession();
          
          if (session?.session) {
            sessionData = session;
            break;
          }
          
          attempts++;
        }

        // If we have a session, verification was successful
        if (sessionData?.session) {
          // Show success message
          setStatus('success');
          setMessage('Email verified successfully!');
          
          // Signal the original tab that verification is complete
          localStorage.setItem('email-verified', 'true');
          localStorage.setItem('email-verified-timestamp', Date.now().toString());
          
          // Dispatch storage event for cross-tab communication
          window.dispatchEvent(new StorageEvent('storage', {
            key: 'email-verified',
            newValue: 'true',
            storageArea: localStorage,
          }));
          
          // Clear the hash from URL
          window.history.replaceState(null, '', window.location.pathname);
          
          // Redirect after showing success message for a moment
          setTimeout(() => {
            if (!hasRedirected) {
              setHasRedirected(true);
              router.replace('/welcome');
            }
          }, 2000);
        } else if (accessToken && type === 'email') {
          // We have tokens but no session yet - wait a bit more
          setTimeout(async () => {
            const { data: session } = await supabase.auth.getSession();
            if (session?.session) {
              setStatus('success');
              setMessage('Email verified successfully!');
              localStorage.setItem('email-verified', 'true');
              localStorage.setItem('email-verified-timestamp', Date.now().toString());
              setTimeout(() => {
                if (!hasRedirected) {
                  setHasRedirected(true);
                  router.replace('/welcome');
                }
              }, 2000);
            } else {
              setStatus('error');
              setMessage('Verification is taking longer than expected. You can close this window and return to the app.');
            }
          }, 1000);
        } else {
          // No tokens - check if already verified
          const { data: { session } } = await supabase.auth.getSession();
          if (session?.session) {
            setStatus('success');
            setMessage('Email already verified!');
            setTimeout(() => {
              if (!hasRedirected) {
                setHasRedirected(true);
                router.replace('/welcome');
              }
            }, 2000);
          } else {
            setStatus('error');
            setMessage('No verification tokens found. Please check your email and click the verification link.');
          }
        }
      } catch (error) {
        console.error('[EMAIL VERIFICATION] Error:', error);
        setStatus('error');
        setMessage('There was an issue verifying your email. Please try clicking the link again.');
      }
    };

    handleEmailVerification();
  }, [router, hasRedirected]);

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
                You can close this window and return to the app.
              </p>
              <p style={{ fontSize: '14px', color: 'rgba(81, 81, 81, 0.75)', marginTop: '8px' }}>
                Redirecting automatically...
              </p>
            </div>
          </>
        )}
        {status === 'error' && (
          <>
            <h1 className={styles.authTitle}>Verification Issue</h1>
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

