/**
 * Payment Types
 */

export type PlanId = 'starter' | 'growth' | 'agency';

export interface PaymentPlan {
  id: PlanId;
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  popular?: boolean;
  borderColor: string;
  buttonGradient: string;
  buttonTextColor?: string;
}

export interface CheckoutSessionRequest {
  planId: PlanId;
  successUrl?: string;
  cancelUrl?: string;
}

export interface CheckoutSessionResponse {
  sessionId: string;
  url?: string;
}

export interface SubscriptionStatus {
  isActive: boolean;
  planId?: PlanId;
  currentPeriodEnd?: string;
  cancelAtPeriodEnd?: boolean;
}
