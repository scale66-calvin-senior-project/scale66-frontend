'use client';

import { useEffect, useState } from 'react';
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
  const { user, isAuthenticated } = useAuth();
  const [hasCheckedSession, setHasCheckedSession] = useState(false);

  useEffect(() => {
    // Quick session check - don't wait for full auth context
    const checkSession = async () => {
      if (hasCheckedSession) return;
      
      try {
        const { supabase } = await import('@/lib/supabase');
        const { data: { session } } = await supabase.auth.getSession();
        
        setHasCheckedSession(true);
        
        // Only redirect if we're absolutely sure there's no session
        if (!session?.user && !isAuthenticated && !user) {
          console.log('No session found, redirecting to landing page');
          router.replace('/');
        }
      } catch (error) {
        console.error('Session check error:', error);
        setHasCheckedSession(true);
      }
    };

    checkSession();
  }, [isAuthenticated, user, router, hasCheckedSession]);

  // Always show dashboard optimistically - no loading screen ever
  // If user isn't authenticated, the redirect will happen in the background
  return <MainPage />;
}
