import React from 'react';
import styles from './SocialAuthButtons.module.css';

export interface SocialAuthButtonsProps {
  onSuccess?: () => void;
}

/**
 * SocialAuthButtons Component
 * TODO: Implement social auth buttons (Google, Apple)
 */
export const SocialAuthButtons: React.FC<SocialAuthButtonsProps> = ({ onSuccess }) => {
  return (
    <div className={styles.container}>
      <p>TODO: Implement Google & Apple auth buttons</p>
    </div>
  );
};

export default SocialAuthButtons;

