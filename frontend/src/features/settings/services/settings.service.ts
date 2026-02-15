/**
 * Settings Service
 * Handles API calls for user profile, subscription, and billing management
 */

import { apiClient } from '@/services/api/client';
import type {
  UserProfile,
  ProfileFormData,
  SubscriptionInfo,
  PaymentTransaction,
  SubscriptionTier,
  PaymentStatus,
} from '../types';

/**
 * API response types
 */
interface UserProfileResponse {
  id: string;
  email: string;
  subscription_tier: SubscriptionTier;
  stripe_customer_id?: string;
  onboarding_completed: boolean;
  created_at?: string;
  updated_at?: string;
}

interface SubscriptionResponse {
  tier: SubscriptionTier;
  status: 'active' | 'canceled' | 'past_due' | 'trialing';
  current_period_end?: string;
  cancel_at_period_end?: boolean;
}

interface PaymentTransactionResponse {
  id: string;
  user_id: string;
  stripe_payment_intent_id: string;
  amount: number;
  subscription_tier: SubscriptionTier;
  status: PaymentStatus;
  created_at?: string;
}

/**
 * Transform API response to frontend model
 */
const transformProfile = (data: UserProfileResponse): UserProfile => ({
  id: data.id,
  email: data.email,
  subscriptionTier: data.subscription_tier,
  stripeCustomerId: data.stripe_customer_id,
  onboardingCompleted: data.onboarding_completed,
  createdAt: data.created_at,
  updatedAt: data.updated_at,
});

const transformSubscription = (data: SubscriptionResponse): SubscriptionInfo => ({
  tier: data.tier,
  status: data.status,
  currentPeriodEnd: data.current_period_end,
  cancelAtPeriodEnd: data.cancel_at_period_end,
});

const transformTransaction = (data: PaymentTransactionResponse): PaymentTransaction => ({
  id: data.id,
  userId: data.user_id,
  stripePaymentIntentId: data.stripe_payment_intent_id,
  amount: data.amount,
  subscriptionTier: data.subscription_tier,
  status: data.status,
  createdAt: data.created_at,
});

class SettingsService {
  private userUrl = '/api/v1/users/me';
  private subscriptionUrl = '/api/v1/payments/subscription';
  private billingUrl = '/api/v1/payments/transactions';

  /**
   * Get current user profile
   */
  async getProfile(): Promise<UserProfile | null> {
    try {
      const response = await apiClient.get<UserProfileResponse>(this.userUrl);
      return transformProfile(response.data);
    } catch (error: unknown) {
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { status?: number } };
        if (axiosError.response?.status === 404) {
          return null;
        }
      }
      throw error;
    }
  }

  /**
   * Update user profile (email)
   */
  async updateProfile(data: Partial<ProfileFormData>): Promise<UserProfile> {
    const payload: Record<string, unknown> = {};
    if (data.email !== undefined) payload.email = data.email;

    const response = await apiClient.put<UserProfileResponse>(this.userUrl, payload);
    return transformProfile(response.data);
  }

  /**
   * Change user password
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.post(`${this.userUrl}/change-password`, {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  /**
   * Get current subscription info
   */
  async getSubscription(): Promise<SubscriptionInfo | null> {
    try {
      const response = await apiClient.get<SubscriptionResponse>(this.subscriptionUrl);
      return transformSubscription(response.data);
    } catch {
      return null;
    }
  }

  /**
   * Get billing history (payment transactions)
   */
  async getBillingHistory(): Promise<PaymentTransaction[]> {
    try {
      const response = await apiClient.get<PaymentTransactionResponse[]>(this.billingUrl);
      const list = Array.isArray(response.data) ? response.data : [];
      return list.map(transformTransaction);
    } catch {
      return [];
    }
  }

  /**
   * Get Stripe customer portal URL for managing payment methods
   */
  async getCustomerPortalUrl(): Promise<{ url: string }> {
    const response = await apiClient.post<{ url: string }>(
      '/api/v1/payments/customer-portal'
    );
    return response.data;
  }

  /**
   * Cancel subscription
   */
  async cancelSubscription(): Promise<void> {
    await apiClient.post(`${this.subscriptionUrl}/cancel`);
  }

  /**
   * Resume canceled subscription
   */
  async resumeSubscription(): Promise<void> {
    await apiClient.post(`${this.subscriptionUrl}/resume`);
  }

  /**
   * Delete user account
   */
  async deleteAccount(): Promise<void> {
    await apiClient.delete(this.userUrl);
  }
}

export const settingsService = new SettingsService();
export type { SettingsService };
