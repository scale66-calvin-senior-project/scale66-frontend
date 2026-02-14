'use client';

import { useEffect, useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { onboardingService } from '@/features/onboarding/services';
import type { OnboardingData } from '@/features/onboarding/types';

const STORAGE_DONE = 'payment_success_done';
const STORAGE_STARTED = 'payment_success_started';
const API_TIMEOUT_MS = 5000;
const OVERALL_TIMEOUT_MS = 12000;

/** Run a promise with a timeout; rejects on timeout. */
function withTimeout<T>(p: Promise<T>, ms: number): Promise<T> {
  return Promise.race([
    p,
    new Promise<T>((_, reject) => setTimeout(() => reject(new Error('Request timeout')), ms)),
  ]);
}

/** Get subscription tier from plan ID. */
function getSubscriptionTier(planId: string | null): 'starter' | 'growth' | 'agency' | null {
  if (!planId) return null;
  const planLower = planId.toLowerCase();
  if (planLower.includes('starter')) return 'starter';
  if (planLower.includes('growth')) return 'growth';
  if (planLower.includes('agency')) return 'agency';
  return null;
}

/** Save brand kit via Supabase (no backend). Used when API is unreachable. */
async function saveBrandKitViaSupabase(userId: string, data: Partial<OnboardingData>): Promise<void> {
  const brandName = (data.brandName ?? '').trim();
  if (!brandName) return;

  const row: Record<string, unknown> = {
    user_id: userId,
    brand_name: brandName,
  };
  if ((data.brandNiche ?? '').trim()) row.brand_niche = (data.brandNiche as string).trim();
  if ((data.brandStyle ?? '').trim()) row.brand_style = (data.brandStyle as string).trim();
  if ((data.productService ?? '').trim()) row.product_service_description = (data.productService as string).trim();
  if (data.customerPainPoints) {
    const arr = Array.isArray(data.customerPainPoints) ? data.customerPainPoints : [data.customerPainPoints];
    row.customer_pain_points = arr.map((p) => String(p).trim()).filter(Boolean).join('\n') || null;
  }

  const { data: existing } = await supabase.from('brand_kits').select('id').eq('user_id', userId).limit(1).maybeSingle();
  if (existing) {
    await supabase.from('brand_kits').update(row).eq('user_id', userId);
  } else {
    await supabase.from('brand_kits').insert(row);
  }
}

/**
 * Payment Success Page
 *
 * Handles redirect from Stripe Payment Link after successful payment.
 * Uses Supabase-first for user update so it works even when the backend API is unreachable.
 * Uses sessionStorage to avoid re-running and looping on remounts.
 */
function PaymentSuccessPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Processing your payment...');
  const hasRunRef = useRef(false);

  useEffect(() => {
    const goDashboard = () => {
      if (typeof window !== 'undefined') {
        sessionStorage.removeItem(STORAGE_STARTED);
        sessionStorage.setItem(STORAGE_DONE, '1');
      }
      router.push('/dashboard');
    };

    // Already completed in this tab – skip processing and redirect
    if (typeof window !== 'undefined' && sessionStorage.getItem(STORAGE_DONE)) {
      goDashboard();
      return;
    }

    // Remount while previous run still in progress – don’t start again; cap wait and redirect
    if (typeof window !== 'undefined' && sessionStorage.getItem(STORAGE_STARTED)) {
      const t = setTimeout(goDashboard, 15000);
      return () => clearTimeout(t);
    }

    if (hasRunRef.current) return;
    hasRunRef.current = true;
    if (typeof window !== 'undefined') sessionStorage.setItem(STORAGE_STARTED, '1');

    const processPayment = async () => {
      let authUser: { id: string } | null = null;
      let subscriptionTier: 'starter' | 'growth' | 'agency' | null = null;

      try {
        setStatus('loading');
        setMessage('Processing your payment...');

        const { data: { user }, error: authError } = await supabase.auth.getUser();
        if (authError || !user) {
          setStatus('error');
          setMessage('You must be logged in. Redirecting to login...');
          setTimeout(() => router.push('/login'), 2000);
          return;
        }
        authUser = user;

        const planId = searchParams.get('plan_id') || searchParams.get('plan') || (typeof window !== 'undefined' ? localStorage.getItem('selected_plan_id') : null);
        if (!planId) {
          setStatus('error');
          setMessage('Could not identify which plan you purchased. Please contact support.');
          setTimeout(goDashboard, 5000);
          return;
        }

        subscriptionTier = getSubscriptionTier(planId);
        if (!subscriptionTier) {
          setStatus('error');
          setMessage('Invalid plan selected. Please contact support.');
          setTimeout(goDashboard, 5000);
          return;
        }

        // 1) Update user in Supabase first (no backend dependency – avoids Network Error loop)
        setMessage('Updating your account...');
        const { error: updateError } = await supabase
          .from('users')
          .update({ subscription_tier: subscriptionTier, onboarding_completed: true })
          .eq('id', authUser.id);

        if (updateError) {
          console.error('Supabase user update error:', updateError);
          throw updateError;
        }
        console.log(`✅ Updated user: subscription_tier=${subscriptionTier}, onboarding_completed=true`);

        // 2) Brand kit: try API with timeout, then Supabase fallback
        const onboardingData = onboardingService.loadFromLocalStorage();
        if (onboardingData && Object.keys(onboardingData).length > 0 && (onboardingData.brandName ?? '').trim()) {
          setMessage('Saving your brand information...');
          try {
            await withTimeout(onboardingService.saveBrandKit(onboardingData), API_TIMEOUT_MS);
            console.log('✅ Brand kit saved via API');
          } catch (brandKitErr) {
            console.warn('Brand kit API failed, trying Supabase:', brandKitErr);
            try {
              await saveBrandKitViaSupabase(authUser.id, onboardingData);
              console.log('✅ Brand kit saved via Supabase');
            } catch (supabaseErr) {
              console.warn('Brand kit Supabase fallback failed:', supabaseErr);
            }
          }
        }

        onboardingService.clearLocalStorage();
        if (typeof window !== 'undefined') localStorage.removeItem('selected_plan_id');

        setStatus('success');
        setMessage('Payment successful! Your account has been activated. Redirecting to dashboard...');
        setTimeout(goDashboard, 1500);
      } catch (error) {
        console.error('Payment processing error:', error);
        if (authUser && subscriptionTier) {
          const { error: fallbackErr } = await supabase
            .from('users')
            .update({ subscription_tier: subscriptionTier, onboarding_completed: true })
            .eq('id', authUser.id);
          if (!fallbackErr) console.log('✅ User updated via Supabase on error path');
        }
        setStatus('success');
        setMessage('Payment recorded. Redirecting to dashboard...');
        setTimeout(goDashboard, 2000);
      }
    };

    const timeoutId = setTimeout(() => {
      setMessage('Almost there...');
    }, OVERALL_TIMEOUT_MS - 2000);

    processPayment().finally(() => clearTimeout(timeoutId));
  }, [router, searchParams]);

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
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#515151' }}>Payment Processing Issue</h1>
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
