/**
 * Settings Types
 * Based on database schema for Users and PaymentTransactions tables
 */

/**
 * Subscription tier options matching backend/database enum
 */
export type SubscriptionTier = 'free' | 'starter' | 'growth' | 'agency';

/**
 * Payment status matching database enum
 */
export type PaymentStatus = 'pending' | 'succeeded' | 'failed' | 'refunded';

/**
 * User profile data from Users table
 */
export interface UserProfile {
  id: string;
  email: string;
  subscriptionTier: SubscriptionTier;
  stripeCustomerId?: string;
  onboardingCompleted: boolean;
  createdAt?: string;
  updatedAt?: string;
}

/**
 * Form data for updating profile
 */
export interface ProfileFormData {
  email?: string;
  currentPassword?: string;
  newPassword?: string;
  confirmPassword?: string;
}

/**
 * Payment transaction from PaymentTransactions table
 */
export interface PaymentTransaction {
  id: string;
  userId: string;
  stripePaymentIntentId: string;
  amount: number;
  subscriptionTier: SubscriptionTier;
  status: PaymentStatus;
  createdAt?: string;
}

/**
 * Subscription info for display
 */
export interface SubscriptionInfo {
  tier: SubscriptionTier;
  status: 'active' | 'canceled' | 'past_due' | 'trialing';
  currentPeriodEnd?: string;
  cancelAtPeriodEnd?: boolean;
}

/**
 * Settings state for hook
 */
export interface SettingsState {
  profile: UserProfile | null;
  subscription: SubscriptionInfo | null;
  billingHistory: PaymentTransaction[];
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
}

/**
 * Subscription tier display info
 */
export interface SubscriptionTierInfo {
  tier: SubscriptionTier;
  name: string;
  price: number;
  interval: 'month' | 'year';
  features: string[];
}

/**
 * Available subscription tiers (tier values match backend)
 */
export const SUBSCRIPTION_TIERS: SubscriptionTierInfo[] = [
  {
    tier: 'free',
    name: 'Free',
    price: 0,
    interval: 'month',
    features: ['Limited carousel generation', 'Basic templates'],
  },
  {
    tier: 'starter',
    name: 'Starter',
    price: 19,
    interval: 'month',
    features: ['50 carousels/month', 'All templates', 'Direct posting'],
  },
  {
    tier: 'growth',
    name: 'Growth',
    price: 49,
    interval: 'month',
    features: ['Unlimited carousels', 'Priority support', 'Advanced analytics'],
  },
  {
    tier: 'agency',
    name: 'Agency',
    price: 99,
    interval: 'month',
    features: ['Everything in Growth', 'Team collaboration', 'Custom branding'],
  },
];
