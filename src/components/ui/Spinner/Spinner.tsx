import React from 'react';
import styles from './Spinner.module.css';

export interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * Spinner Component
 * 
 * TODO: Implement loading spinner
 * - Different sizes
 * - Smooth animation
 * - Color variants
 */
export const Spinner: React.FC<SpinnerProps> = ({ size = 'md', className }) => {
  return (
    <div className={`${styles.spinner} ${styles[size]} ${className || ''}`}>
      <div className={styles.circle}></div>
    </div>
  );
};

export default Spinner;

