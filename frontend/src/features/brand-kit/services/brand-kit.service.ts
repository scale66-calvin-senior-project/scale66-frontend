/**
 * Brand Kit Service
 * Handles API calls for brand kit and social media account management
 */

import { apiClient } from '@/services/api/client';
import type { BrandKit, BrandKitFormData, SocialMediaAccount, SocialPlatform } from '../types';

/**
 * API response types
 */
interface BrandKitResponse {
  id: string;
  user_id: string;
  brand_name?: string;
  brand_niche?: string;
  brand_style?: string;
  customer_pain_points?: string;
  product_service_description: string;
  created_at?: string;
  updated_at?: string;
}

interface SocialAccountResponse {
  id: string;
  user_id: string;
  platform: SocialPlatform;
  platform_user_id: string;
  is_active: boolean;
  username?: string;
  profile_url?: string;
}

/**
 * Transform API response to frontend model
 */
const transformBrandKit = (data: BrandKitResponse): BrandKit => ({
  id: data.id,
  userId: data.user_id,
  brandName: data.brand_name,
  brandNiche: data.brand_niche,
  brandStyle: data.brand_style as BrandKit['brandStyle'],
  customerPainPoints: data.customer_pain_points,
  productServiceDescription: data.product_service_description,
  createdAt: data.created_at,
  updatedAt: data.updated_at,
});

/**
 * Transform social account API response
 */
const transformSocialAccount = (data: SocialAccountResponse): SocialMediaAccount => ({
  id: data.id,
  userId: data.user_id,
  platform: data.platform,
  platformUserId: data.platform_user_id,
  isActive: data.is_active,
  username: data.username,
  profileUrl: data.profile_url,
});

class BrandKitService {
  private baseUrl = '/api/v1/brand-kit';
  private socialUrl = '/api/v1/social-accounts';

  /**
   * Get current user's brand kit
   */
  async getBrandKit(): Promise<BrandKit | null> {
    try {
      const response = await apiClient.get<BrandKitResponse>(this.baseUrl);
      return transformBrandKit(response.data);
    } catch (error: unknown) {
      // Return null if no brand kit exists yet
      if (error && typeof error === 'object' && 'response' in error) {
        const axiosError = error as { response?: { status?: number } };
        if (axiosError.response?.status === 404) {
          return null;
        }
      }
      throw error;
    }
  }

  /**
   * Create a new brand kit
   */
  async createBrandKit(data: BrandKitFormData): Promise<BrandKit> {
    const payload = {
      brand_name: data.brandName,
      brand_niche: data.brandNiche,
      brand_style: data.brandStyle,
      customer_pain_points: data.customerPainPoints,
      product_service_description: data.productServiceDescription,
    };

    const response = await apiClient.post<BrandKitResponse>(this.baseUrl, payload);
    return transformBrandKit(response.data);
  }

  /**
   * Update existing brand kit
   */
  async updateBrandKit(data: Partial<BrandKitFormData>): Promise<BrandKit> {
    const payload: Record<string, unknown> = {};
    
    if (data.brandName !== undefined) payload.brand_name = data.brandName;
    if (data.brandNiche !== undefined) payload.brand_niche = data.brandNiche;
    if (data.brandStyle !== undefined) payload.brand_style = data.brandStyle;
    if (data.customerPainPoints !== undefined) payload.customer_pain_points = data.customerPainPoints;
    if (data.productServiceDescription !== undefined) {
      payload.product_service_description = data.productServiceDescription;
    }

    const response = await apiClient.patch<BrandKitResponse>(this.baseUrl, payload);
    return transformBrandKit(response.data);
  }

  /**
   * Delete brand kit
   */
  async deleteBrandKit(): Promise<void> {
    await apiClient.delete(this.baseUrl);
  }

  /**
   * Get connected social media accounts
   */
  async getSocialAccounts(): Promise<SocialMediaAccount[]> {
    try {
      const response = await apiClient.get<SocialAccountResponse[]>(this.socialUrl);
      return response.data.map(transformSocialAccount);
    } catch {
      return [];
    }
  }

  /**
   * Initiate OAuth flow for social platform connection
   * Returns the OAuth URL to redirect the user to
   */
  async connectSocialAccount(platform: SocialPlatform): Promise<{ authUrl: string }> {
    const response = await apiClient.post<{ auth_url: string }>(
      `${this.socialUrl}/connect/${platform}`
    );
    return { authUrl: response.data.auth_url };
  }

  /**
   * Disconnect a social media account
   */
  async disconnectSocialAccount(accountId: string): Promise<void> {
    await apiClient.delete(`${this.socialUrl}/${accountId}`);
  }

  /**
   * Toggle social account active status
   */
  async toggleSocialAccountStatus(accountId: string, isActive: boolean): Promise<SocialMediaAccount> {
    const response = await apiClient.patch<SocialAccountResponse>(
      `${this.socialUrl}/${accountId}`,
      { is_active: isActive }
    );
    return transformSocialAccount(response.data);
  }
}

export const brandKitService = new BrandKitService();
export type { BrandKitService };
