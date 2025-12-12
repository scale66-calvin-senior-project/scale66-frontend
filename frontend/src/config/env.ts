/**
 * Environment Configuration
 * Validates and exports environment variables for the application
 */
export const env = {
  // Backend API
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  
  // Supabase (Auth only - all DB operations via backend)
  supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL || '',
  supabaseAnonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '',
  
  // Stripe
  stripePublishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '',
  // Stripe Payment Links (optional - if using Payment Links instead of checkout sessions)
  stripePaymentLinks: {
    starter: process.env.NEXT_PUBLIC_STRIPE_PAYMENT_LINK_STARTER || '',
    growth: process.env.NEXT_PUBLIC_STRIPE_PAYMENT_LINK_GROWTH || '',
    agency: process.env.NEXT_PUBLIC_STRIPE_PAYMENT_LINK_AGENCY || '',
  },
};
