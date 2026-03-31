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

export const useBrandKit = (): UseBrandKitReturn => {
  const [brandKit, setBrandKit] = useState<BrandKit | null>(null);
  const [socialAccounts, setSocialAccounts] = useState<SocialMediaAccount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadBrandKit = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    // Safety net: never stay in loading state longer than 12 seconds
    const safetyTimer = setTimeout(() => setIsLoading(false), 12000);
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
      clearTimeout(safetyTimer);
      setIsLoading(false);
    }
  }, []);

  const saveBrandKit = useCallback(async (data: BrandKitFormData): Promise<BrandKit | null> => {
    setIsSaving(true);
    setError(null);
    try {
      const result = brandKit
        ? await brandKitService.updateBrandKit(data)
        : await brandKitService.createBrandKit(data);
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

  const updateField = useCallback(
    async (field: keyof BrandKitFormData, value: string): Promise<void> => {
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
    },
    [brandKit]
  );

  // TODO: Backend needs DELETE /api/v1/brand-kits/me before this can be enabled.
  const deleteBrandKit = useCallback(async (): Promise<void> => {
    setError('Deleting the brand kit is not yet available.');
  }, []);

  // TODO: Backend needs POST /api/v1/social-accounts/connect/:platform (OAuth flow).
  const connectSocialAccount = useCallback(async (_platform: SocialPlatform): Promise<void> => {
    setError('Connecting social accounts is not yet available.');
  }, []);

  const disconnectSocialAccount = useCallback(async (accountId: string): Promise<void> => {
    setError(null);
    try {
      await brandKitService.disconnectSocialAccount(accountId);
      setSocialAccounts((prev) => prev.filter((acc) => acc.id !== accountId));
    } catch (err) {
      console.error('Error disconnecting social account:', err);
      setError('Failed to disconnect account. Please try again.');
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);

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
