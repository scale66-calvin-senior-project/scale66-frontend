/**
 * Environment Configuration
 * Validates and exports environment variables for the application
 */
export const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  firebaseApiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || '',
  // Add more env vars as needed
};
