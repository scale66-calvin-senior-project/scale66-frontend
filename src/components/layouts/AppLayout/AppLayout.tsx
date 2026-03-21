'use client';

import React from 'react';
import { MainNavbar } from '@/features/mainpage';
import styles from './AppLayout.module.css';

export interface AppLayoutProps {
  children: React.ReactNode;
}

/**
 * AppLayout Component
 *
 * Shared layout for authenticated app pages (dashboard, brand-kit, settings, campaigns).
 * Provides consistent navbar and background so routes look and navigate the same.
 */
export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className={styles.wrapper}>
      <MainNavbar />
      <main className={styles.main}>{children}</main>
    </div>
  );
};

export default AppLayout;
