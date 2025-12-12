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
  
  const { error } = await stripe.redirectToCheckout({ sessionId });
  if (error) {
    throw error;
  }
};

