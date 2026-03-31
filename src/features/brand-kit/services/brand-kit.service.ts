/**
 * Brand Kit Service
 * Handles API calls for brand kit and social media account management
 *
 * Backend endpoints:
 *   POST /api/v1/brand-kits        — create brand kit (BrandKitCreate)
 *   GET  /api/v1/brand-kits/me     — get user's brand kit (BrandKitResponse)
 *   PUT  /api/v1/brand-kits/me     — update brand kit (BrandKitUpdate)
 *
 *   GET    /api/v1/social-accounts           — list connected accounts
 *   PUT    /api/v1/social-accounts/:id       — update account (toggle active etc.)
 *   DELETE /api/v1/social-accounts/:id       — disconnect account
 */

import { apiClient } from '@/services/api/client';
import type { BrandKit, BrandKitFormData, SocialMediaAccount, SocialPlatform } from '../types';

// ── Backend response shapes (snake_case) ─────────────────────────────────────

interface BrandKitResponse {
  id: string;
  user_id: string;
  brand_name: string;
  brand_niche?: string | null;
  brand_style?: string | null;
  /** Backend stores as string[] (JSONB array) */
  customer_pain_points?: string[];
  product_service_description?: string | null;
  created_at: string;
  updated_at: string;
}

interface SocialAccountResponse {
  id: string;
  user_id: string;
  platform: SocialPlatform;
  platform_user_id: string;
  platform_username?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ── Transformers ──────────────────────────────────────────────────────────────

/**
 * Backend returns customer_pain_points as string[].
 * UI stores/displays them as a single newline-separated string.
 */
const transformBrandKit = (data: BrandKitResponse): BrandKit => ({
  id: data.id,
  userId: data.user_id,
  brandName: data.brand_name,
  brandNiche: data.brand_niche ?? undefined,
  brandStyle: (data.brand_style ?? undefined) as BrandKit['brandStyle'],
  customerPainPoints: Array.isArray(data.customer_pain_points)
    ? data.customer_pain_points.join('\n')
    : '',
  productServiceDescription: data.product_service_description ?? '',
  createdAt: data.created_at,
  updatedAt: data.updated_at,
});

const transformSocialAccount = (data: SocialAccountResponse): SocialMediaAccount => ({
  id: data.id,
  userId: data.user_id,
  platform: data.platform,
  platformUserId: data.platform_user_id,
  isActive: data.is_active,
  username: data.platform_username ?? undefined,
});

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Split a newline-separated UI string into the array the backend expects. */
const toPainPointsArray = (value: string | undefined): string[] => {
  if (!value) return [];
  return value.split('\n').map((p) => p.trim()).filter(Boolean);
};

// ── Service ───────────────────────────────────────────────────────────────────

class BrandKitService {
  private readonly baseUrl = '/api/v1/brand-kits';
  private readonly meUrl  = '/api/v1/brand-kits/me';
  private readonly socialUrl = '/api/v1/social-accounts';

  /** Fetch the current user's brand kit. Returns null if none exists yet. */
  async getBrandKit(): Promise<BrandKit | null> {
    try {
      const { data } = await apiClient.get<BrandKitResponse>(this.meUrl);
      return transformBrandKit(data);
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 404) return null;
      throw err;
    }
  }

  /**
   * Create a brand kit.
   * `brand_name` is required (min_length 1) — falls back to "My Brand" if blank.
   */
  async createBrandKit(data: BrandKitFormData): Promise<BrandKit> {
    const payload = {
      brand_name: data.brandName?.trim() || 'My Brand',
      brand_niche: data.brandNiche?.trim() || undefined,
      brand_style: data.brandStyle || undefined,
      customer_pain_points: toPainPointsArray(data.customerPainPoints),
      product_service_description: data.productServiceDescription?.trim() || undefined,
    };

    const { data: res } = await apiClient.post<BrandKitResponse>(this.baseUrl, payload);
    return transformBrandKit(res);
  }

  /**
   * Update the current user's brand kit.
   * Only sends fields that are explicitly provided (all fields are optional on update).
   * Skips brand_name if it would become empty (backend requires min_length 1).
   */
  async updateBrandKit(data: Partial<BrandKitFormData>): Promise<BrandKit> {
    const payload: Record<string, unknown> = {};

    if (data.brandName !== undefined) {
      const trimmed = data.brandName.trim();
      if (trimmed) payload.brand_name = trimmed;
      // skip empty — backend rejects brand_name with min_length=1
    }
    if (data.brandNiche !== undefined) {
      payload.brand_niche = data.brandNiche.trim() || null;
    }
    if (data.brandStyle !== undefined) {
      payload.brand_style = data.brandStyle || null;
    }
    if (data.customerPainPoints !== undefined) {
      payload.customer_pain_points = toPainPointsArray(data.customerPainPoints);
    }
    if (data.productServiceDescription !== undefined) {
      payload.product_service_description = data.productServiceDescription.trim() || null;
    }

    const { data: res } = await apiClient.put<BrandKitResponse>(this.meUrl, payload);
    return transformBrandKit(res);
  }

  // /**
  //  * Delete brand kit
  //  * TODO: Backend needs DELETE /api/v1/brand-kits/me
  //  */
  // async deleteBrandKit(): Promise<void> { ... }

  /** List connected social accounts for the current user. */
  async getSocialAccounts(): Promise<SocialMediaAccount[]> {
    try {
      const { data } = await apiClient.get<SocialAccountResponse[]>(this.socialUrl);
      return data.map(transformSocialAccount);
    } catch {
      return [];
    }
  }

  // /**
  //  * Initiate OAuth connect flow
  //  * TODO: Backend needs POST /api/v1/social-accounts/connect/:platform
  //  */
  // async connectSocialAccount(platform: SocialPlatform): Promise<{ authUrl: string }> { ... }

  /** Disconnect (soft-delete) a social account. */
  async disconnectSocialAccount(accountId: string): Promise<void> {
    await apiClient.delete(`${this.socialUrl}/${accountId}`);
  }

  /** Toggle a social account's active status. */
  async toggleSocialAccountStatus(accountId: string, isActive: boolean): Promise<SocialMediaAccount> {
    const { data } = await apiClient.put<SocialAccountResponse>(
      `${this.socialUrl}/${accountId}`,
      { is_active: isActive }
    );
    return transformSocialAccount(data);
  }
}

export const brandKitService = new BrandKitService();
export type { BrandKitService };
