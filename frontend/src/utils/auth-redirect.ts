/**
 * Auth Redirect Utility
 * Determines where to redirect users after login based on their onboarding and subscription status
 */

import type { User } from '@/features/auth/types';

/**
 * Determines the appropriate redirect path after login
 * 
 * @param user - User object with onboarding_completed and subscription_tier
 * @returns Redirect path
 */
export function getPostLoginRedirectPath(user: User | null): string {
  if (!user) {
    return '/login';
  }

  // If onboarding not completed, send to onboarding
  if (!user.onboarding_completed) {
    return '/welcome';
  }

  // If onboarding completed but not paid (free tier), send to paywall
  if (user.onboarding_completed && (!user.subscription_tier || user.subscription_tier === 'free')) {
    return '/welcome?step=7';
  }

  // If onboarding completed and paid (pro or premium), send to dashboard
  if (user.onboarding_completed && (user.subscription_tier === 'pro' || user.subscription_tier === 'premium')) {
    return '/dashboard';
  }

  // Default fallback
  return '/dashboard';
}

