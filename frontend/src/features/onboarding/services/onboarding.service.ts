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
  customer_pain_points?: string[]; // JSONB array - send as array, not stringified
  product_service_description?: string;
}

export const onboardingService = {
  /**
   * Get current user's ID from Supabase session
   * This returns auth.users.id which should match public.users.id after trigger
   */
  async getCurrentUserId(): Promise<string> {
    // First check session to ensure user is authenticated
    const { data: { session }, error: sessionError } = await supabase.auth.getSession();
    
    if (sessionError || !session) {
      // If we get a JWT sub claim error, the user doesn't exist in auth.users
      if (sessionError?.message?.includes('sub claim') || sessionError?.message?.includes('does not exist')) {
        console.error('JWT contains invalid user ID - clearing session');
        await supabase.auth.signOut();
        throw new Error('Your session is invalid. Please sign in again.');
      }
      throw new Error('User not authenticated - no active session');
    }
    
    // Get user to ensure we have the latest user data
    const { data: { user }, error: userError } = await supabase.auth.getUser();
    
    if (userError || !user) {
      // If we get a JWT sub claim error, the user doesn't exist in auth.users
      if (userError?.message?.includes('sub claim') || userError?.message?.includes('does not exist')) {
        console.error('JWT contains invalid user ID - clearing session');
        await supabase.auth.signOut();
        throw new Error('Your session is invalid. Please sign in again.');
      }
      throw new Error('User not authenticated - unable to get user');
    }
    
    // The user.id from auth.users should match public.users.id
    // The trigger handle_new_user() creates the public.users record with the same ID
    return user.id;
  },

  /**
   * Save or update brand kit data for the current user
   * Uses upsert to create or update the brand kit
   */
  async saveBrandKit(data: Partial<OnboardingData>): Promise<void> {
    try {
      const userId = await this.getCurrentUserId();
      
      // Ensure public.users record exists (should be created by trigger, but verify)
      // This helps catch any timing issues
      const { data: userRecord, error: userError } = await supabase
        .from('users')
        .select('id')
        .eq('id', userId)
        .single();
      
      if (userError && userError.code !== 'PGRST116') { // PGRST116 = not found
        console.warn('User record check failed:', userError);
        // Continue anyway - the trigger should have created it, or RLS might be blocking
      }
      
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
      
      // Handle customer pain points - JSONB column expects array, not stringified
      if (data.customerPainPoints) {
        if (Array.isArray(data.customerPainPoints)) {
          // Filter out empty strings and send as array for JSONB
          const filteredArray = data.customerPainPoints
            .map(p => typeof p === 'string' ? p.trim() : String(p).trim())
            .filter(p => p.length > 0);
          if (filteredArray.length > 0) {
            brandKitData.customer_pain_points = filteredArray;
          }
        } else if (typeof data.customerPainPoints === 'string') {
          // If it's a string, convert to array first
          const painPointsArray = data.customerPainPoints
            .split('\n')
            .map(p => p.trim())
            .filter(p => p.length > 0);
          if (painPointsArray.length > 0) {
            brandKitData.customer_pain_points = painPointsArray;
          }
        }
      }
      
      if (data.productService) {
        brandKitData.product_service_description = data.productService.trim();
      }
      
      // Check if brand kit already exists for this user
      // First, try to find any existing brand kit for this user
      const { data: existingKits, error: selectError } = await supabase
        .from('brand_kits')
        .select('id, brand_name')
        .eq('user_id', userId)
        .limit(1);
      
      if (selectError) {
        console.error('Error checking existing brand kits:', selectError);
        throw new Error(`Failed to check existing brand kits: ${selectError.message}`);
      }
      
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
          // Check if it's an RLS policy issue
          if (error.message?.includes('policy') || error.message?.includes('permission')) {
            throw new Error(`Permission denied: Make sure you are authenticated and your email is verified. ${error.message}`);
          }
          throw new Error(`Failed to create brand kit: ${error.message}`);
        }
      }
    } catch (error) {
      console.error('Error saving brand kit:', error);
      throw error;
    }
  },
};
