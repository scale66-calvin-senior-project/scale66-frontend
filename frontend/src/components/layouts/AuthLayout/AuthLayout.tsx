import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import styles from './AuthLayout.module.css';

export interface AuthLayoutProps {
  children: React.ReactNode;
}

/**
 * AuthLayout Component
 * 
 * Layout wrapper for authentication pages (login/signup)
 * Includes minimal header with logo and centered auth form
 */
export const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <Link href="/">
          <Image src="/logo.png" alt="Scale66" width={32} height={32} />
          Scale66
        </Link>
      </header>
      <main className={styles.main}>
        <div className={styles.container}>{children}</div>
      </main>
    </div>
  );
};

export default AuthLayout;

