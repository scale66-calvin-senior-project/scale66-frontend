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

  // Send all authenticated users to dashboard
  return '/dashboard';

  // Default fallback
  return '/dashboard';
}

