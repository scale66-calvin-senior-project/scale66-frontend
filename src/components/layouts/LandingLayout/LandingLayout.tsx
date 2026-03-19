import React from 'react';
import Navbar from './Navbar';
import Footer from './Footer';
import styles from './LandingLayout.module.css';

export interface LandingLayoutProps {
  children: React.ReactNode;
}

/**
 * LandingLayout Component
 * 
 * Layout wrapper for public marketing pages
 * Includes Navbar and Footer
 */
export const LandingLayout: React.FC<LandingLayoutProps> = ({ children }) => {
  return (
    <div className={styles.layout}>
      <Navbar />
      <main className={styles.main}>{children}</main>
      <Footer />
    </div>
  );
};

export default LandingLayout;

