/**
 * Stripe Integration
 * 
 * Client-side Stripe integration for checkout sessions
 */

import { loadStripe, Stripe } from '@stripe/stripe-js';
import { env } from '@/config/env';

// Initialize Stripe with publishable key
let stripePromise: Promise<Stripe | null> | null = null;

export const getStripe = (): Promise<Stripe | null> => {
  if (!stripePromise) {
    if (!env.stripePublishableKey) {
      console.warn('Stripe publishable key is not configured');
      return Promise.resolve(null);
    }
    stripePromise = loadStripe(env.stripePublishableKey);
  }
  return stripePromise;
};

/**
 * Redirect to Stripe Checkout
 * @param sessionId - Checkout session ID from backend
 */
export const redirectToCheckout = async (sessionId: string): Promise<void> => {
  const stripe = await getStripe();
  if (!stripe) {
    throw new Error('Stripe is not initialized. Please check your environment variables.');
  }
  
  // redirectToCheckout is a method on the Stripe instance
  // Type assertion needed as TypeScript types may not include this method
  const result = await (stripe as unknown as {
    redirectToCheckout: (options: { sessionId: string }) => Promise<{ error?: { message: string } }>;
  }).redirectToCheckout({ sessionId });
  
  if (result?.error) {
    throw new Error(result.error.message);
  }
};

