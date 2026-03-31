/**
 * useSettings Hook
 * Manages user settings, profile, and subscription state
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthContext } from '@/context/AuthContext';
import { settingsService } from '../services';
import type {
  UserProfile,
  ProfileFormData,
  SubscriptionInfo,
  PaymentTransaction,
} from '../types';

interface UseSettingsReturn {
  profile: UserProfile | null;
  subscription: SubscriptionInfo | null;
  billingHistory: PaymentTransaction[];
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  loadSettings: () => Promise<void>;
  updateProfile: (data: Partial<ProfileFormData>) => Promise<boolean>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<boolean>;
  openCustomerPortal: () => Promise<void>;
  cancelSubscription: () => Promise<boolean>;
  resumeSubscription: () => Promise<boolean>;
  deleteAccount: () => Promise<boolean>;
  signOut: () => Promise<void>;
  clearError: () => void;
}

const NOT_IMPLEMENTED = 'This feature is not yet available. Please check back soon.';

export const useSettings = (): UseSettingsReturn => {
  const router = useRouter();
  const { logout } = useAuthContext();

  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null);
  const [billingHistory, setBillingHistory] = useState<PaymentTransaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSettings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    // Safety net: never stay in loading state longer than 12 seconds
    const safetyTimer = setTimeout(() => setIsLoading(false), 12000);
    try {
      const [profileData, historyData] = await Promise.all([
        settingsService.getProfile(),
        settingsService.getBillingHistory(),
      ]);
      setProfile(profileData);
      // Derive minimal subscription info from user profile until backend implements the endpoint
      setSubscription(
        profileData ? { tier: profileData.subscriptionTier, status: 'active' as const } : null
      );
      setBillingHistory(historyData);
    } catch (err) {
      console.error('Error loading settings:', err);
      setError('Failed to load settings. Please try again.');
    } finally {
      clearTimeout(safetyTimer);
      setIsLoading(false);
    }
  }, []);

  // TODO: Backend needs PUT /api/v1/users/me to accept email updates.
  //       Email/profile changes should go through Supabase Auth updateUser() for now.
  const updateProfile = useCallback(async (_data: Partial<ProfileFormData>): Promise<boolean> => {
    setError(NOT_IMPLEMENTED);
    return false;
  }, []);

  // TODO: Backend needs POST /api/v1/users/me/change-password.
  //       Use Supabase Auth updateUser({ password }) instead.
  const changePassword = useCallback(async (_currentPassword: string, _newPassword: string): Promise<boolean> => {
    setError(NOT_IMPLEMENTED);
    return false;
  }, []);

  // TODO: Backend needs POST /api/v1/payments/customer-portal
  const openCustomerPortal = useCallback(async (): Promise<void> => {
    setError(NOT_IMPLEMENTED);
  }, []);

  // TODO: Backend needs POST /api/v1/payments/subscription/cancel
  const cancelSubscription = useCallback(async (): Promise<boolean> => {
    setError(NOT_IMPLEMENTED);
    return false;
  }, []);

  // TODO: Backend needs POST /api/v1/payments/subscription/resume
  const resumeSubscription = useCallback(async (): Promise<boolean> => {
    setError(NOT_IMPLEMENTED);
    return false;
  }, []);

  // TODO: Backend needs DELETE /api/v1/users/me
  const deleteAccount = useCallback(async (): Promise<boolean> => {
    setError(NOT_IMPLEMENTED);
    return false;
  }, []);

  const signOut = useCallback(async (): Promise<void> => {
    try {
      await logout();
      router.push('/login');
    } catch (err) {
      console.error('Error signing out:', err);
      setError('Failed to sign out. Please try again.');
    }
  }, [logout, router]);

  const clearError = useCallback(() => setError(null), []);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  return {
    profile,
    subscription,
    billingHistory,
    isLoading,
    isSaving,
    error,
    loadSettings,
    updateProfile,
    changePassword,
    openCustomerPortal,
    cancelSubscription,
    resumeSubscription,
    deleteAccount,
    signOut,
    clearError,
  };
};
