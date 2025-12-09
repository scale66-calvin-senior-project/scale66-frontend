'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/features/auth';
import LandingPage from '@/features/landing/landing-page/page';

/**
 * Landing Page
 * 
 * Public landing page
 * Redirects authenticated users to dashboard
 */
export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const [hasChecked, setHasChecked] = useState(false);

  useEffect(() => {
    // Wait for auth to load
    if (isLoading) {
      setHasChecked(false);
      return;
    }

    setHasChecked(true);

    // If user is authenticated, redirect to dashboard
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading only while checking auth
  if (isLoading || !hasChecked) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  // If authenticated, don't render (redirect will happen)
  if (isAuthenticated) {
    return null;
  }

  // Show landing page for unauthenticated users
  return <LandingPage />;
}

