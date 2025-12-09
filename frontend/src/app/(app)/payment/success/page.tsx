'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/features/auth';
import { env } from '@/config/env';

/**
 * Payment Success Page
 * 
 * Handles redirect from Stripe Payment Link after successful payment
 * Verifies payment and updates user subscription in Supabase
 */
export default function PaymentSuccessPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUser } = useAuth();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Processing your payment...');

  useEffect(() => {
    const verifyPayment = async () => {
      try {
        // Get payment intent or session ID from URL params
        const paymentIntentId = searchParams.get('payment_intent');
        const sessionId = searchParams.get('session_id');
        
        // Refresh user data to get updated subscription (webhook should have updated it)
        await refreshUser();
        
        if (!paymentIntentId && !sessionId) {
          // If no payment info, just redirect to dashboard
          // The webhook will handle the subscription update
          setStatus('success');
          setMessage('Payment successful! Redirecting to dashboard...');
          setTimeout(() => {
            router.push('/dashboard');
          }, 2000);
          return;
        }

        // Verify payment with backend
        const response = await fetch(`${env.apiBaseUrl}/api/v1/payment/verify`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            payment_intent_id: paymentIntentId,
            session_id: sessionId,
          }),
        });

        if (!response.ok) {
          throw new Error('Payment verification failed');
        }

        // Refresh user data again after verification
        await refreshUser();

        setStatus('success');
        setMessage('Payment successful! Redirecting to dashboard...');

        // Redirect to dashboard after 2 seconds
        setTimeout(() => {
          router.push('/dashboard');
        }, 2000);
      } catch (error) {
        console.error('Payment verification error:', error);
        setStatus('error');
        setMessage('There was an issue verifying your payment. Please contact support if the charge appears on your account.');
        
        // Still redirect after error (webhook may have processed it)
        setTimeout(() => {
          router.push('/dashboard');
        }, 5000);
      }
    };

    verifyPayment();
  }, [searchParams, router, refreshUser]);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '2rem',
      textAlign: 'center',
    }}>
      {status === 'loading' && (
        <>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⏳</div>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Processing Payment</h1>
          <p>{message}</p>
        </>
      )}
      
      {status === 'success' && (
        <>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Payment Successful!</h1>
          <p>{message}</p>
        </>
      )}
      
      {status === 'error' && (
        <>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>Payment Verification Issue</h1>
          <p>{message}</p>
        </>
      )}
    </div>
  );
}

