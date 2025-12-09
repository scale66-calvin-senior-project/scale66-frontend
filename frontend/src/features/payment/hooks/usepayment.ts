/**
 * usePayment Hook
 * Manages payment state and checkout flow
 * 
 * Supports two modes:
 * 1. Direct Payment Links (simpler, no backend needed)
 * 2. Checkout Sessions (via backend API)
 */

import { useState } from 'react';
import { paymentService } from '../services';
import { redirectToCheckout } from '@/lib/stripe';
import { env } from '@/config/env';
import type { PlanId } from '../types';

export const usePayment = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handlePlanSelect = async (planId: PlanId): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // Check if using direct Payment Links (simpler approach)
      const paymentLink = env.stripePaymentLinks[planId];
      
      if (paymentLink) {
        // Redirect directly to Stripe Payment Link
        // Using globalThis.location for external redirect (client-side only)
        if (typeof globalThis !== 'undefined' && globalThis.location) {
          globalThis.location.href = paymentLink;
        }
        return;
      }

      // Otherwise, use backend checkout session creation
      const session = await paymentService.createCheckoutSession({
        planId,
      });

      // Redirect to Stripe Checkout
      await redirectToCheckout(session.sessionId);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to process payment');
      setError(error);
      console.error('Payment error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    handlePlanSelect,
  };
};
