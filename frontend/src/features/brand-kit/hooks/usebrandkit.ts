/**
 * useBrandKit Hook
 * Manages brand kit state and operations
 */

import { useState, useEffect, useCallback } from 'react';
import { brandKitService } from '../services';
import type { BrandKit, BrandKitFormData, SocialMediaAccount, SocialPlatform } from '../types';

interface UseBrandKitReturn {
  brandKit: BrandKit | null;
  socialAccounts: SocialMediaAccount[];
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  loadBrandKit: () => Promise<void>;
  saveBrandKit: (data: BrandKitFormData) => Promise<BrandKit | null>;
  updateField: (field: keyof BrandKitFormData, value: string) => Promise<void>;
  deleteBrandKit: () => Promise<void>;
  connectSocialAccount: (platform: SocialPlatform) => Promise<void>;
  disconnectSocialAccount: (accountId: string) => Promise<void>;
  clearError: () => void;
}

/**
 * Hook for managing brand kit data and social account connections
 */
export const useBrandKit = (): UseBrandKitReturn => {
  const [brandKit, setBrandKit] = useState<BrandKit | null>(null);
  const [socialAccounts, setSocialAccounts] = useState<SocialMediaAccount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load brand kit and social accounts
   */
  const loadBrandKit = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [kit, accounts] = await Promise.all([
        brandKitService.getBrandKit(),
        brandKitService.getSocialAccounts(),
      ]);

      setBrandKit(kit);
      setSocialAccounts(accounts);
    } catch (err) {
      console.error('Error loading brand kit:', err);
      setError('Failed to load brand kit. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Save brand kit (create or update)
   */
  const saveBrandKit = useCallback(async (data: BrandKitFormData): Promise<BrandKit | null> => {
    setIsSaving(true);
    setError(null);

    try {
      let result: BrandKit;
      
      if (brandKit) {
        result = await brandKitService.updateBrandKit(data);
      } else {
        result = await brandKitService.createBrandKit(data);
      }

      setBrandKit(result);
      return result;
    } catch (err) {
      console.error('Error saving brand kit:', err);
      setError('Failed to save brand kit. Please try again.');
      return null;
    } finally {
      setIsSaving(false);
    }
  }, [brandKit]);

  /**
   * Update a single field with auto-save
   */
  const updateField = useCallback(async (
    field: keyof BrandKitFormData,
    value: string
  ): Promise<void> => {
    if (!brandKit) return;

    setIsSaving(true);
    setError(null);

    try {
      const result = await brandKitService.updateBrandKit({ [field]: value });
      setBrandKit(result);
    } catch (err) {
      console.error('Error updating field:', err);
      setError('Failed to save changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  }, [brandKit]);

  /**
   * Delete brand kit
   */
  const deleteBrandKit = useCallback(async (): Promise<void> => {
    if (!brandKit) return;

    setIsSaving(true);
    setError(null);

    try {
      await brandKitService.deleteBrandKit();
      setBrandKit(null);
    } catch (err) {
      console.error('Error deleting brand kit:', err);
      setError('Failed to delete brand kit. Please try again.');
    } finally {
      setIsSaving(false);
    }
  }, [brandKit]);

  /**
   * Connect social account via OAuth
   */
  const connectSocialAccount = useCallback(async (platform: SocialPlatform): Promise<void> => {
    setError(null);

    try {
      const { authUrl } = await brandKitService.connectSocialAccount(platform);
      // Redirect to OAuth provider
      window.location.href = authUrl;
    } catch (err) {
      console.error('Error connecting social account:', err);
      setError(`Failed to connect ${platform}. Please try again.`);
    }
  }, []);

  /**
   * Disconnect social account
   */
  const disconnectSocialAccount = useCallback(async (accountId: string): Promise<void> => {
    setError(null);

    try {
      await brandKitService.disconnectSocialAccount(accountId);
      setSocialAccounts(prev => prev.filter(acc => acc.id !== accountId));
    } catch (err) {
      console.error('Error disconnecting social account:', err);
      setError('Failed to disconnect account. Please try again.');
    }
  }, []);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Load data on mount
  useEffect(() => {
    loadBrandKit();
  }, [loadBrandKit]);

  return {
    brandKit,
    socialAccounts,
    isLoading,
    isSaving,
    error,
    loadBrandKit,
    saveBrandKit,
    updateField,
    deleteBrandKit,
    connectSocialAccount,
    disconnectSocialAccount,
    clearError,
  };
};
