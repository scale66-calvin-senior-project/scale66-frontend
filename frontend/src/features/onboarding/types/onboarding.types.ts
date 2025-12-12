/**
 * Onboarding Types
 */

export interface OnboardingData {
  brandName?: string;
  brandNiche?: string;
  brandStyle?: string;
  customerPainPoints?: string | string[]; // Can be string or array of strings
  productService?: string;
  socialMediaLinks?: {
    instagram?: string;
    tiktok?: string;
  };
  paywallSelection?: {
    plan: 'agency' | 'growth' | 'starter';
  };
}

export interface OnboardingStep {
  id: number;
  title: string;
  description?: string;
}
