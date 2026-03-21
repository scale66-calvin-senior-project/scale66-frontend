'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { BrandKit, SocialMediaAccount } from '@/features/brand-kit/types';
import { brandKitService } from '@/features/brand-kit/services';

interface BrandContextType {
  brandKit: BrandKit | null;
  socialAccounts: SocialMediaAccount[];
  isLoading: boolean;
  error: string | null;
  refreshBrandKit: () => Promise<void>;
}

const BrandContext = createContext<BrandContextType | null>(null);

/**
 * BrandProvider
 * Provides global brand kit state across the application
 */
export const BrandProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [brandKit, setBrandKit] = useState<BrandKit | null>(null);
  const [socialAccounts, setSocialAccounts] = useState<SocialMediaAccount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
      setError('Failed to load brand kit');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBrandKit();
  }, [loadBrandKit]);

  const value: BrandContextType = {
    brandKit,
    socialAccounts,
    isLoading,
    error,
    refreshBrandKit: loadBrandKit,
  };

  return <BrandContext.Provider value={value}>{children}</BrandContext.Provider>;
};

export const useBrandContext = () => {
  const context = useContext(BrandContext);
  if (!context) {
    throw new Error('useBrandContext must be used within BrandProvider');
  }
  return context;
};

export default BrandContext;
