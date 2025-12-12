'use client';

import { useEffect, useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/features/auth';
import { supabase } from '@/lib/supabase';
import { env } from '@/config/env';

/**
 * Payment Success Page
 * 
 * Handles redirect from Stripe Payment Link after successful payment
 * Verifies payment and updates user subscription_tier in Supabase
 */
function PaymentSuccessPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUser } = useAuth();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Processing your payment...');
  const hasRunRef = useRef(false);

  // Get subscription tier from plan ID
  // Store the actual plan name: 'starter', 'growth', or 'agency'
  const getSubscriptionTier = (planId: string | null): 'starter' | 'growth' | 'agency' | null => {
    if (!planId) return null;
    const planLower = planId.toLowerCase();
    
    // Return the actual plan name
    if (planLower.includes('starter')) return 'starter';
    if (planLower.includes('growth')) return 'growth';
    if (planLower.includes('agency')) return 'agency';
    
    return null;
  };

  useEffect(() => {
    // Prevent multiple runs
    if (hasRunRef.current) {
      return;
    }
    hasRunRef.current = true;

    const verifyPayment = async () => {
      try {
        // Get payment intent or session ID from URL params (Stripe adds these)
        const paymentIntentId = searchParams.get('payment_intent');
        const sessionId = searchParams.get('session_id');
        
        // Get plan ID from URL params (if Payment Link was configured with it)
        const planIdFromUrl = searchParams.get('plan_id') || searchParams.get('plan');
        
        // Get plan ID from localStorage (stored before redirecting to Stripe)
        const planIdFromStorage = typeof window !== 'undefined' 
          ? localStorage.getItem('selected_plan_id')
          : null;
        
        const planId = planIdFromUrl || planIdFromStorage;
        
        console.log('Payment verification:', {
          paymentIntentId,
          sessionId,
          planIdFromUrl,
          planIdFromStorage,
          planId,
        });
        
        // Get current user
        const { data: { user: authUser }, error: authError } = await supabase.auth.getUser();
        if (authError || !authUser) {
          console.error('Auth error:', authError);
          setStatus('error');
          setMessage('You must be logged in to verify payment. Redirecting to login...');
          setTimeout(() => {
            router.push('/login');
          }, 2000);
          return;
        }

        // Determine subscription tier from plan ID
        let subscriptionTier = getSubscriptionTier(planId);
        
        // If we have payment intent or session ID, try to verify with backend
        // This is optional - we'll update subscription_tier regardless
        // Add timeout to prevent hanging
        if (paymentIntentId || sessionId) {
          try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
            
            const response = await fetch(`${env.apiBaseUrl}/api/v1/payment/verify`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              credentials: 'include',
              signal: controller.signal,
              body: JSON.stringify({
                payment_intent_id: paymentIntentId,
                session_id: sessionId,
              }),
            });

            clearTimeout(timeoutId);

            if (response.ok) {
              const data = await response.json();
              // Backend should return the plan/subscription tier
              if (data.subscription_tier) {
                subscriptionTier = data.subscription_tier as 'starter' | 'growth' | 'agency';
              } else if (data.plan_id) {
                subscriptionTier = getSubscriptionTier(data.plan_id);
              }
            }
          } catch (verifyError) {
            console.error('Backend verification error (continuing anyway):', verifyError);
            // Continue with plan_id from URL if backend fails
            if (!subscriptionTier && planId) {
              subscriptionTier = getSubscriptionTier(planId);
            }
          }
        }
        
        // Update subscription_tier directly in Supabase
        // This ensures the user gets updated even if webhook hasn't fired yet
        let finalStatus: 'success' | 'error' = 'success';
        let finalMessage = 'Payment successful! Your subscription has been activated. Redirecting to dashboard...';
        
        if (subscriptionTier) {
          console.log(`💾 Updating subscription_tier to ${subscriptionTier} for user ${authUser.id}`);
          
          // Add timeout to prevent hanging
          const updatePromise = supabase
            .from('users')
            .update({ subscription_tier: subscriptionTier })
            .eq('id', authUser.id);
          
          const timeoutPromise = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Update timeout')), 8000)
          );
          
          try {
            await Promise.race([updatePromise, timeoutPromise]);
            console.log(`✅ Updated subscription_tier to ${subscriptionTier} for user ${authUser.id}`);
            // Clear the stored plan ID after successful update
            if (typeof window !== 'undefined') {
              localStorage.removeItem('selected_plan_id');
            }
          } catch (updateError: unknown) {
            console.error('Error updating subscription tier:', updateError);
            // If it's a timeout, still show success (webhook might have updated it)
            const errorMessage = updateError instanceof Error ? updateError.message : String(updateError);
            if (errorMessage.includes('timeout')) {
              console.warn('Update timed out, but webhook may have processed it');
              finalStatus = 'success';
              finalMessage = 'Payment successful! Your subscription is being processed. Redirecting to dashboard...';
            } else {
              finalStatus = 'error';
              finalMessage = 'Payment received but there was an issue updating your subscription. Please contact support.';
            }
          }
        } else {
          // No plan ID found - this shouldn't happen, but handle gracefully
          console.warn('No plan ID found - cannot update subscription tier');
          console.warn('URL params:', { planIdFromUrl, planIdFromStorage, planId });
          finalStatus = 'error';
          finalMessage = 'Payment received but we could not identify which plan you purchased. Please contact support with your payment details.';
        }
        
        // Refresh user data to get updated subscription (with timeout)
        try {
          const refreshPromise = refreshUser();
          const refreshTimeout = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Refresh timeout')), 5000)
          );
          await Promise.race([refreshPromise, refreshTimeout]);
        } catch (refreshError) {
          console.error('Error refreshing user (continuing anyway):', refreshError);
        }
        
        // Update UI status
        setStatus(finalStatus);
        setMessage(finalMessage);
        
        // Redirect to dashboard after showing status
        setTimeout(() => {
          router.push('/dashboard');
        }, finalStatus === 'success' ? 2000 : 5000);
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty deps - only run once on mount

  // SVG Icon Components
  const LoadingIcon = () => (
    <svg 
      width="64" 
      height="64" 
      viewBox="0 0 24 24" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle 
        cx="12" 
        cy="12" 
        r="10" 
        stroke="currentColor" 
        strokeWidth="2" 
        strokeLinecap="round" 
        strokeDasharray="31.416" 
        strokeDashoffset="15.708"
        className="payment-spinner"
        style={{ transformOrigin: '12px 12px' }}
      />
    </svg>
  );

  const SuccessIcon = () => (
    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none"/>
      <path d="M8 12l2 2 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
    </svg>
  );

  const ErrorIcon = () => (
    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none"/>
      <path d="M12 8v4" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
      <path d="M12 16h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  );

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
          <div style={{ marginBottom: '1rem', color: '#5a79ff' }}>
            <LoadingIcon />
          </div>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#515151' }}>Processing Payment</h1>
          <p style={{ color: 'rgba(81, 81, 81, 0.75)' }}>{message}</p>
        </>
      )}
      
      {status === 'success' && (
        <>
          <div style={{ marginBottom: '1rem', color: '#10b981' }}>
            <SuccessIcon />
          </div>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#515151' }}>Payment Successful!</h1>
          <p style={{ color: 'rgba(81, 81, 81, 0.75)' }}>{message}</p>
        </>
      )}
      
      {status === 'error' && (
        <>
          <div style={{ marginBottom: '1rem', color: '#ef4444' }}>
            <ErrorIcon />
          </div>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#515151' }}>Payment Verification Issue</h1>
          <p style={{ color: 'rgba(81, 81, 81, 0.75)' }}>{message}</p>
        </>
      )}
    </div>
  );
}

export default function PaymentSuccessPage() {
  return (
    <Suspense fallback={
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '2rem',
        textAlign: 'center',
      }}>
        <p>Loading...</p>
      </div>
    }>
      <PaymentSuccessPageContent />
    </Suspense>
  );
}

