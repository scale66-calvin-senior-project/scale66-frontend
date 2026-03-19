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
  customer_pain_points?: string; // TEXT column - stored as string (newline-separated)
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
    console.log('🚀 saveBrandKit called with data:', data);
    try {
      const userId = await this.getCurrentUserId();
      console.log('✅ Got userId:', userId);
      
      // Quick check if user record exists (with minimal retries)
      let userExists = false;
      for (let i = 0; i < 3; i++) {
        const { data: user, error: userError } = await supabase
          .from('users')
          .select('id')
          .eq('id', userId)
          .maybeSingle();
        
        if (user && !userError) {
          userExists = true;
          console.log('✅ User record found');
          break;
        }
        
        if (userError?.code === 'PGRST116') {
          // Not found - wait briefly and retry (trigger might still be processing)
          if (i < 2) {
            await new Promise(resolve => setTimeout(resolve, 300));
            continue;
          }
        } else {
          // Other error - break and try to continue
          break;
        }
      }
      
      // If user record doesn't exist, try to create it (trigger might not have run yet)
      if (!userExists) {
        console.log('🔄 User record not found, attempting to create...');
        const { data: userData } = await supabase.auth.getUser();
        const { error: createError } = await supabase
          .from('users')
          .insert({
            id: userId,
            email: userData.user?.email || '',
          });
        
        if (createError && createError.code !== '23505') {
          // 23505 = duplicate key (record was created between checks)
          console.warn('⚠️ Could not create user record:', createError);
          // Continue anyway - the brand kit insert will fail if user doesn't exist
        } else {
          console.log('✅ User record created or already exists');
        }
      }
      
      // Prepare the data for Supabase
      const brandKitData: Partial<BrandKitData> = {};
      
      if (data.brandName) {
        const trimmedName = data.brandName.trim();
        if (trimmedName) {
          brandKitData.brand_name = trimmedName;
          console.log('📝 Brand name to save:', brandKitData.brand_name);
        } else {
          console.warn('⚠️ Brand name is empty after trimming');
        }
      } else {
        console.warn('⚠️ No brandName in data:', data);
      }
      
      if (data.brandNiche) {
        brandKitData.brand_niche = data.brandNiche;
      }
      
      if (data.brandStyle) {
        brandKitData.brand_style = data.brandStyle;
      }
      
      // Handle customer pain points - TEXT column, store as string
      if (data.customerPainPoints) {
        if (Array.isArray(data.customerPainPoints)) {
          // Join array into string
          const filteredArray = data.customerPainPoints
            .map(p => typeof p === 'string' ? p.trim() : String(p).trim())
            .filter(p => p.length > 0);
          if (filteredArray.length > 0) {
            brandKitData.customer_pain_points = filteredArray.join('\n');
          }
        } else if (typeof data.customerPainPoints === 'string') {
          brandKitData.customer_pain_points = data.customerPainPoints.trim();
        }
      }
      
      if (data.productService) {
        brandKitData.product_service_description = data.productService.trim();
      }
      
      // Validate required data
      if (!brandKitData.brand_name) {
        throw new Error('Brand name is required to save brand kit');
      }
      
      // Check if brand kit already exists for this user
      // Since users typically have one brand kit, we'll update if exists, insert if not
      console.log('💾 Saving brand kit with data:', { user_id: userId, ...brandKitData });
      
      // First, check if a brand kit exists for this user
      const { data: existingKit, error: checkError } = await supabase
        .from('brand_kits')
        .select('id')
        .eq('user_id', userId)
        .maybeSingle();
      
      if (checkError && checkError.code !== 'PGRST116') {
        // PGRST116 = not found, which is fine
        console.warn('⚠️ Error checking for existing brand kit:', checkError);
      }
      
      let savedData = null;
      let saveError = null;
      
      if (existingKit) {
        // Update existing brand kit
        console.log('🔄 Updating existing brand kit:', existingKit.id);
        const { data: updatedData, error: updateError } = await supabase
          .from('brand_kits')
          .update(brandKitData)
          .eq('user_id', userId)
          .select()
          .single();
        
        savedData = updatedData;
        saveError = updateError;
      } else {
        // Insert new brand kit
        console.log('🆕 Creating new brand kit');
        const { data: insertedData, error: insertError } = await supabase
          .from('brand_kits')
          .insert({
            user_id: userId,
            ...brandKitData,
          })
          .select()
          .single();
        
        savedData = insertedData;
        saveError = insertError;
      }
      
      if (saveError) {
        console.error('❌ Error saving brand kit:', saveError);
        console.error('Error details:', {
          code: saveError.code,
          message: saveError.message,
          details: saveError.details,
          hint: saveError.hint,
          userId,
          brandKitData,
        });
        
        // Check if it's a foreign key constraint issue (user doesn't exist)
        if (saveError.code === '23503' || saveError.message?.includes('foreign key') || saveError.message?.includes('user_id')) {
          throw new Error(`User record not found. Please wait a moment and try again. ${saveError.message}`);
        }
        
        // Check if it's an RLS policy issue
        if (saveError.message?.includes('policy') || saveError.message?.includes('permission')) {
          throw new Error(`Permission denied: Make sure you are authenticated and your email is verified. ${saveError.message}`);
        }
        
        throw new Error(`Failed to save brand kit: ${saveError.message}`);
      }
      
      if (!savedData) {
        throw new Error('Save completed but no data returned from database');
      }
      
      console.log('✅ Brand kit saved successfully:', savedData);
      
      // Verify the save by reading it back (quick consistency check)
      // Wait a tiny bit for database consistency
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const { data: verifyData, error: verifyError } = await supabase
        .from('brand_kits')
        .select('id, brand_name, updated_at')
        .eq('user_id', userId)
        .single();
      
      if (verifyError || !verifyData) {
        console.warn('⚠️ Verification read failed, but save appeared successful:', verifyError);
        // Don't throw - the save might have succeeded, just the read failed
      } else {
        console.log('✅ Verified save - data confirmed in database:', verifyData);
        // Double-check the brand_name matches what we tried to save
        if (verifyData.brand_name !== brandKitData.brand_name) {
          console.warn('⚠️ Brand name mismatch - saved:', brandKitData.brand_name, 'found:', verifyData.brand_name);
        }
      }
    } catch (error) {
      console.error('❌ Error saving brand kit:', error);
      // Re-throw to ensure the caller knows it failed
      throw error;
    }
  },
};
