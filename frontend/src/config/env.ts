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
};
