/**
 * Campaigns Service
 * Handles campaign operations via backend API
 */

import { apiClient } from '@/services/api/client';

export interface Campaign {
  id: string;
  user_id: string;
  campaign_name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface CampaignCreate {
  campaign_name: string;
  description?: string;
}

export interface CampaignUpdate {
  campaign_name?: string;
  description?: string;
}

export const campaignsService = {
  /**
   * Get all campaigns for current user
   */
  async getCampaigns(limit = 100, offset = 0): Promise<Campaign[]> {
    try {
      const { data } = await apiClient.get<Campaign[]>('/api/v1/campaigns', {
        params: { limit, offset },
      });
      return data;
    } catch (err: unknown) {
      if ((err as { response?: { status?: number } })?.response?.status === 404) {
        return [];
      }
      throw err;
    }
  },

  /**
   * Get a specific campaign by ID
   */
  async getCampaign(campaignId: string): Promise<Campaign> {
    const { data } = await apiClient.get<Campaign>(`/api/v1/campaigns/${campaignId}`);
    return data;
  },

  /**
   * Create a new campaign
   */
  async createCampaign(campaignData: CampaignCreate): Promise<Campaign> {
    const { data } = await apiClient.post<Campaign>('/api/v1/campaigns', campaignData);
    return data;
  },

  /**
   * Update a campaign
   */
  async updateCampaign(campaignId: string, updates: CampaignUpdate): Promise<Campaign> {
    const { data } = await apiClient.put<Campaign>(`/api/v1/campaigns/${campaignId}`, updates);
    return data;
  },

  /**
   * Delete a campaign
   */
  async deleteCampaign(campaignId: string): Promise<void> {
    await apiClient.delete(`/api/v1/campaigns/${campaignId}`);
  },
};
