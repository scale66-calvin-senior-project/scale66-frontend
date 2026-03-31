'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MainNavbar } from '@/features/mainpage';
import { useAuth } from '@/features/auth/hooks/useAuth';
import styles from './AppLayout.module.css';

export interface AppLayoutProps {
  children: React.ReactNode;
}

/**
 * AppLayout Component
 *
 * Shared layout for authenticated app pages (dashboard, brand-kit, settings, campaigns).
 * Blocks rendering until auth state is confirmed — prevents API calls going out
 * before the session token is available (fixes 403 race condition on hard refresh).
 */
export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const { isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading || !isAuthenticated) {
    return null;
  }

  return (
    <div className={styles.wrapper}>
      <MainNavbar />
      <main className={styles.main}>{children}</main>
    </div>
  );
};

export default AppLayout;
