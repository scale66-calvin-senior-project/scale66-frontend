/**
 * Brand Kit Types
 * Based on database schema for BrandKits and SocialMediaAccounts tables
 */

/**
 * Brand style options matching database enum
 */
export type BrandStyle =
  | 'professional'
  | 'casual'
  | 'playful'
  | 'bold'
  | 'minimalist'
  | 'luxury'
  | 'modern'
  | 'vintage';

/**
 * Supported social media platforms
 */
export type SocialPlatform = 'instagram' | 'tiktok' | 'facebook' | 'linkedin';

/**
 * Social media account connection status
 */
export interface SocialMediaAccount {
  id: string;
  userId: string;
  platform: SocialPlatform;
  platformUserId: string;
  isActive: boolean;
  username?: string;
  profileUrl?: string;
}

/**
 * Brand Kit data structure matching database schema
 */
export interface BrandKit {
  id: string;
  userId: string;
  brandName?: string;
  brandNiche?: string;
  brandStyle?: BrandStyle;
  customerPainPoints?: string;
  productServiceDescription: string;
  createdAt?: string;
  updatedAt?: string;
}

/**
 * Form data for creating/updating brand kit
 */
export interface BrandKitFormData {
  brandName?: string;
  brandNiche?: string;
  brandStyle?: BrandStyle;
  customerPainPoints?: string;
  productServiceDescription: string;
}

/**
 * Brand Kit state for hook
 */
export interface BrandKitState {
  brandKit: BrandKit | null;
  socialAccounts: SocialMediaAccount[];
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
}

/**
 * Brand style option for dropdown
 */
export interface BrandStyleOption {
  value: BrandStyle;
  label: string;
  description?: string;
}

/**
 * Available brand style options
 */
export const BRAND_STYLE_OPTIONS: BrandStyleOption[] = [
  { value: 'professional', label: 'Professional', description: 'Clean, corporate, trustworthy' },
  { value: 'casual', label: 'Casual', description: 'Friendly, approachable, relaxed' },
  { value: 'playful', label: 'Playful', description: 'Fun, energetic, creative' },
  { value: 'bold', label: 'Bold', description: 'Strong, confident, impactful' },
  { value: 'minimalist', label: 'Minimalist', description: 'Simple, clean, focused' },
  { value: 'luxury', label: 'Luxury', description: 'Premium, elegant, sophisticated' },
  { value: 'modern', label: 'Modern', description: 'Contemporary, innovative, fresh' },
  { value: 'vintage', label: 'Vintage', description: 'Classic, nostalgic, timeless' },
];
