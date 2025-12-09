/**
 * Payment Service
 * Handles payment-related API calls
 */

import { apiClient } from '@/services/api/client';
import type { CheckoutSessionRequest, CheckoutSessionResponse, SubscriptionStatus, PlanId } from '../types';

class PaymentService {
  /**
   * Create a Stripe checkout session
   */
  async createCheckoutSession(request: CheckoutSessionRequest): Promise<CheckoutSessionResponse> {
    const { data } = await apiClient.post<CheckoutSessionResponse>('/api/v1/payment/checkout', {
      plan_id: request.planId,
      success_url: request.successUrl || `${window.location.origin}/dashboard?payment=success`,
      cancel_url: request.cancelUrl || `${window.location.origin}/onboarding?payment=cancelled`,
    });
    return data;
  }

  /**
   * Get current subscription status
   */
  async getSubscriptionStatus(): Promise<SubscriptionStatus> {
    const { data } = await apiClient.get<SubscriptionStatus>('/api/v1/payment/subscription');
    return data;
  }

  /**
   * Cancel subscription
   */
  async cancelSubscription(): Promise<void> {
    await apiClient.post('/api/v1/payment/subscription/cancel');
  }

  /**
   * Update subscription plan
   */
  async updateSubscription(planId: PlanId): Promise<SubscriptionStatus> {
    const { data } = await apiClient.post<SubscriptionStatus>('/api/v1/payment/subscription/update', {
      plan_id: planId,
    });
    return data;
  }
}

export const paymentService = new PaymentService();
export type { PaymentService };
