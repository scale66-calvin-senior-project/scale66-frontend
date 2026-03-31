/**
 * Payment Service
 * Handles payment-related API calls
 *
 * NOTE: The backend currently only implements:
 *   POST /api/v1/payments/transactions  (record a transaction)
 *   GET  /api/v1/payments/transactions  (list transactions)
 *   GET  /api/v1/payments/transactions/:id
 *   POST /api/v1/payments/webhook       (Stripe webhook handler)
 *
 * The Stripe checkout session, subscription management, and customer-portal
 * endpoints below are commented out until the backend implements them.
 */

// import { apiClient } from '@/services/api/client';
import type { CheckoutSessionRequest, CheckoutSessionResponse, SubscriptionStatus, PlanId } from '../types';

class PaymentService {
  // /**
  //  * Create a Stripe checkout session
  //  * TODO: Backend needs POST /api/v1/payments/checkout
  //  */
  // async createCheckoutSession(request: CheckoutSessionRequest): Promise<CheckoutSessionResponse> {
  //   const { data } = await apiClient.post<CheckoutSessionResponse>('/api/v1/payments/checkout', {
  //     plan_id: request.planId,
  //     success_url: request.successUrl || `${window.location.origin}/payment/success?plan_id=${request.planId}`,
  //     cancel_url: request.cancelUrl || `${window.location.origin}/welcome?step=7&payment=cancelled`,
  //   });
  //   return data;
  // }

  // /**
  //  * Get current subscription status
  //  * TODO: Backend needs GET /api/v1/payments/subscription
  //  */
  // async getSubscriptionStatus(): Promise<SubscriptionStatus> {
  //   const { data } = await apiClient.get<SubscriptionStatus>('/api/v1/payments/subscription');
  //   return data;
  // }

  // /**
  //  * Cancel subscription
  //  * TODO: Backend needs POST /api/v1/payments/subscription/cancel
  //  */
  // async cancelSubscription(): Promise<void> {
  //   await apiClient.post('/api/v1/payments/subscription/cancel');
  // }

  // /**
  //  * Update subscription plan
  //  * TODO: Backend needs POST /api/v1/payments/subscription/update
  //  */
  // async updateSubscription(planId: PlanId): Promise<SubscriptionStatus> {
  //   const { data } = await apiClient.post<SubscriptionStatus>('/api/v1/payments/subscription/update', {
  //     plan_id: planId,
  //   });
  //   return data;
  // }
}

// Suppress unused import warnings until methods are re-enabled
void (null as unknown as CheckoutSessionRequest);
void (null as unknown as CheckoutSessionResponse);
void (null as unknown as SubscriptionStatus);
void (null as unknown as PlanId);

export const paymentService = new PaymentService();
export type { PaymentService };
