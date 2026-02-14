/**
 * Brand Kit Service
 * Handles brand kit operations via backend API
 */

import { apiClient } from '@/services/api/client';

export interface BrandKit {
  id: string;
  user_id: string;
  brand_name: string;
  brand_niche?: string;
  brand_style?: string;
  customer_pain_points?: string[];
  product_service_description?: string;
  created_at: string;
  updated_at: string;
}

export interface BrandKitUpdate {
  brand_name?: string;
  brand_niche?: string;
  brand_style?: string;
  customer_pain_points?: string[];
  product_service_description?: string;
}

export const brandKitService = {
  /**
   * Get current user's brand kit
   */
  async getBrandKit(): Promise<BrandKit> {
    const { data } = await apiClient.get<BrandKit>('/api/v1/brand-kits/me');
    return data;
  },

  /**
   * Update current user's brand kit
   */
  async updateBrandKit(updates: BrandKitUpdate): Promise<BrandKit> {
    const { data } = await apiClient.put<BrandKit>('/api/v1/brand-kits/me', updates);
    return data;
  },
};
