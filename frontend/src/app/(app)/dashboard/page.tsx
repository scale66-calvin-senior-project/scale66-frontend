'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/features/auth';
import { MainPage } from "@/features/mainpage";

/**
 * Dashboard Page
 * 
 * Main entry point for authenticated users
 * Displays "Let's Create" prompt interface
 * 
 * Access Rules:
 * - Must be logged in (middleware handles this)
 * - If not subscribed, shows dashboard but may show upgrade prompt
 */
export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    // Wait for auth to load
    if (isLoading) return;

    // Only redirect if we're absolutely sure there's no session
    // Double-check with Supabase directly before redirecting
    if (!isAuthenticated) {
      import('@/lib/supabase').then(({ supabase }) => {
        supabase.auth.getSession().then(({ data: { session } }) => {
          if (!session) {
            console.log('No session found, redirecting to landing page');
            router.push('/');
          } else {
            console.log('Session found but auth context not loaded yet, waiting...');
            // Session exists but auth context hasn't loaded it yet
            // Give it a moment to sync
          }
        });
      });
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading while checking auth
  if (isLoading) {
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

  // Don't render if not authenticated (redirect will happen)
  if (!isAuthenticated) {
    return null;
  }

  // Show dashboard for all authenticated users
  // Subscription check can be done at feature level if needed
  return <MainPage />;
}
