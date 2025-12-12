'use client';

import React, { useState } from 'react';
import { LoginForm } from '../LoginForm';
import { SignupForm } from '../SignupForm';
import styles from './AuthModal.module.css';

export interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  initialMode?: 'login' | 'signup';
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  initialMode = 'signup',
}) => {
  const [mode, setMode] = useState<'login' | 'signup'>(initialMode);

  if (!isOpen) return null;

  const handleSuccess = () => {
    onSuccess?.();
    onClose();
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose} aria-label="Close">
          ×
        </button>

        <div className={styles.header}>
          <h2 className={styles.title}>
            {mode === 'login' ? 'Welcome Back' : 'Get Started'}
          </h2>
          <p className={styles.subtitle}>
            {mode === 'login'
              ? 'Sign in to continue to Scale66'
              : 'Create your account to start creating amazing content'}
          </p>
        </div>

        <div className={styles.content}>
          {mode === 'login' ? (
            <LoginForm onSuccess={handleSuccess} />
          ) : (
            <SignupForm onSuccess={handleSuccess} />
          )}
        </div>

        <div className={styles.footer}>
          <p className={styles.footerText}>
            {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <button
              className={styles.toggleButton}
              onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}
            >
              {mode === 'login' ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

