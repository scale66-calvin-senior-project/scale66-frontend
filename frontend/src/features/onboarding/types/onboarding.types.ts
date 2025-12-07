/**
 * Onboarding Types
 */

export interface OnboardingData {
  brandName?: string;
  brandNiche?: string;
  brandStyle?: string;
  customerPainPoints?: string;
  productService?: string;
  socialMediaLinks?: {
    instagram?: string;
    tiktok?: string;
  };
}

export interface OnboardingStep {
  id: number;
  title: string;
  description?: string;
}
