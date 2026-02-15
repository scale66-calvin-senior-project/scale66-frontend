/**
 * Brand Styles Data
 * Matches database enum values for brand_style
 */

export interface BrandStyleOption {
  value: string;
  label: string;
  description: string;
}

export const brandStyles: BrandStyleOption[] = [
  { 
    value: 'professional', 
    label: 'Professional', 
    description: 'Clean, corporate, trustworthy' 
  },
  { 
    value: 'casual', 
    label: 'Casual', 
    description: 'Friendly, approachable, relaxed' 
  },
  { 
    value: 'playful', 
    label: 'Playful', 
    description: 'Fun, energetic, creative' 
  },
  { 
    value: 'bold', 
    label: 'Bold', 
    description: 'Strong, confident, impactful' 
  },
  { 
    value: 'minimalist', 
    label: 'Minimalist', 
    description: 'Simple, clean, focused' 
  },
  { 
    value: 'luxury', 
    label: 'Luxury', 
    description: 'Premium, elegant, sophisticated' 
  },
  { 
    value: 'modern', 
    label: 'Modern', 
    description: 'Contemporary, innovative, fresh' 
  },
  { 
    value: 'vintage', 
    label: 'Vintage', 
    description: 'Classic, nostalgic, timeless' 
  },
];

export default brandStyles;
