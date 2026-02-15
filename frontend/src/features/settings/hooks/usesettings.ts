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
    try {
      const [profileData, subscriptionData, historyData] = await Promise.all([
        settingsService.getProfile(),
        settingsService.getSubscription(),
        settingsService.getBillingHistory(),
      ]);
      setProfile(profileData);
      setSubscription(
        subscriptionData ??
          (profileData ? { tier: profileData.subscriptionTier, status: 'active' as const } : null)
      );
      setBillingHistory(historyData);
    } catch (err) {
      console.error('Error loading settings:', err);
      setError('Failed to load settings. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateProfile = useCallback(async (data: Partial<ProfileFormData>): Promise<boolean> => {
    setIsSaving(true);
    setError(null);
    try {
      const result = await settingsService.updateProfile(data);
      setProfile(result);
      return true;
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('Failed to update profile. Please try again.');
      return false;
    } finally {
      setIsSaving(false);
    }
  }, []);

  const changePassword = useCallback(async (currentPassword: string, newPassword: string): Promise<boolean> => {
    setIsSaving(true);
    setError(null);
    try {
      await settingsService.changePassword(currentPassword, newPassword);
      return true;
    } catch (err) {
      console.error('Error changing password:', err);
      setError('Failed to change password. Please check your current password.');
      return false;
    } finally {
      setIsSaving(false);
    }
  }, []);

  const openCustomerPortal = useCallback(async (): Promise<void> => {
    setError(null);
    try {
      const { url } = await settingsService.getCustomerPortalUrl();
      window.location.href = url;
    } catch (err) {
      console.error('Error opening customer portal:', err);
      setError('Failed to open billing portal. Please try again.');
    }
  }, []);

  const cancelSubscription = useCallback(async (): Promise<boolean> => {
    setIsSaving(true);
    setError(null);
    try {
      await settingsService.cancelSubscription();
      const subscriptionData = await settingsService.getSubscription();
      setSubscription(subscriptionData);
      return true;
    } catch (err) {
      console.error('Error canceling subscription:', err);
      setError('Failed to cancel subscription. Please try again.');
      return false;
    } finally {
      setIsSaving(false);
    }
  }, []);

  const resumeSubscription = useCallback(async (): Promise<boolean> => {
    setIsSaving(true);
    setError(null);
    try {
      await settingsService.resumeSubscription();
      const subscriptionData = await settingsService.getSubscription();
      setSubscription(subscriptionData);
      return true;
    } catch (err) {
      console.error('Error resuming subscription:', err);
      setError('Failed to resume subscription. Please try again.');
      return false;
    } finally {
      setIsSaving(false);
    }
  }, []);

  const deleteAccount = useCallback(async (): Promise<boolean> => {
    setIsSaving(true);
    setError(null);
    try {
      await settingsService.deleteAccount();
      return true;
    } catch (err) {
      console.error('Error deleting account:', err);
      setError('Failed to delete account. Please try again.');
      return false;
    } finally {
      setIsSaving(false);
    }
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
