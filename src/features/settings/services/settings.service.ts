/**
 * Settings Service
 * Handles API calls for user profile, subscription, and billing management
 *
 * Backend endpoints available:
 *   GET /api/v1/users/me                   — get user profile
 *   PUT /api/v1/users/me                   — update subscription_tier or onboarding_completed only
 *   GET /api/v1/payments/transactions      — billing history
 *
 * Endpoints commented out below are not yet implemented in the backend.
 */

import { apiClient } from '@/services/api/client';
import type {
  UserProfile,
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

const transformTransaction = (data: PaymentTransactionResponse): PaymentTransaction => ({
  id: data.id,
  userId: data.user_id,
  stripePaymentIntentId: data.stripe_payment_intent_id,
  amount: data.amount,
  subscriptionTier: data.subscription_tier,
  status: data.status,
  createdAt: data.created_at,
});

// Suppress unused type warning until subscription endpoints are re-enabled
void (null as unknown as SubscriptionInfo);

class SettingsService {
  private userUrl = '/api/v1/users/me';
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

  // /**
  //  * Update user profile (email)
  //  * TODO: Backend PUT /api/v1/users/me only accepts subscription_tier and onboarding_completed.
  //  *       Email changes must go through Supabase Auth — no backend endpoint exists for this.
  //  */
  // async updateProfile(data: Partial<ProfileFormData>): Promise<UserProfile> { ... }

  // /**
  //  * Change user password
  //  * TODO: Backend needs POST /api/v1/users/me/change-password
  //  *       Password changes should use Supabase Auth updateUser() instead.
  //  */
  // async changePassword(currentPassword: string, newPassword: string): Promise<void> { ... }

  // /**
  //  * Get current subscription info
  //  * TODO: Backend needs GET /api/v1/payments/subscription
  //  */
  // async getSubscription(): Promise<SubscriptionInfo | null> { ... }

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

  // /**
  //  * Get Stripe customer portal URL for managing payment methods
  //  * TODO: Backend needs POST /api/v1/payments/customer-portal
  //  */
  // async getCustomerPortalUrl(): Promise<{ url: string }> { ... }

  // /**
  //  * Cancel subscription
  //  * TODO: Backend needs POST /api/v1/payments/subscription/cancel
  //  */
  // async cancelSubscription(): Promise<void> { ... }

  // /**
  //  * Resume canceled subscription
  //  * TODO: Backend needs POST /api/v1/payments/subscription/resume
  //  */
  // async resumeSubscription(): Promise<void> { ... }

  // /**
  //  * Delete user account
  //  * TODO: Backend needs DELETE /api/v1/users/me
  //  */
  // async deleteAccount(): Promise<void> { ... }
}

export const settingsService = new SettingsService();
export type { SettingsService };
