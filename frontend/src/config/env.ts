/**
 * Environment Configuration
 * TODO: Validate and export environment variables
 */
export const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || '',
  firebaseApiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || '',
  // TODO: Add more env vars
};
