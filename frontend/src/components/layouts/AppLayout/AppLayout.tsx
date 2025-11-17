import React from 'react';
import styles from './AppLayout.module.css';

export interface AppLayoutProps {
  children: React.ReactNode;
}

/**
 * AppLayout Component
 * 
 * Layout wrapper for authenticated app pages
 * 
 * TODO: Implement app layout
 * - App navigation bar
 * - Sidebar (optional)
 * - User menu
 * - Breadcrumbs
 * - Main content area
 */
export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        {/* TODO: Add app navigation */}
        <div>Scale66 App Navigation</div>
      </header>
      <main className={styles.main}>{children}</main>
    </div>
  );
};

export default AppLayout;

