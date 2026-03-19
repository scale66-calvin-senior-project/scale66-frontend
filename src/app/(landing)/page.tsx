'use client';

import LandingPage from '@/features/landing/landing-page/page';

/**
 * Landing Page
 * 
 * Public landing page - loads immediately without auth checks
 * Auth checks happen when user clicks login/signup buttons
 */
export default function Home() {
  // Show landing page immediately - no auth checks
  return <LandingPage />;
}

