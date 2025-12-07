'use client';

import React from 'react';
import Navbar from './Navbar';
import Footer from './Footer';
import { AuthModalProvider, useAuthModal } from '@/context/AuthModalContext';
import { AuthModal } from '@/features/auth';
import { useRouter } from 'next/navigation';
import styles from './LandingLayout.module.css';

export interface LandingLayoutProps {
  children: React.ReactNode;
}

const LandingLayoutContent: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isOpen, mode, openModal, closeModal } = useAuthModal();
  const router = useRouter();

  const handleAuthSuccess = () => {
    router.push('/onboarding');
  };

  return (
    <>
      <div className={styles.layout}>
        <Navbar />
        <main className={styles.main}>{children}</main>
        <Footer />
      </div>
      <AuthModal
        isOpen={isOpen}
        onClose={closeModal}
        onSuccess={handleAuthSuccess}
        initialMode={mode}
      />
    </>
  );
};

/**
 * LandingLayout Component
 * 
 * Layout wrapper for public marketing pages
 * Includes Navbar and Footer
 */
export const LandingLayout: React.FC<LandingLayoutProps> = ({ children }) => {
  return (
    <AuthModalProvider>
      <LandingLayoutContent>{children}</LandingLayoutContent>
    </AuthModalProvider>
  );
};

export default LandingLayout;

