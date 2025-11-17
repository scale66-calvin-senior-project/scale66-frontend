import React from 'react';
import { Spinner } from '@/components/ui';
import styles from './LoadingSpinner.module.css';

export interface LoadingSpinnerProps {
  message?: string;
  fullScreen?: boolean;
}

/**
 * LoadingSpinner Component
 * 
 * TODO: Implement loading state display
 * - Optional message
 * - Full screen overlay option
 * - Centered positioning
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading...',
  fullScreen = false,
}) => {
  return (
    <div className={`${styles.container} ${fullScreen ? styles.fullScreen : ''}`}>
      <Spinner size="lg" />
      {message && <p className={styles.message}>{message}</p>}
    </div>
  );
};

export default LoadingSpinner;

