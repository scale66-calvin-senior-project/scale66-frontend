import React from 'react';
import styles from './AuthLayout.module.css';

export interface AuthLayoutProps {
  children: React.ReactNode;
}

/**
 * AuthLayout Component
 * 
 * Layout wrapper for authentication pages (login/signup)
 * 
 * TODO: Implement auth layout
 * - Minimal header with logo
 * - Centered auth form container
 * - Background styling
 * - Footer (optional)
 */
export const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        {/* TODO: Add logo */}
        <div>Scale66</div>
      </header>
      <main className={styles.main}>
        <div className={styles.container}>{children}</div>
      </main>
    </div>
  );
};

export default AuthLayout;

