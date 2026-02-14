/**
 * Onboarding Service
 * Handles saving onboarding data to localStorage and backend API
 */

import { apiClient } from '@/services/api/client';
import type { OnboardingData } from '../types';

const ONBOARDING_STORAGE_KEY = 'scale66_onboarding_data';

export interface BrandKitData {
  brand_name: string;
  brand_niche?: string;
  brand_style?: string;
  customer_pain_points?: string[]; // Backend expects array
  product_service_description?: string;
}

export const onboardingService = {
  /**
   * Sanitize data to remove non-serializable values (React elements, DOM nodes, etc.)
   */
  private sanitizeData(data: unknown): unknown {
    if (data === null || data === undefined) {
      return data;
    }
    
    // Handle primitives
    if (typeof data === 'string' || typeof data === 'number' || typeof data === 'boolean') {
      return data;
    }
    
    // Handle arrays
    if (Array.isArray(data)) {
      return data.map(item => this.sanitizeData(item));
    }
    
    // Handle objects - but skip if it's a DOM node or React element
    if (typeof data === 'object') {
      // Skip DOM nodes and React elements
      if (data instanceof HTMLElement || data instanceof Element || data instanceof Node) {
        return undefined;
      }
      
      // Check for React elements (they have $$typeof property)
      if ('$$typeof' in data || '__reactFiber' in data || 'stateNode' in data) {
        return undefined;
      }
      
      // Handle plain objects
      const sanitized: Record<string, unknown> = {};
      for (const [key, value] of Object.entries(data)) {
        // Skip React internal properties
        if (key.startsWith('__react') || key.startsWith('$$')) {
          continue;
        }
        const sanitizedValue = this.sanitizeData(value);
        if (sanitizedValue !== undefined) {
          sanitized[key] = sanitizedValue;
        }
      }
      return sanitized;
    }
    
    // For anything else, return undefined (don't save)
    return undefined;
  },

  /**
   * Save onboarding data to localStorage
   * This is called on each step to persist data locally
   */
  saveToLocalStorage(data: Partial<OnboardingData>): void {
    try {
      const existingData = this.loadFromLocalStorage();
      const mergedData = { ...existingData, ...data };
      
      // Sanitize data before saving to remove any non-serializable values
      const sanitized = this.sanitizeData(mergedData) as Partial<OnboardingData>;
      
      localStorage.setItem(ONBOARDING_STORAGE_KEY, JSON.stringify(sanitized));
      console.log('💾 Saved to localStorage:', sanitized);
    } catch (error) {
      console.error('❌ Error saving to localStorage:', error);
      // Don't throw - localStorage might not be available
    }
  },

  /**
   * Load onboarding data from localStorage
   */
  loadFromLocalStorage(): Partial<OnboardingData> {
    try {
      const stored = localStorage.getItem(ONBOARDING_STORAGE_KEY);
      if (stored) {
        const data = JSON.parse(stored) as Partial<OnboardingData>;
        console.log('📂 Loaded from localStorage:', data);
        return data;
      }
    } catch (error) {
      console.error('❌ Error loading from localStorage:', error);
    }
    return {};
  },

  /**
   * Clear onboarding data from localStorage
   */
  clearLocalStorage(): void {
    try {
      localStorage.removeItem(ONBOARDING_STORAGE_KEY);
      console.log('🗑️ Cleared localStorage');
    } catch (error) {
      console.error('❌ Error clearing localStorage:', error);
    }
  },

  /**
   * Save or update brand kit data for the current user
   * Uses backend API to create or update the brand kit
   * This is only called once at the end of onboarding
   */
  async saveBrandKit(data: Partial<OnboardingData>): Promise<void> {
    console.log('🚀 saveBrandKit called with data:', data);
    
    // Validate we have at least some data
    if (!data || Object.keys(data).length === 0) {
      console.warn('⚠️ No onboarding data provided to saveBrandKit');
      return; // Don't throw - might be called with empty data
    }
    
    try {
      // Prepare the data for backend API
      const brandKitData: Partial<BrandKitData> = {};
      
      if (data.brandName) {
        const trimmedName = data.brandName.trim();
        if (trimmedName) {
          brandKitData.brand_name = trimmedName;
          console.log('📝 Brand name to save:', brandKitData.brand_name);
        }
      }
      
      if (data.brandNiche) {
        brandKitData.brand_niche = data.brandNiche.trim();
      }
      
      if (data.brandStyle) {
        brandKitData.brand_style = data.brandStyle.trim();
      }
      
      // Handle customer pain points - convert to array
      if (data.customerPainPoints) {
        if (Array.isArray(data.customerPainPoints)) {
          brandKitData.customer_pain_points = data.customerPainPoints
            .map(p => typeof p === 'string' ? p.trim() : String(p).trim())
            .filter(p => p.length > 0);
        } else if (typeof data.customerPainPoints === 'string') {
          // Split by newlines and filter empty
          brandKitData.customer_pain_points = data.customerPainPoints
            .split('\n')
            .map(p => p.trim())
            .filter(p => p.length > 0);
        }
      }
      
      if (data.productService) {
        brandKitData.product_service_description = data.productService.trim();
      }
      
      // Validate required data - brand name is required
      if (!brandKitData.brand_name) {
        console.warn('⚠️ Brand name is required but not provided');
        throw new Error('Brand name is required to save brand kit');
      }
      
      console.log('💾 Saving brand kit via API:', brandKitData);
      
      // Check if brand kit exists first
      try {
        const { data: existingKit } = await apiClient.get('/api/v1/brand-kits/me');
        
        // Update existing brand kit
        console.log('🔄 Updating existing brand kit:', existingKit.id);
        const { data: updatedKit } = await apiClient.put('/api/v1/brand-kits/me', brandKitData);
        console.log('✅ Brand kit updated successfully:', updatedKit);
      } catch (error: unknown) {
        // If 404, create new brand kit
        if (error && typeof error === 'object' && 'response' in error) {
          const axiosError = error as { response?: { status?: number } };
          if (axiosError.response?.status === 404) {
            console.log('🆕 Creating new brand kit');
            const { data: createdKit } = await apiClient.post('/api/v1/brand-kits', brandKitData);
            console.log('✅ Brand kit created successfully:', createdKit);
          } else {
            console.error('❌ Error checking/updating brand kit:', axiosError);
            throw error;
          }
        } else {
          console.error('❌ Unexpected error:', error);
          throw error;
        }
      }
    } catch (error) {
      console.error('❌ Error saving brand kit:', error);
      // Re-throw to ensure the caller knows it failed
      throw error;
    }
  },

  /**
   * Save all onboarding data to backend and mark as complete
   * This is called once at the end of onboarding
   */
  async saveAndCompleteOnboarding(data: Partial<OnboardingData>): Promise<void> {
    try {
      console.log('🚀 Saving all onboarding data to backend...', data);
      
      // First, save the brand kit
      await this.saveBrandKit(data);
      
      // Then mark onboarding as complete
      await apiClient.put('/api/v1/users/me', {
        onboarding_completed: true,
      });
      
      console.log('✅ Onboarding saved and marked as complete');
      
      // Clear localStorage after successful save
      this.clearLocalStorage();
    } catch (error) {
      console.error('❌ Error saving onboarding:', error);
      throw error;
    }
  },

  /**
   * Mark onboarding as complete (without saving brand kit)
   * Used if brand kit was already saved separately
   */
  async markOnboardingComplete(): Promise<void> {
    try {
      await apiClient.put('/api/v1/users/me', {
        onboarding_completed: true,
      });
      console.log('✅ Onboarding marked as complete');
      
      // Clear localStorage after successful completion
      this.clearLocalStorage();
    } catch (error) {
      console.error('❌ Error marking onboarding as complete:', error);
      throw error;
    }
  },
};
