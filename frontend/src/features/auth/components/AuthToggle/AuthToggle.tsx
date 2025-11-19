import React from 'react';
import styles from './AuthToggle.module.css';

export interface AuthToggleProps {
  mode: 'login' | 'signup';
  onToggle: () => void;
}

/**
 * AuthToggle Component
 * TODO: Implement toggle between login/signup modes
 */
export const AuthToggle: React.FC<AuthToggleProps> = ({ mode, onToggle }) => {
  return (
    <div className={styles.container}>
      <p>TODO: Implement auth mode toggle</p>
    </div>
  );
};

export default AuthToggle;

