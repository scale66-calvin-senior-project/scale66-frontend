/**
 * Dashboard Service
 * Handles dashboard-related operations via backend API
 */

import { apiClient } from '@/services/api/client';
import { campaignsService } from '@/features/campaigns/services/campaigns.service';
import { brandKitService } from '@/features/brand-kit/services/brand-kit.service';

export interface DashboardStats {
  totalCampaigns: number;
  totalPosts: number;
  recentCampaigns: Array<{
    id: string;
    campaign_name: string;
    created_at: string;
  }>;
}

export const dashboardService = {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<DashboardStats> {
    // Fetch campaigns to get stats
    const campaigns = await campaignsService.getCampaigns(10, 0);
    
    // Count total campaigns
    const totalCampaigns = campaigns.length;
    
    // Get recent campaigns
    const recentCampaigns = campaigns.slice(0, 5).map(c => ({
      id: c.id,
      campaign_name: c.campaign_name,
      created_at: c.created_at,
    }));
    
    // TODO: Add endpoint to get total posts count
    // For now, we'll estimate based on campaigns
    const totalPosts = 0; // Will be calculated when we have posts endpoint
    
    return {
      totalCampaigns,
      totalPosts,
      recentCampaigns,
    };
  },

  /**
   * Get user's brand kit (for dashboard display)
   */
  async getBrandKit() {
    try {
      return await brandKitService.getBrandKit();
    } catch (error) {
      // Brand kit might not exist yet
      return null;
    }
  },
};
