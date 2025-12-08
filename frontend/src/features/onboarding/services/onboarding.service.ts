/**
 * Onboarding Service
 * Handles saving onboarding data to Supabase brand_kits table
 */

import { supabase } from '@/lib/supabase';
import type { OnboardingData } from '../types';

export interface BrandKitData {
  brand_name: string;
  brand_niche?: string;
  brand_style?: string;
  customer_pain_points?: string; // JSON stringified array
  product_service_description?: string;
}

export const onboardingService = {
  /**
   * Get current user's ID from Supabase session
   */
  async getCurrentUserId(): Promise<string> {
    const { data: { user }, error } = await supabase.auth.getUser();
    
    if (error || !user) {
      throw new Error('User not authenticated');
    }
    
    return user.id;
  },

  /**
   * Save or update brand kit data for the current user
   * Uses upsert to create or update the brand kit
   */
  async saveBrandKit(data: Partial<OnboardingData>): Promise<void> {
    try {
      const userId = await this.getCurrentUserId();
      
      // Prepare the data for Supabase
      const brandKitData: Partial<BrandKitData> = {};
      
      if (data.brandName) {
        brandKitData.brand_name = data.brandName;
      }
      
      if (data.brandNiche) {
        brandKitData.brand_niche = data.brandNiche;
      }
      
      if (data.brandStyle) {
        brandKitData.brand_style = data.brandStyle;
      }
      
      // Convert pain points array to JSON string if it's an array
      if (data.customerPainPoints) {
        if (Array.isArray(data.customerPainPoints)) {
          brandKitData.customer_pain_points = JSON.stringify(data.customerPainPoints);
        } else {
          // If it's a string, convert to array first
          const painPointsArray = data.customerPainPoints
            .split('\n')
            .map(p => p.trim())
            .filter(p => p.length > 0);
          brandKitData.customer_pain_points = JSON.stringify(painPointsArray);
        }
      }
      
      if (data.productService) {
        brandKitData.product_service_description = data.productService;
      }
      
      // Check if brand kit already exists for this user
      // First, try to find any existing brand kit for this user
      const { data: existingKits } = await supabase
        .from('brand_kits')
        .select('id, brand_name')
        .eq('user_id', userId)
        .limit(1);
      
      if (existingKits && existingKits.length > 0) {
        // Update existing brand kit (use the first one found)
        const existingKit = existingKits[0];
        
        // If brand_name is provided and different, we need to handle the unique constraint
        // For now, just update the existing one
        const { error } = await supabase
          .from('brand_kits')
          .update(brandKitData)
          .eq('id', existingKit.id)
          .eq('user_id', userId);
        
        if (error) {
          console.error('Error updating brand kit:', error);
          throw new Error(`Failed to update brand kit: ${error.message}`);
        }
      } else {
        // Create new brand kit (requires brand_name)
        if (!brandKitData.brand_name) {
          console.warn('Cannot create brand kit without brand_name, skipping save');
          return;
        }
        
        const { error } = await supabase
          .from('brand_kits')
          .insert({
            user_id: userId,
            ...brandKitData,
          });
        
        if (error) {
          console.error('Error creating brand kit:', error);
          throw new Error(`Failed to create brand kit: ${error.message}`);
        }
      }
    } catch (error) {
      console.error('Error saving brand kit:', error);
      throw error;
    }
  },
};
